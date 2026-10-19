"""Painter-native layered material production, baking, saving and UE export.

Executed inside Painter 12 through c13_painter_bridge. Never closes an
unrelated or unsaved user document. Restarting resumes completed assets.
"""
from pathlib import Path
import json, traceback
from PySide6.QtCore import QTimer
import substance_painter as sp
import substance_painter.project, substance_painter.resource, substance_painter.export
import substance_painter.textureset, substance_painter.baking, substance_painter.layerstack
import substance_painter.source, substance_painter.event, substance_painter.ui
from substance_painter.colormanagement import Color

ROOT=Path('/Users/vini_deiro/bankers')
PROJECTS=ROOT/'painter'; PROJECTS.mkdir(exist_ok=True)
OUT=ROOT/'assets/painter'; OUT.mkdir(parents=True,exist_ok=True)
REPORT=ROOT/'logs/painter_production.json'
RESOURCES=json.loads((ROOT/'logs/painter_resources.json').read_text())['resources']
ASSETS=['SM_Hero_Locker','SM_Hero_Bed','SM_Hero_BlastDoor']
REVISION=2
SMART={'Paint':'Steel Painted Scraped Green','Steel':'Steel Dark Aged',
       'Fabric':'Fabric Canvas Creased','Linen':'Fabric Linen Worn',
       'Rubber':'Rubber Tire Dirty','Safety':'Steel Painted Worn'}
COLORS={'Paint':(.28,.34,.24),'Fabric':(.27,.31,.21),'Linen':(.70,.66,.53),'Safety':(.73,.36,.07)}

def error():
    (ROOT/'logs/painter_error.txt').write_text(traceback.format_exc())
    print(traceback.format_exc())

def smart_id(name):
    return next(sp.resource.ResourceID.from_url(r['id']) for r in RESOURCES
                if r['id'].startswith('resource://starter_assets/'+name+'?') and r['id'].endswith('.spsm'))

def descendants(node):
    yield node
    if isinstance(node,sp.layerstack.GroupLayerNode):
        for child in node.sub_layers(): yield from descendants(child)

