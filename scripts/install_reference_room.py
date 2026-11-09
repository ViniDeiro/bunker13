"""Scoped Unreal integration. Never regenerate the global level or seeded inventory."""
from pathlib import Path
import json,math,shutil
import unreal as u
R=Path(__file__).resolve().parents[1];D='/Game/Bunker/ReferenceRoom';u.EditorAssetLibrary.make_directory(D)
backup=R/'output/reference_room_backup';backup.mkdir(parents=True,exist_ok=True)
level=R/'unreal/Condominio13/Content/Bunker/Lvl_Bunker.umap'
if not (backup/'Lvl_Bunker_before.umap').exists():shutil.copy2(level,backup/'Lvl_Bunker_before.umap')
u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
A=u.AssetToolsHelpers.get_asset_tools();E=u.MaterialEditingLibrary

def node(m,c):return E.create_material_expression(m,c,0,0)
def custom(m,code,ins):
 n=node(m,u.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
 arr=[]
 for k,v in ins:q=u.CustomInput();q.set_editor_property('input_name',k);arr.append(q)
 n.set_editor_property('inputs',arr)
 for k,v in ins:E.connect_material_expressions(v,'',n,k)
 return n
mats={}
for name in ('Concrete','Paint','Steel','Rubber','Fabric','Wood','Ivory','Paper','Amber','Light'):
 ts={}
 for kind in ('BaseColor','Normal','ORM'):
  t=u.AssetImportTask();t.filename=str(R/'assets/reference_room'/f'T_Ref_{name}_{kind}.png');t.destination_path=D+'/Textures';t.automated=True;t.replace_existing=True;t.save=True;A.import_asset_tasks([t]);tex=u.load_asset(D+'/Textures/'+f'T_Ref_{name}_{kind}');tex.set_editor_property('srgb',kind=='BaseColor')
  if kind=='Normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
  if kind=='ORM':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
  u.EditorAssetLibrary.save_loaded_asset(tex);ts[kind]=tex
 m=u.load_asset(D+'/Materials/M_Ref_'+name) or A.create_asset('M_Ref_'+name,D+'/Materials',u.Material,u.MaterialFactoryNew());E.delete_all_material_expressions(m)
 pos=node(m,u.MaterialExpressionWorldPosition);normal=node(m,u.MaterialExpressionVertexNormalWS)
 sample='''float3 w=pow(abs(N),4);w/=max(w.x+w.y+w.z,.001);float3 p=P/100;
 return Texture2DSample(T,TSampler,p.yz).xyz*w.x+Texture2DSample(T,TSampler,p.xz).xyz*w.y+Texture2DSample(T,TSampler,p.xy).xyz*w.z;'''
 for kind,prop in [('BaseColor',u.MaterialProperty.MP_BASE_COLOR),('ORM',None)]:
  tex=node(m,u.MaterialExpressionTextureObject);tex.set_editor_property('texture',ts[kind]);result=custom(m,sample,[('T',tex),('P',pos),('N',normal)])
  if prop:
   macro=custom(m,'float v=1+.055*sin(P.x*.004+P.y*.0017)*sin(P.z*.007+P.y*.003);return C*v;',[('P',pos),('C',result)]);E.connect_material_property(macro,'',prop)
  else:
   for chan,pr in [('r',u.MaterialProperty.MP_AMBIENT_OCCLUSION),('g',u.MaterialProperty.MP_ROUGHNESS),('b',u.MaterialProperty.MP_METALLIC)]:
    mask=node(m,u.MaterialExpressionComponentMask)
    for c in 'rgba':mask.set_editor_property(c,c==chan)
    E.connect_material_expressions(result,'',mask,'');E.connect_material_property(mask,'',pr)
 tex=node(m,u.MaterialExpressionTextureObject);tex.set_editor_property('texture',ts['Normal'])
 code='''float3 w=pow(abs(N),4);w/=max(w.x+w.y+w.z,.001);float3 p=P/100;
 float3 a=Texture2DSample(T,TSampler,p.yz).xyz,b=Texture2DSample(T,TSampler,p.xz).xyz,c=Texture2DSample(T,TSampler,p.xy).xyz;
 a.xy=a.xy*2-1;b.xy=b.xy*2-1;c.xy=c.xy*2-1;
 a.z=sqrt(saturate(1-dot(a.xy,a.xy)));b.z=sqrt(saturate(1-dot(b.xy,b.xy)));c.z=sqrt(saturate(1-dot(c.xy,c.xy)));
 return normalize(lerp(N,normalize(float3(a.z*sign(N.x),a.x,a.y)*w.x+float3(b.x,b.z*sign(N.y),b.y)*w.y+float3(c.x,c.y,c.z*sign(N.z))*w.z),.15));'''
 nr=custom(m,code,[('T',tex),('P',pos),('N',normal)]);m.set_editor_property('tangent_space_normal',False);E.connect_material_property(nr,'',u.MaterialProperty.MP_NORMAL)
 if name=='Light':
  em=node(m,u.MaterialExpressionConstant3Vector);em.set_editor_property('constant',u.LinearColor(3,1.8,.65,1));E.connect_material_property(em,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 E.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m);mats[name]=m
meshes={};manifest=json.loads((R/'exports/reference_room/manifest.json').read_text())
for name in manifest:
 t=u.AssetImportTask();t.filename=str(R/'exports/reference_room'/(name+'.fbx'));t.destination_path=D+'/Meshes';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 o=u.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=False;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.generate_lightmap_u_vs=False;o.static_mesh_import_data.auto_generate_collision=False;t.options=o;A.import_asset_tasks([t])
 mesh=u.load_asset(D+'/Meshes/'+name);slots=list(mesh.get_editor_property('static_materials'))
 for s in slots:s.set_editor_property('material_interface',mats[str(s.material_slot_name).removeprefix('M_Ref_')])
 mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);u.EditorAssetLibrary.save_loaded_asset(mesh);meshes[name]=mesh
