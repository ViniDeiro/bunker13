"""Reopen authored Blender sources and verify real geometry/UV/export integrity."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];checks=[]
for filename,names in [('Bunker_Hands_v001.blend',['SM_Hands_Left','SM_Hands_Right','SM_Hands_Spoon','SM_Hands_Bandage']),('Bunker_ItemUseVariants_v001.blend',['SM_Use_Water','SM_Use_Food'])]:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender'/filename))
 for name in names:
  obj=bpy.data.objects[name];assert obj.type=='MESH' and obj.data.uv_layers.active
  assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
  assert all(-.001<=c<=1.001 for loop in obj.data.uv_layers.active.data for c in loop.uv)
  assert all(abs(v-1)<.0001 for v in obj.scale)
  assert max(obj.dimensions)<.35
  src=ROOT/'exports/hands'/(name+'.fbx');assert src.stat().st_size>1000
  checks.append({'name':name,'vertices':len(obj.data.vertices),'dimensions_m':list(obj.dimensions),'uv_valid':True,'fbx_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
(ROOT/'logs/hands_source_validation.json').write_text(json.dumps({'passed':True,'reopened_blends':2,'assets':checks},indent=2));print('C13_HANDS_SOURCE_PASS')