class Production:
    def __init__(self):
        self.index=0;self.results=[];self.current=None
    def start(self):
        if sp.project.is_open():
            path=sp.project.file_path()
            if path and not str(path).startswith(str(PROJECTS)):
                raise RuntimeError('An unrelated project is open; preserving it.')
            if sp.project.needs_saving():
                if path:sp.project.save()
                elif Path(sp.project.last_imported_mesh_path()).name!='SM_Hero_Locker.fbx':
                    raise RuntimeError('Preserving unsaved user project')
                else:
                    from datetime import datetime
                    sp.project.save_as(str(PROJECTS/('C13_Recovery_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.spp')))
            sp.project.close()
        self.next()
    def next(self):
        try:
            if self.index>=len(ASSETS):
                REPORT.write_text(json.dumps({'complete':True,'assets':self.results},indent=2))
                print('C13_PAINTER_PRODUCTION_OK')
                self.verified=[];self.verify(0);return
            self.current=ASSETS[self.index]
            target=PROJECTS/(self.current+'.spp')
            if target.exists() and (OUT/self.current/'export_manifest.json').exists():
                prior=json.loads((OUT/self.current/'export_manifest.json').read_text())
                if prior.get('revision')==REVISION:
                    self.results.append(prior)
                    self.index+=1;self.next();return
            settings=sp.project.Settings();settings.default_texture_resolution=1024
            settings.normal_map_format=sp.project.NormalMapFormat.DirectX
            sp.project.create(str(ROOT/'exports/hero_kit'/(self.current+'.fbx')),settings=settings)
            sp.project.execute_when_not_busy(self.prepare)
        except Exception:error()
    def verify(self,index):
        try:
            if index==len(ASSETS):
                (ROOT/'logs/painter_verify.json').write_text(json.dumps({'complete':True,'projects':self.verified},indent=2))
                print('C13_PAINTER_REOPEN_OK');return
            if sp.project.is_open():
                if sp.project.needs_saving():sp.project.save()
                sp.project.close()
            asset=ASSETS[index]
            sp.project.open(str(PROJECTS/(asset+'.spp')))
            def loaded():
                try:
                    sets=sp.textureset.all_texture_sets()
                    assert len(sets)==(3 if asset.endswith('BlastDoor') else 4)
                    data=[]
                    for ts in sets:
                        maps={str(m):bool(ts.get_mesh_map_resource(m)) for m in (sp.textureset.MeshMapUsage.Normal,sp.textureset.MeshMapUsage.AO,sp.textureset.MeshMapUsage.Curvature,sp.textureset.MeshMapUsage.Position,sp.textureset.MeshMapUsage.WorldSpaceNormal)}
                        assert all(maps.values()),(asset,ts.name(),maps)
                        layers=sp.layerstack.get_root_layer_nodes(ts.get_stack())
                        assert any(n.get_name().startswith('C13 /') for n in layers)
                        data.append({'name':ts.name(),'maps':maps,'root_layers':len(layers)})
                    self.verified.append({'asset':asset,'sets':data})
                    QTimer.singleShot(0,lambda:self.verify(index+1))
                except Exception:error()
            sp.project.execute_when_not_busy(loaded)
        except Exception:error()
    def prepare(self):
        try:
            self.sets=sp.textureset.all_texture_sets()
            for ts in self.sets:
                bp=sp.baking.BakingParameters.from_texture_set(ts)
                common=bp.common()
                sp.baking.BakingParameters.set({common['OutputSize']:(10,10),common['LowAsHigh']:True})
                bp.set_enabled_bakers([sp.textureset.MeshMapUsage.Normal,sp.textureset.MeshMapUsage.WorldSpaceNormal,
                    sp.textureset.MeshMapUsage.AO,sp.textureset.MeshMapUsage.Curvature,sp.textureset.MeshMapUsage.Position])
                bp.set_textureset_enabled(True)
            sp.event.DISPATCHER.connect_strong(sp.event.BakingProcessEnded,self.baked)
            self.stop=sp.baking.bake_selected_textures_async()
            print('C13_BAKING',self.current)
        except Exception:error()
    def baked(self,event):
        sp.event.DISPATCHER.disconnect(sp.event.BakingProcessEnded,self.baked)
        try:
            if event.status!=sp.baking.BakingStatus.Success:raise RuntimeError('Bake failed: '+str(event.status))
            QTimer.singleShot(0,self.paint)
        except Exception:error()
    def paint(self):
        try:
            sp.ui.switch_to_mode(sp.ui.UIMode.Edition)
            self.layer_report=[]
            for ts in self.sets:
                key=ts.name().removeprefix('M_Hero_')
                stack=ts.get_stack()
                for old in sp.layerstack.get_root_layer_nodes(stack):sp.layerstack.delete_node(old)
                group=sp.layerstack.insert_smart_material(sp.layerstack.InsertPosition.from_textureset_stack(stack),smart_id(SMART[key]))
                group.set_name('C13 / '+key+' / '+SMART[key])
                tree=[]
                for node in descendants(group):
                    tree.append({'name':node.get_name(),'type':type(node).__name__})
                    if isinstance(node,sp.layerstack.FillLayerNode):
                        strength={'Tears':0.0,'Worn Edges':.18,'Dirt':.38,'Edges Damages':.40,'Scratches':.35}.get(node.get_name())
                        if strength is not None:
                            if strength==0:node.set_visible(False)
                            else:
                                for channel in node.active_channels:node.set_opacity(strength,channel)
                    # Adjust only uniform base-paint/fabric layers; retain their wear masks.
                    if key in COLORS and isinstance(node,sp.layerstack.FillLayerNode):
                        if node.source_mode==sp.source.SourceMode.Split and sp.textureset.ChannelType.BaseColor in node.active_channels:
                            src=node.get_source(sp.textureset.ChannelType.BaseColor)
                            if isinstance(src,sp.source.SourceUniformColor) and any(t in node.get_name().lower() for t in ('base','paint','fabric','color')):
                                src.set_color(Color(*COLORS[key]))
                self.layer_report.append({'set':ts.name(),'smart_material':SMART[key],'layers':tree})
            sp.project.execute_when_not_busy(self.save_export)
        except Exception:error()
    def save_export(self):
        try:
            sp.project.save_as(str(PROJECTS/(self.current+'.spp')))
            export_dir=OUT/self.current;export_dir.mkdir(exist_ok=True)
            def rgb_channels(kind,name):
                return [{'destChannel':c,'srcChannel':c,'srcMapType':kind,'srcMapName':name} for c in 'RGB']
            maps=[{'fileName':'$textureSet_BaseColor','channels':rgb_channels('documentMap','baseColor')},
                  {'fileName':'$textureSet_Normal','channels':rgb_channels('virtualMap','Normal_DirectX')},
                  {'fileName':'$textureSet_ORM','channels':[
                    {'destChannel':'R','srcChannel':'L','srcMapType':'virtualMap','srcMapName':'AO_Mixed'},
                    {'destChannel':'G','srcChannel':'L','srcMapType':'documentMap','srcMapName':'roughness'},
                    {'destChannel':'B','srcChannel':'L','srcMapType':'documentMap','srcMapName':'metallic'}]}]
            config={'exportShaderParams':False,'exportPath':str(export_dir),'defaultExportPreset':'C13_Unreal',
                'exportPresets':[{'name':'C13_Unreal','maps':maps}],
                'exportList':[{'rootPath':ts.name()} for ts in self.sets],
                'exportParameters':[{'parameters':{'fileFormat':'png','bitDepth':'8','sizeLog2':10,'paddingAlgorithm':'infinite','dithering':False}}]}
            result=sp.export.export_project_textures(config)
            if result.status!=sp.export.ExportStatus.Success:raise RuntimeError(result.message)
            entry={'asset':self.current,'revision':REVISION,'project':str(PROJECTS/(self.current+'.spp')),
                'bake':'Success','resolution':1024,'sets':self.layer_report,
                'textures':[p for paths in result.textures.values() for p in paths]}
            (export_dir/'export_manifest.json').write_text(json.dumps(entry,indent=2))
            self.results.append(entry)
            REPORT.write_text(json.dumps({'complete':False,'assets':self.results},indent=2))
            print('C13_ASSET_DONE',self.current)
            self.index+=1
            if self.index<len(ASSETS):
                sp.project.close();QTimer.singleShot(0,self.next)
            else:self.next()
        except Exception:error()

controller=Production()
try:
    (ROOT/'logs/painter_error.txt').write_text('')
    controller.start()
except Exception:error()