# Never delete or rename legacy native interactables. Existing cabinet extension is reused.
actors=u.EditorLevelLibrary.get_all_level_actors();native_before=[{'name':a.get_name(),'class':a.get_class().get_name(),'position':list(a.get_actor_location().to_tuple())} for a in actors if a.get_class().get_name().startswith('Bunker') and a.get_class().get_name()!='BunkerReferenceCabinet']
cab=next((a for a in actors if a.get_class().get_name()=='BunkerReferenceCabinet'),None)
for a in actors:
 label=a.get_actor_label()
 if (label.startswith('REF_') and a!=cab) or label.startswith('Social_'):
  u.EditorLevelLibrary.destroy_actor(a)
 # Old common-room light leakage is confined by channel2 on new meshes.
 # Turn off only the old lamps whose origins are in this room.
 elif isinstance(a,u.PointLight):
  p=a.get_actor_location()
  if 700<p.x<1600 and -730<p.y<-30:a.point_light_component.set_editor_property('intensity',0)

def setchannels(comp):comp.set_editor_property('lighting_channels',u.LightingChannels(False,False,True))
def spawn(name,key,p,yaw=0,scale=None,collision=True):
 if key in ('SM_Ref_Sofa','SM_Ref_Table','SM_Ref_Chair','SM_Ref_CabinetBody','SM_Ref_TV') and p[2]==0:p=(p[0],p[1],2.6)
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*p),u.Rotator(yaw=yaw));a.set_actor_label('REF_'+name);c=a.static_mesh_component;c.set_static_mesh(meshes[key]);setchannels(c)
 if scale:a.set_actor_scale3d(u.Vector(*scale))
 if not collision:c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 return a
spawn('Sofa','SM_Ref_Sofa',(795,-420,0),-90)
spawn('Table','SM_Ref_Table',(1140,-370,0))
for x in (1075,1205):
 for y,yaw in ((-305,180),(-435,0)):spawn(f'Chair_{x}_{y}','SM_Ref_Chair',(x,y,0),yaw)
# Panel segments leave both actual entry openings untouched.
def panels(name,start,end,axis,fixed,yaw):
 count=math.ceil((end-start)/150);width=(end-start)/count
 for i in range(count):
  along=start+(i+.5)*width;p=(along,fixed,0) if axis=='x' else (fixed,along,0)
  spawn(f'Panel_{name}_{i}','SM_Ref_WallPanel',p,yaw,((width-1)/148,1,1))
