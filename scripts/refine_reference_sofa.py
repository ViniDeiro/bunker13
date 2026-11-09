import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'exports/reference_room';bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'));o=bpy.data.objects['SM_Ref_Sofa']
if not o.get('seat_deck_added'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.045,.36));d=bpy.context.object;d.name='Seat support deck';d.dimensions=(2.1,.7,.04);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);d.data.materials.append(bpy.data.materials['M_Ref_Paint']);mod=d.modifiers.new('Rounded deck','BEVEL');mod.width=.005;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);d.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.join();o['seat_deck_added']=True
 uv=o.data.uv_layers.get('PhysicalMeters') or o.data.uv_layers.new(name='PhysicalMeters')
 for p in o.data.polygons:
  ax=max(range(3),key=lambda a:abs(p.normal[a]));axes=[a for a in range(3) if a!=ax]
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(O/'SM_Ref_Sofa.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,mesh_smooth_type='FACE');o.hide_set(True)
m=json.loads((O/'manifest.json').read_text());m[o.name]['polygons']=len(o.data.polygons);(O/'manifest.json').write_text(json.dumps(m,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'));print('REFERENCE_SEAT_SUPPORT_OK')
