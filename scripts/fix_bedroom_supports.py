"""Fix supports/contact gaps found in the first source render; only this study."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'exports/bedroom_study';S=bpy.context.scene
def support(n,p,d,mat):
 if n in bpy.data.objects:return
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);md=o.modifiers.new('Chamfer','BEVEL');md.width=.01;md.segments=3;bpy.ops.object.modifier_apply(modifier=md.name);o.data.materials.append(bpy.data.materials['M_Bedroom_'+mat])
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections['Furniture'].objects.link(o);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');o.data.uv_layers.new(name='Meters')
support('Monitor stand',(.29,1.96,.875),(.05,.09,.14),'Graphite')
for i,(x,y) in enumerate(((3.40,3.88),(3.40,4.35),(4.22,3.88),(4.22,4.35))):support('Locker foot_'+str(i),(x,y,.04),(.08,.08,.08),'Rubber')
if not S.get('contact_correction_v1'):
 for o in S.objects:
  if o.name.startswith(('Personal box','Label')):o.location.z-=.095
  if o.name=='Rolled linen':o.location.z-=.01
 S['contact_correction_v1']=True
manifest=json.loads((O/'manifest.json').read_text())
for group in ('Furniture','Details','Bed'):
 obs=[o for o in bpy.data.collections[group].objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 key='SM_Bedroom_'+group
 if group=='Bed':
  for o in obs:o.location.x-=1.17;o.location.y-=3.14
 bpy.ops.export_scene.fbx(filepath=str(O/(key+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False)
 if group=='Bed':
  for o in obs:o.location.x+=1.17;o.location.y+=3.14
 manifest['meshes'][key]['objects']=len(obs);manifest['meshes'][key]['triangles']=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bedroom_StyleStudy_v001.blend'))
(R/'logs/bedroom_blender.json').write_text(json.dumps({'objects':sum(m['objects'] for m in manifest['meshes'].values()),'triangles':sum(m['triangles'] for m in manifest['meshes'].values()),'uv_layers_min':2,'dimensions_m':[4.4,4.6,2.8],'entry_m':1.2,'packed_images':2,'contact_corrections':True},indent=2))
print('C13_BEDROOM_CONTACTS_FIXED',flush=True)
