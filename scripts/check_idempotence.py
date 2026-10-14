import bpy,runpy,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/Bunker_Blockout_v001.blend'))
def signature():
 return sorted((o.name,o.type,tuple(round(v,5) for v in o.matrix_world.translation),tuple(round(v,5) for v in o.dimensions),len(o.data.vertices) if o.type=='MESH' else 0) for o in bpy.context.scene.objects)
a=signature();sys.argv.append('--no-render')
runpy.run_path(str(ROOT/'scripts/create_bunker_blockout.py'),run_name='__main__')
b=signature();out={'pass':a==b,'before_objects':len(a),'after_objects':len(b),'before_sha256':hashlib.sha256(repr(a).encode()).hexdigest(),'after_sha256':hashlib.sha256(repr(b).encode()).hexdigest()}
(ROOT/'logs/idempotence.json').write_text(json.dumps(out,indent=2))
inv=[{'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection],'dimensions_m':list(o.dimensions),'location':list(o.location)} for o in bpy.context.scene.objects]
(ROOT/'logs/object_inventory.json').write_text(json.dumps(inv,indent=2));print('IDEMPOTENCE',out);assert out['pass']
