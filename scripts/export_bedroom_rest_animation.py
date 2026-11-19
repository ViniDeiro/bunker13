"""Sample the saved editable action; unlike the generator, never rebuilds its poses."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];rig=bpy.data.objects.get('C13_Manny_Rest_Rig')
if not rig:
 bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Bedroom_Rest_Animation_v001.blend'));rig=bpy.data.objects['C13_Manny_Rest_Rig']
s=bpy.context.scene;assert abs(s.unit_settings.scale_length-1)<1e-6
ref=json.loads((R/'exports/bedroom_rest_rig.json').read_text());B=Matrix.Diagonal((1,-1,1,1));tracks={b['name']:{'positions':[],'rotations':[],'scales':[]} for b in ref['bones']};previous=s.frame_current
for frame in range(s.frame_start,s.frame_end+1):
 s.frame_set(frame);bpy.context.view_layer.update()
 for b in ref['bones']:
  m=rig.pose.bones[b['name']].matrix
  if b['parent']>=0:m=rig.pose.bones[ref['bones'][b['parent']]['name']].matrix.inverted()@m
  p,q,scale=(B@m@B).decompose();t=tracks[b['name']];t['positions'].append(list(p*100));t['rotations'].append([q.x,q.y,q.z,q.w]);t['scales'].append(list(scale))
s.frame_set(previous)
result={'skeleton':ref['skeleton'],'fps':s.render.fps,'frames':s.frame_end-s.frame_start+1,'tracks':tracks,'editable_source':bpy.data.filepath}
(R/'exports/bedroom_rest_animation.json').write_text(json.dumps(result,separators=(',',':')))
print('C13_EDITED_REST_ACTION_EXPORTED',result['frames'],len(tracks),flush=True)
