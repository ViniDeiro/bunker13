import bpy,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'exports/reference_room';bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'))
s=bpy.context.scene;lib=bpy.data.collections['ASSET_LIBRARY'];parts=[]
def mat(n):return bpy.data.materials['M_Ref_'+n]
def box(n,p,d,m,b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);md=o.modifiers.new('Rounded joinery','BEVEL');md.width=min(b,min(d)*.25);md.segments=3;bpy.ops.object.modifier_apply(modifier=md.name);o.data.materials.append(mat(m));parts.append(o);return o
def cyl(n,p,r,dep,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=dep,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(mat(m));parts.append(o);return o
def text(n,p,size):
 bpy.ops.object.text_add(location=p,rotation=(math.pi/2,0,0));o=bpy.context.object;o.data.body=n;o.data.size=size;o.data.extrude=.0003;o.data.materials.append(mat('Paint'));bpy.ops.object.convert(target='MESH');parts.append(bpy.context.object)
manifest=json.loads((O/'manifest.json').read_text())
def finish(name):
 global parts
 old=bpy.data.objects.get(name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False)
 manifest[name]={'dimensions_m':list(o.dimensions),'polygons':len(o.data.polygons),'materials':[m.name for m in o.data.materials]}
 for c in list(o.users_collection):c.objects.unlink(o)
 lib.objects.link(o);o.hide_set(True);o.hide_render=True;parts=[]
# Vintage CRT and stand with visible back ventilation, speaker grille, controls.
for x in (-.36,.36):
 for y in (-.18,.18):box('Stand leg',(x,y,.24),(.04,.04,.48),'Wood')
box('Stand top',(0,0,.49),(.90,.52,.035),'Wood');box('Stand shelf',(0,0,.14),(.82,.44,.02),'Wood')
box('CRT casing',(0,0,.79),(.78,.43,.55),'Paint',.035)
box('Screen rubber surround',(-.065,-.222,.82),(.59,.022,.44),'Rubber',.022)
# Dark glass uses polished steel with very low albedo as an unpowered CRT face.
box('Dark curved glass',(-.065,-.24,.82),(.54,.018,.39),'Steel',.018)
for i in range(13):box('Speaker slit',(.315,-.224,.68+i*.012),(.055,.008,.004),'Rubber',.001)
for z in (.94,1.01):cyl('Channel dial',(.313,-.236,z),.022,.025,'Ivory',(math.pi/2,0,0))
for x in (-.28,.28):
 for i in range(9):box('Side ventilation',(x,.219,.64+i*.032),(.13,.004,.008),'Rubber',.001)
text('13',(-.325,-.253,.59),.025);finish('SM_Ref_TV')
# Framed inhabited notice wall, with physical paper and pins, no gameplay promises.
box('Notice cork',(0,0,0),(1.48,.022,.85),'Wood')
for x in (-.76,.76):box('Notice frame side',(x,-.01,0),(.035,.035,.91),'Paint')
for z in (-.45,.45):box('Notice frame rail',(0,-.01,z),(1.55,.035,.035),'Paint')
for i,(x,z) in enumerate(((-.52,.15),(-.12,.08),(.37,.19),(.34,-.21))):
 box('Pinned paper',(x,-.023,z),(.28,.002,.32 if i<3 else .22),'Paper',.0004);cyl('Pin',(x,-.03,z+.13),.005,.009,'Steel',(math.pi/2,0,0));text(('TURNO 01','AGUA','AVISO','SANTA AURORA')[i],(x-.12,-.026,z+.05),.027)
 for row in range(3):box('Written note',(x,-.027,z-.025-row*.035),(.21-row*.015,.001,.002),'Paint',.0001)
finish('SM_Ref_NoticeBoard')
cyl('Clock rim',(0,0,0),.19,.035,'Steel',(math.pi/2,0,0));cyl('Clock dial',(0,-.023,0),.177,.009,'Ivory',(math.pi/2,0,0))
for i in range(12):
 a=i*math.pi/6;o=box('Hour index',(math.sin(a)*.15,-.029,math.cos(a)*.15),(.005,.002,.018),'Paint',.0005);o.rotation_euler[1]=a
box('Minute hand',(.045,-.031,.04),(.008,.003,.125),'Paint',.001).rotation_euler[1]=-.65
box('Hour hand',(-.025,-.035,.014),(.008,.003,.085),'Paint',.001).rotation_euler[1]=1.0
cyl('Clock arbor',(0,-.04,0),.01,.006,'Steel',(math.pi/2,0,0));finish('SM_Ref_Clock')
# Small shared radio, with perforated speaker face, tuning scale, knobs and feet.
box('Radio shell',(0,0,.13),(.42,.20,.24),'Paint',.018)
for x in (-.17,.17):box('Radio rubber foot',(x,0,.013),(.04,.13,.026),'Rubber')
box('Speaker recess',(-.075,-.107,.13),(.23,.012,.17),'Rubber',.007)
for i in range(12):box('Speaker grille bar',(-.175+i*.018,-.117,.13),(.004,.006,.15),'Steel',.001)
box('Tuning scale',(.125,-.108,.18),(.12,.005,.035),'Ivory',.002)
for x in (.09,.16):cyl('Radio knob',(x,-.126,.09),.022,.025,'Rubber',(math.pi/2,0,0))
text('AURORA',(-.03,-.121,.225),.015);finish('SM_Ref_Radio')
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'));print('REFERENCE_DETAILS_OK')
