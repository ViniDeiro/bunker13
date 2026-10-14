import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/Bunker_Blockout_v001.blend'))
cols=['ARCH_Walls','ARCH_Floors','ARCH_Ceilings','ARCH_Doors','ARCH_Stairs','PROPS_Blockout']
names={o.name for c in cols for o in bpy.data.collections[c].objects if o.type=='MESH'}
expected={n:list(bpy.data.objects[n].dimensions) for n in names};results={}
for ext in ['glb','fbx']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if ext=='glb':bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports/Bunker_Blockout_v001.glb'))
 else:bpy.ops.import_scene.fbx(filepath=str(ROOT/'exports/Bunker_Blockout_v001.fbx'))
 missing=[n for n in names if n not in bpy.data.objects];wrong=[];nomat=[]
 for n,d in expected.items():
  o=bpy.data.objects.get(n)
  if not o:continue
  if any(abs(a-b)>.001 for a,b in zip(o.dimensions,d)):wrong.append(n)
  if not o.data.materials:nomat.append(n)
 results[ext]={'missing':missing,'wrong_dimensions':wrong,'missing_materials':nomat,'imported_meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'collision_meshes':sum(o.name.startswith('UCX_') for o in bpy.context.scene.objects),'pass':not(missing or wrong or nomat)}
(ROOT/'logs/export_roundtrip.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2));assert all(v['pass'] for v in results.values())
