"""Export opened presentation variants without changing the world pickup sources."""
import bpy,bmesh,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'exports/hands';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/Bunker_Items_v001.blend'))
report=[]
for key in ('Water','Food'):
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for src in bpy.data.collections['ITEM_'+key].objects:
  if (key=='Water' and src.name.startswith(('Cap threaded','Cap grip','Neck tamper'))) or (key=='Food' and src.name.startswith(('Recessed lid','Ring lid stamp','Ring pull tab','Tab rivet'))):continue
  cp=src.copy();cp.data=src.data.copy();bpy.context.scene.collection.objects.link(cp);cp.hide_set(False);cp.hide_render=False
  if cp.name.startswith('Body'):
   bm=bmesh.new();bm.from_mesh(cp.data)
   top=.197 if key=='Water' else .119
   bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.normal.z>.9 and f.calc_center_median().z>top],context='FACES');bm.to_mesh(cp.data);bm.free()
  cp.select_set(True);copies.append(cp)
 # A dark interior for the neck, food-colored fill below the open can rim.
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.013 if key=='Water' else .038,depth=.002,location=(0,0,.191 if key=='Water' else .110))
 fill=bpy.context.object;fill.name='Visible interior';fill.data.materials.append(copies[0].data.materials[0]);fill.data.uv_layers.new() if not fill.data.uv_layers else None
 for loop in fill.data.uv_layers.active.data:loop.uv=(.15,.15) if key=='Water' else (.15,.70)
 copies.append(fill)
 bpy.ops.object.select_all(action='DESELECT')
 for cp in copies:cp.select_set(True)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();obj=bpy.context.object;obj.name='SM_Use_'+key
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(OUT/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
 report.append({'asset':obj.name,'variant':'Open neck' if key=='Water' else 'Open can with visible fill','dimensions_m':list(obj.dimensions)})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Bunker_ItemUseVariants_v001.blend'))
(ROOT/'logs/item_use_variants.json').write_text(json.dumps(report,indent=2));print('C13_OPEN_VARIANTS_OK')
