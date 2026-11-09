import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'exports/reference_room';bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'));manifest=json.loads((O/'manifest.json').read_text());removed={}
for name in manifest:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if f.calc_area()<1e-12]
 if not bad:bm.free();continue
 removed[name]=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,mesh_smooth_type='FACE');o.hide_set(True);manifest[name]['polygons']=len(o.data.polygons)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));(R/'logs/reference_geometry_cleanup.json').write_text(json.dumps(removed,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'));print('REFERENCE_CLEANUP',removed)
