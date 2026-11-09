"""Detailed replacements keep the legacy interactable roots and saved keys intact."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
source=(R/'scripts/create_reference_details.py').read_text();exec(compile(source.split('# Vintage CRT')[0],str(R/'scripts/create_reference_details.py'),'exec'))
if 'M_Ref_Amber' not in bpy.data.materials:
 m=bpy.data.materials.new('M_Ref_Amber');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.75,.35,.055,1);p.inputs['Roughness'].default_value=.6
# Standard-sized target; the existing random-score minigame remains a placeholder.
cyl('Target body',(0,0,0),.2255,.04,'Paint',(math.pi/2,0,0))
order=[20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]
for i in range(20):
 a0=(i-.5)*2*math.pi/20;a1=(i+.5)*2*math.pi/20
 for rin,rout,ring in [(0.018,.105,0),(.105,.116,1),(.116,.165,0),(.165,.176,1),(.176,.193,0)]:
  vs=[(math.sin(a)*r,-.0215,math.cos(a)*r) for a,r in ((a0,rin),(a1,rin),(a1,rout),(a0,rout))]
  me=bpy.data.meshes.new('Target segment');me.from_pydata(vs,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('Target segment',me);bpy.context.collection.objects.link(o);o.data.materials.append(mat(('Paint' if i%2==0 else 'Amber') if ring else ('Ivory' if i%2==0 else 'Rubber')));parts.append(o)
 a=i*2*math.pi/20;text(str(order[i]),(math.sin(a)*.207-.007,-.023,math.cos(a)*.207-.008),.015);parts[-1].data.materials.clear();parts[-1].data.materials.append(mat('Ivory'))
cyl('Bull',(0,-.023,0),.018,.003,'Amber',(math.pi/2,0,0));cyl('Inner bull',(0,-.025,0),.008,.003,'Paint',(math.pi/2,0,0));finish('SM_Ref_Dartboard')
def variant(srcname,name,offset,scale):
 old=bpy.data.objects.get(name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 src=bpy.data.objects[srcname];o=src.copy();o.data=src.data.copy();bpy.context.collection.objects.link(o);o.name=name;o.hide_set(False);o.hide_render=False
 for v in o.data.vertices:
  for a in range(3):v.co[a]=(v.co[a]+offset[a])/scale[a]
 o['purpose']='Baked visual offset preserves the legacy native actor transform and checkpoint identity.'
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,mesh_smooth_type='FACE')
 for c in list(o.users_collection):c.objects.unlink(o)
 lib.objects.link(o);o.hide_set(True);o.hide_render=True;manifest[name]={'dimensions_m':list(o.dimensions),'polygons':len(o.data.polygons),'materials':[m.name for m in o.data.materials],'legacy_actor_scale':scale,'visual_offset_m':offset}
variant('SM_Ref_Radio','SM_Ref_RadioLegacy',(.20,.45,-.3185),(.55,.4,.32))
variant('SM_Ref_Dartboard','SM_Ref_DartboardLegacy',(0,0,.28),(.62,.12,.62))
# Physical UV channel, in meters, for Unreal's decoded tangent normal maps.
for name in manifest:
 o=bpy.data.objects[name]
 if len(o.data.uv_layers)<2:
  uv=o.data.uv_layers.new(name='PhysicalMeters')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda a:abs(p.normal[a]));axes=[a for a in range(3) if a!=axis]
   for li in p.loop_indices:
    co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
  bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,mesh_smooth_type='FACE');o.hide_set(True)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'));print('REFERENCE_NATIVE_PROPS_OK')
