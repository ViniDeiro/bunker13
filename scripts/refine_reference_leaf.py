import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'exports/reference_room';bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'))
o=bpy.data.objects['SM_Ref_CabinetLeaf']
# 4mm side reveals in a 1160mm clear opening. Only run once for this source revision.
if not o.get('side_reveal_mm'):
 for v in o.data.vertices:v.co.x*=1.152/1.12
 o['side_reveal_mm']=4
bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(O/'SM_Ref_CabinetLeaf.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,mesh_smooth_type='FACE')
o.hide_set(True)
# Ground the ceramic mug at its actual base instead of a floating pivot.
mug=bpy.data.objects['SM_Ref_Mug'];minimum=min(v.co.z for v in mug.data.vertices)
for v in mug.data.vertices:v.co.z-=minimum
bpy.ops.object.select_all(action='DESELECT');mug.hide_set(False);mug.select_set(True);bpy.context.view_layer.objects.active=mug
bpy.ops.export_scene.fbx(filepath=str(O/'SM_Ref_Mug.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,mesh_smooth_type='FACE')
mug.hide_set(True)
m=json.loads((O/'manifest.json').read_text());m[o.name]['dimensions_m']=list(o.dimensions);m[o.name]['side_reveal_mm']=4;(O/'manifest.json').write_text(json.dumps(m,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'));print('REFERENCE_LEAF_REVEAL_OK')