panels('North',710,1590,'x',-40,180)
panels('East',-720,-40,'y',1590,90)
panels('WestA',-120,-40,'y',710,-90);panels('WestB',-720,-240,'y',710,-90)
panels('SouthA',710,1050,'x',-720,0);panels('SouthB',1250,1590,'x',-720,0)
# Full local lining, no change to the structural shell or floor elevation.
spawn('Floor','SM_Ref_FloorTile',(1150,-380,2.6),0,(8.8,6.8,1))
# Ceiling geometry uses the floor slab scaled, so both visible underside and shadow have real thickness.
a=spawn('Ceiling','SM_Ref_FloorTile',(1150,-380,286),0,(8.8,6.8,2));a.static_mesh_component.set_material(0,mats['Concrete'])
for i,(x,y,temp,power) in enumerate(((1000,-330,3000,1000),(1330,-530,3300,750),(1400,-150,3700,600))):
 spawn(f'CeilingLamp{i}','SM_Ref_Lamp',(x,y,280))
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.PointLight,u.Vector(x,y,268));a.set_actor_label(f'REF_Light{i}');c=a.point_light_component;c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_editor_property('intensity',power);c.set_editor_property('attenuation_radius',630);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',temp);c.set_editor_property('cast_shadows',i==0);c.set_editor_property('source_radius',12);setchannels(c)
for x in (850,1050,1250,1450):spawn(f'Duct{x}','SM_Ref_Duct',(x,-75,262))
spawn('CivicSign','SM_Ref_Sign',(1140,-56,210),180)
spawn('TV','SM_Ref_TV',(820,-100,0),180)
spawn('NoticeBoard','SM_Ref_NoticeBoard',(1150,-58,145),180)
spawn('Clock','SM_Ref_Clock',(980,-58,210),180)
for i,(x,y) in enumerate(((1080,-340),(1200,-380),(1160,-400))):spawn(f'Mug{i}','SM_Ref_Mug',(x,y,76.65),i*27,collision=False)
spawn('Notebook','SM_Ref_Notebook',(1230,-340,76.65),18,collision=False)
spawn('Blanket','SM_Ref_Blanket',(795,-477,58.3),-90,collision=False)
# Existing TV/notice wall are replaced by coherent pieces using shared authored kit.
# Additional small practical table along the sofa, shelf, documents and tea.
spawn('SideTable','SM_Ref_Table',(820,-580,0),0,(.35,.65,1));spawn('SideTea','SM_Ref_Mug',(840,-590,76.65),collision=False)
spawn('Journal','SM_Ref_Notebook',(810,-590,76.65),12,collision=False)
spawn('Radio','SM_Ref_Radio',(825,-565,76.65),0,collision=False)
spawn('OpenBookcase','SM_Ref_CabinetBody',(1540,-470,0),90)
for i in range(4):spawn(f'BookOnShelf{i}','SM_Ref_Notebook',(1540,-475+i*8,53.75),90,collision=False)
spawn('CardTable','SM_Ref_Table',(1480,-625,0),0,(.45,.7,1))
spawn('CardChair','SM_Ref_Chair',(1480,-540,0),180)
for i in range(3):
 a=spawn(f'Card{i}','SM_Ref_FloorTile',(1455+i*12,-625,76.675),i*8,(.06,.09,.03),collision=False);a.static_mesh_component.set_material(0,mats['Paper'])
