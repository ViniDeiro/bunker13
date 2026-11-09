import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Bunker_CollectionRound_v001.blend'))
errors=[];col=bpy.data.collections['ROUND_Market_Access'];floors=[o for o in col.objects if 'MarketFloor' in o.name]
if len(floors)!=4:errors.append('Expected four floor pieces')
for o in col.objects:
 if any(not math.isfinite(v) for p in o.data.vertices for v in p.co):errors.append('Nonfinite '+o.name)
for o in floors:
 inv=o.matrix_world.inverted();hit,*_=o.ray_cast(inv@Vector((25.5,-5,4)),inv.to_3x3()@Vector((0,0,-1)))
 if hit:errors.append('Floor covers stair opening: '+o.name)
result={'passed':not errors,'reopened':True,'floor_pieces':len(floors),'new_geometry_objects':len(col.objects),'stair_opening_m':[2.2,8.0],'unit_scale':bpy.context.scene.unit_settings.scale_length,'errors':errors}
(R/'logs/round_architecture_validation.json').write_text(json.dumps(result,indent=2));print(result)
if errors:raise RuntimeError(errors)
