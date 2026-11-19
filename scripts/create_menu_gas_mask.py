"""Original editable prop, authored in Blender; no external meshes/textures."""
from pathlib import Path
import bpy, math
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC'
parts=[]
def sphere(name,p,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=p)
 o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(o)
 return o
def cylinder(name,p,r,h,rot):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=h,location=p,rotation=rot)
 o=bpy.context.object;o.name=name;parts.append(o)
 m=o.modifiers.new('Manufactured lip','BEVEL');m.width=.004;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
 return o
sphere('Rubber face shell',(0,0,.13),(.105,.066,.135))
for x in (-.047,.047):
 cylinder('Goggle steel rim',(x,-.057,.175),.043,.022,(math.pi/2,0,0))
 cylinder('Recessed glass',(x,-.071,.175),.035,.005,(math.pi/2,0,0))
cylinder('Filter thread',(0,-.071,.075),.041,.05,(math.pi/2,0,0))
cylinder('Filter cartridge',(0,-.113,.075),.048,.052,(math.pi/2,0,0))
for k in range(5):
 cylinder('Filter cooling ring',(0,-.094-k*.009,.075),.049,.003,(math.pi/2,0,0))
for x in (-.104,.104):
 sphere('Harness anchor',(x,.005,.13),(.009,.033,.012))
mat=bpy.data.materials.new('Menu_Rubber');mat.diffuse_color=(.032,.039,.036,1)
for o in parts:o.data.materials.append(mat)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
o=bpy.context.object;o.name='SM_Menu_Respirator'
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Menu_Respirator_v001.blend'))
dest=R/'exports/main_menu';dest.mkdir(exist_ok=True)
bpy.ops.export_scene.fbx(filepath=str(dest/'SM_Menu_Respirator.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True)
print('C13_MENU_MASK_EXPORTED')
# Companion desk lamp: separate editable object, with metal shade and stem.
parts=[]
cylinder('Lamp base',(0,0,.022),.16,.044,(0,0,0))
cylinder('Lamp stem',(-.09,0,.30),.018,.56,(0,0,0))
sphere('Lamp elbow',(-.09,0,.58),(.035,.035,.035))
cylinder('Lamp arm',(.025,0,.65),.016,.27,(0,math.pi/3,0))
bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.16,radius2=.07,depth=.19,location=(.13,0,.59))
shade=bpy.context.object;shade.name='Metal bell shade';parts.append(shade)
for obj in parts:
 if not obj.data.materials:obj.data.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
lamp=bpy.context.object;lamp.name='SM_Menu_DeskLamp'
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.export_scene.fbx(filepath=str(dest/'SM_Menu_DeskLamp.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Menu_Respirator_v001.blend'))
# Round industrial pipe section with real flanges and eight bolts per flange.
parts=[]
cylinder('Pipe barrel',(0,0,0),.075,1,(0,math.pi/2,0))
for x in (-.46,.46):
 cylinder('Flange',(x,0,0),.105,.025,(0,math.pi/2,0))
 for k in range(8):
  a=k*math.pi/4
  cylinder('Flange bolt',(x-.018,.089*math.cos(a),.089*math.sin(a)),.009,.022,(0,math.pi/2,0))
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
pipe=bpy.context.object;pipe.name='SM_Menu_Pipe'
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
for poly in pipe.data.polygons:poly.use_smooth=True
bpy.ops.export_scene.fbx(filepath=str(dest/'SM_Menu_Pipe.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Menu_Respirator_v001.blend'))
parts=[]
cylinder('Ventilator hub',(0,0,0),.045,.045,(0,0,0))
for k in range(4):
 a=k*math.pi/2
 bpy.ops.mesh.primitive_cube_add(size=1,location=(.105*math.cos(a),.105*math.sin(a),0))
 o=bpy.context.object;o.name='Formed fan blade';o.dimensions=(.19,.055,.01);o.rotation_euler.z=a
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 m=o.modifiers.new('Rounded blade','BEVEL');m.width=.018;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
 parts.append(o)
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
fan=bpy.context.object;fan.name='SM_Menu_Fan'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.export_scene.fbx(filepath=str(dest/'SM_Menu_Fan.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Menu_Respirator_v001.blend'))