for i,x in enumerate((727,1573)):
 a=spawn(f'CoveFixture{i}','SM_Ref_Lamp',(x,-420,248),90);a.set_actor_rotation(u.Rotator(yaw=90,roll=180),False)
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.PointLight,u.Vector(x,-420,262));a.set_actor_label(f'REF_CoveLight{i}');c=a.point_light_component;c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_editor_property('intensity',120);c.set_editor_property('attenuation_radius',600);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',4600);c.set_editor_property('cast_shadows',False);c.set_editor_property('source_radius',12);setchannels(c)
if not cab:cab=u.EditorLevelLibrary.spawn_actor_from_class(u.load_class(None,'/Script/Condominio13.BunkerReferenceCabinet'),u.Vector(1435,-100,0),u.Rotator(yaw=180))
cab.set_actor_location(u.Vector(1435,-100,2.6),False,False)
cab.get_editor_property('hinge').set_relative_location(u.Vector(-57.6,27,0),False,False);cab.get_editor_property('door_collision').set_box_extent(u.Vector(57.6,2,94));cab.get_editor_property('door_collision').set_relative_location(u.Vector(57.6,0,100),False,False)
cab.set_actor_label('REF_PhysicalCabinet');cab.mesh.set_static_mesh(meshes['SM_Ref_CabinetBody']);cab.mesh.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);cab.get_editor_property('leaf').set_static_mesh(meshes['SM_Ref_CabinetLeaf']);setchannels(cab.mesh);setchannels(cab.get_editor_property('leaf'))
for sound in ('Open','Close'):
 t=u.AssetImportTask();t.filename=str(R/'assets/reference_room'/f'S_Cabinet_{sound}.wav');t.destination_path=D+'/Audio';t.automated=True;t.replace_existing=True;t.save=True;A.import_asset_tasks([t]);cab.set_editor_property(sound.lower()+'_sound',u.load_asset(D+'/Audio/S_Cabinet_'+sound))
# Local post-process volume: fixed exposure remains confined to the approved room.
a=u.EditorLevelLibrary.spawn_actor_from_class(u.PostProcessVolume,u.Vector(1150,-380,150));a.set_actor_label('REF_Exposure');a.set_actor_scale3d(u.Vector(4.3,3.3,1.4));a.set_editor_property('unbound',False);a.set_editor_property('blend_radius',20);a.set_editor_property('priority',50)
p=a.get_editor_property('settings');p.set_editor_property('override_auto_exposure_method',True);p.set_editor_property('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL);p.set_editor_property('override_auto_exposure_bias',True);p.set_editor_property('auto_exposure_bias',-1.5);p.set_editor_property('override_auto_exposure_apply_physical_camera_exposure',True);p.set_editor_property('auto_exposure_apply_physical_camera_exposure',False);a.set_editor_property('settings',p)
u.EditorLevelLibrary.save_current_level();u.EditorAssetLibrary.save_directory(D,only_if_is_dirty=True,recursive=True)
after=[{'name':a.get_name(),'class':a.get_class().get_name(),'position':list(a.get_actor_location().to_tuple())} for a in u.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name().startswith('Bunker') and a.get_class().get_name()!='BunkerReferenceCabinet']
assert sorted(native_before,key=lambda a:a['name'])==sorted(after,key=lambda a:a['name']),'Legacy native actor keys/positions changed'
(R/'logs/reference_unreal_import.json').write_text(json.dumps({'assets':manifest,'legacy_native_actors_unchanged':True,'new_container_initial_contents':0,'scope':'living room only','cabinet_name':cab.get_name()},indent=2))
exec(compile((R/'scripts/install_reference_shell.py').read_text(),str(R/'scripts/install_reference_shell.py'),'exec'))
exec(compile((R/'scripts/refine_reference_shading.py').read_text(),str(R/'scripts/refine_reference_shading.py'),'exec'))
exec(compile((R/'scripts/install_reference_native_props.py').read_text(),str(R/'scripts/install_reference_native_props.py'),'exec'))
exec(compile((R/'scripts/style_reference_doors.py').read_text(),str(R/'scripts/style_reference_doors.py'),'exec'))
exec(compile((R/'scripts/tune_reference_layout.py').read_text(),str(R/'scripts/tune_reference_layout.py'),'exec'))
exec(compile((R/'scripts/refine_reference_practicals.py').read_text(),str(R/'scripts/refine_reference_practicals.py'),'exec'))
exec(compile((R/'scripts/snapshot_reference_scene.py').read_text(),str(R/'scripts/snapshot_reference_scene.py'),'exec'))
u.log_warning('C13_REFERENCE_IMPORT_OK')
