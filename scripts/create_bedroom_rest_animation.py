"""Editable 89-bone rig/action. Proxy geometry is authoring-only; UE keeps its real skinned mesh."""
import bpy,json,math
from mathutils import Matrix,Vector,Quaternion
from pathlib import Path
R=Path(__file__).resolve().parents[1];data=json.loads((R/'exports/bedroom_rest_rig.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.fps=30;s.frame_start=1;s.frame_end=36
bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='C13_Manny_Rest_Rig';bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
B=Matrix.Diagonal((1,-1,1,1));globals=[]
for b in data['bones']:
 q=b['rotation'];m=Quaternion((q[3],*q[:3])).to_matrix().to_4x4();m.translation=Vector(b['position'])/100
 m=B@m@B;world=globals[b['parent']]@m if b['parent']>=0 else m;globals.append(world)
 bone=rig.data.edit_bones.new(b['name']);bone.length=.05;bone.matrix=world
 if b['parent']>=0:bone.parent=rig.data.edit_bones[data['bones'][b['parent']]['name']]
bpy.ops.object.mode_set(mode='POSE')
def reset():
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
def aim(bone,child,target):
 p=rig.pose.bones[bone];a=p.matrix.copy();v=rig.pose.bones[child].matrix.translation-a.translation
 q=v.normalized().rotation_difference(Vector(target).normalized());out=(q@a.to_quaternion()).to_matrix().to_4x4();out.translation=a.translation;p.matrix=out;bpy.context.view_layer.update()
# Verify lossless reference-frame round trip before adding animation.
reset();max_error=0
for i,b in enumerate(data['bones']):
 m=rig.pose.bones[b['name']].matrix
 if b['parent']>=0:m=rig.pose.bones[data['bones'][b['parent']]['name']].matrix.inverted()@m
 ue=B@m@B;max_error=max(max_error,(ue.translation*100-Vector(b['position'])).length)
assert max_error<.002,max_error
for frame,root_angle,knee,reach in ((1,0,0,0),(10,-18,30,.20),(22,-62,36,.14),(36,-90,4,0)):
 reset()
 for side,sign in (('l',1),('r',-1)):
  aim('upperarm_'+side,'lowerarm_'+side,(sign*.10,.06 if frame==36 else -reach,-1))
  aim('lowerarm_'+side,'hand_'+side,(sign*.03,.04 if frame==36 else -reach*.6,-1))
  a=math.radians(knee)
  aim('thigh_'+side,'calf_'+side,(sign*.02,.10 if frame==36 else -math.sin(a*.5),-math.cos(a*.5)))
  aim('calf_'+side,'foot_'+side,(0,.10 if frame==36 else math.sin(a*.5),-math.cos(a*.5)))
 rig.pose.bones['root'].rotation_mode='QUATERNION';rig.pose.bones['root'].rotation_quaternion=Quaternion((1,0,0),math.radians(root_angle))
 for p in rig.pose.bones:
  p.rotation_mode='QUATERNION';p.keyframe_insert('location',frame=frame);p.keyframe_insert('rotation_quaternion',frame=frame);p.keyframe_insert('scale',frame=frame)
rig.animation_data.action.name='C13_Rest_Recline_v001'
bpy.ops.object.mode_set(mode='OBJECT')
# Simple weighted proxies show the action without copying the character's art into this file.
s.frame_set(1);mat=bpy.data.materials.new('Authoring proxy — not game asset');mat.diffuse_color=(.06,.25,.19,1)
for bone,child,radius in [('pelvis','spine_02',.13),('spine_02','neck_01',.16)]+[(a+'_'+side,b+'_'+side,r) for side in ('l','r') for a,b,r in [('upperarm','lowerarm',.055),('lowerarm','hand',.045),('thigh','calf',.08),('calf','foot',.06)]]:
 a=globals[next(i for i,b in enumerate(data['bones']) if b['name']==bone)].translation;c=globals[next(i for i,b in enumerate(data['bones']) if b['name']==child)].translation
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=(c-a).length,location=(a+c)*.5);o=bpy.context.object;o.name='PROXY_'+bone;o.rotation_mode='QUATERNION';o.rotation_quaternion=(c-a).to_track_quat('Z','Y');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(mat);v=o.vertex_groups.new(name=bone);v.add(list(range(len(o.data.vertices))),1,'REPLACE');md=o.modifiers.new('Editable rig preview','ARMATURE');md.object=rig
head=globals[next(i for i,b in enumerate(data['bones']) if b['name']=='head')].translation
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.105,location=head+Vector((0,0,.06)));o=bpy.context.object;o.name='PROXY_head';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(mat);v=o.vertex_groups.new(name='head');v.add(list(range(len(o.data.vertices))),1,'REPLACE');o.modifiers.new('Editable rig preview','ARMATURE').object=rig
tracks={b['name']:{'positions':[],'rotations':[],'scales':[]} for b in data['bones']}
for frame in range(1,37):
 s.frame_set(frame);bpy.context.view_layer.update()
 for b in data['bones']:
  m=rig.pose.bones[b['name']].matrix
  if b['parent']>=0:m=rig.pose.bones[data['bones'][b['parent']]['name']].matrix.inverted()@m
  ue=B@m@B;p,q,scale=ue.decompose();t=tracks[b['name']];t['positions'].append(list(p*100));t['rotations'].append([q.x,q.y,q.z,q.w]);t['scales'].append(list(scale))
s['scope']='Authoring rig and weighted proxies only. Real Manny skinned mesh remains unchanged in Unreal.';s.frame_set(36)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bedroom_Rest_Animation_v001.blend'))
(R/'exports/bedroom_rest_animation.json').write_text(json.dumps({'skeleton':data['skeleton'],'fps':30,'frames':36,'reference_error_cm':max_error,'tracks':tracks},separators=(',',':')))
print('C13_REST_ANIMATION_SOURCE_OK',len(tracks),'bones; reference error cm',max_error,flush=True)
