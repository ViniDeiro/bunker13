"""Open master .blend > Scripting > this text > Run Script.
Select a 3D viewport, F3 > B1 Navegar. WASD, mouse look, Shift slow, Esc exits.
Local inspection only: no multiplayer or UE gameplay implemented.
"""
import bpy, json, math, time
from pathlib import Path
from mathutils import Vector, Euler
class B1Walk(bpy.types.Operator):
 bl_idname='view3d.b1_navegar';bl_label='B1 Navegar';bl_options={'REGISTER'}
 def floor(self,x,y):
  if 24.6<=x<=26.4 and -8<=y<-2:return max(0,3-.15*int((y+8)/.3))
  if 24<=x<=27 and -10<=y<-8:return 3
  return 0
 def clear(self,x,y):
  r=.30;z=self.floor(x,y)
  inside=(r<x<28-r and r<y<20-r) or (24.6+r<x<26.4-r and -8<y<.5) or (24+r<x<27-r and -10+r<y<=-8)
  if not inside:return False
  for o in self.nav['obstacles']:
   a,b=o['min'],o['max']
   if a[2]>=z+1.75 or b[2]<=z+.09:continue
   if a[0]-r<x<b[0]+r and a[1]-r<y<b[1]+r:return False
  return True
 def modal(self,context,event):
  if event.type=='ESC':
   context.window_manager.event_timer_remove(self.timer);context.window.cursor_modal_restore();self.area.header_text_set(None);self.area.spaces.active.overlay.show_overlays=self.old_overlay;return {'FINISHED'}
  if event.type in {'W','A','S','D','LEFT_SHIFT','RIGHT_SHIFT'}:
   if event.value=='PRESS':self.keys.add(event.type)
   elif event.value=='RELEASE':self.keys.discard(event.type)
  if event.type=='MOUSEMOVE':
   self.yaw-=(event.mouse_x-event.mouse_prev_x)*.003
   self.pitch=max(-1.4,min(1.4,self.pitch-(event.mouse_y-event.mouse_prev_y)*.003))
  if event.type=='TIMER':
   now=time.monotonic();dt=min(.04,now-self.last);self.last=now
   dx=int('D'in self.keys)-int('A'in self.keys);dy=int('W'in self.keys)-int('S'in self.keys)
   v=Vector((dx*math.cos(self.yaw)-dy*math.sin(self.yaw),dx*math.sin(self.yaw)+dy*math.cos(self.yaw),0))
   if v.length:v.normalize();v*=dt*(.7 if any('SHIFT'in k for k in self.keys) else 1.4)
   for axis in [0,1]:
    p=self.pos.copy();p[axis]+=v[axis]
    if self.clear(p.x,p.y):self.pos=p
   self.pos.z=self.floor(self.pos.x,self.pos.y)+1.65
   rv=self.area.spaces.active.region_3d;rv.view_perspective='PERSP';rv.view_rotation=Euler((math.pi/2+self.pitch,0,self.yaw),'XYZ').to_quaternion();rv.view_distance=0;rv.view_location=self.pos
   self.area.tag_redraw()
  return {'RUNNING_MODAL'}
 def invoke(self,context,event):
  if context.area.type!='VIEW_3D':self.report({'ERROR'},'Execute F3 em uma vista 3D');return {'CANCELLED'}
  self.nav=json.loads((Path(bpy.data.filepath).parents[1]/'exports/navigation.json').read_text())
  self.pos=Vector(self.nav['spawn']);self.yaw=0;self.pitch=0;self.keys=set();self.area=context.area;self.last=time.monotonic()
  self.old_overlay=self.area.spaces.active.overlay.show_overlays;self.area.spaces.active.overlay.show_overlays=False;self.area.spaces.active.shading.type='MATERIAL';self.area.header_text_set('B1 / WASD: andar | Mouse: olhar | Shift: lento | Esc: sair / capsula 0,60 x 1,75 m')
  self.timer=context.window_manager.event_timer_add(1/60,window=context.window);context.window_manager.modal_handler_add(self);return {'RUNNING_MODAL'}
try:bpy.utils.unregister_class(B1Walk)
except:pass
bpy.utils.register_class(B1Walk)
def menu_b1(self,context):self.layout.operator('view3d.b1_navegar')
bpy.types.VIEW3D_MT_view.append(menu_b1)
print('B1 Navegar registrado: use F3 em uma vista 3D.')
