"""Original, editable industrial bedroom study. Does not modify earlier sources."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'exports/bedroom_study';O.mkdir(parents=True,exist_ok=True)
(R/'logs').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
palette={'Ivory':((.65,.61,.48),0,.57),'Green':((.055,.16,.12),0,.46),'Graphite':((.035,.048,.05),.35,.4),'Steel':((.18,.22,.23),.8,.32),'Rubber':((.012,.018,.018),0,.88),'Teal':((.025,.27,.30),0,.85),'Linen':((.66,.62,.48),0,.94),'Ochre':((.60,.27,.045),0,.46),'Wood':((.28,.13,.055),0,.57),'Floor':((.28,.28,.235),0,.8),'Paper':((.77,.7,.50),0,.95),'Light':((.95,.76,.43),0,.35),'Blue':((.025,.20,.48),0,.38)}
mats={}
# Original packed micro-normal/roughness tiles. Broad color planes remain quiet.
for kind in ('Weave','Coat'):
 size=256;im=bpy.data.images.new('T_Bedroom_'+kind+'_Normal',width=size,height=size);pix=[]
 for y in range(size):
  for x in range(size):
   a=.07*math.sin(x*math.pi/2) if kind=='Weave' else .012*math.sin(x*1.31+y*.74)
   b=.07*math.sin(y*math.pi/2) if kind=='Weave' else .012*math.cos(y*1.12-x*.55)
   pix.extend((.5+a,.5+b,1,1))
 im.pixels=pix;im.colorspace_settings.name='Non-Color';im.filepath_raw=str(O/(im.name+'.png'));im.file_format='PNG';im.save();im.pack()
for n,(c,metal,rough) in palette.items():
 m=bpy.data.materials.new('M_Bedroom_'+n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if n in ('Teal','Linen','Ivory','Green'):
  uv=m.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='Meters';t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images['T_Bedroom_'+('Weave' if n in ('Teal','Linen') else 'Coat')+'_Normal'];normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35
  m.node_tree.links.new(uv.outputs['UV'],t.inputs['Vector']);m.node_tree.links.new(t.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
 if n=='Light':p.inputs['Emission Color'].default_value=(1,.78,.44,1);p.inputs['Emission Strength'].default_value=3
 mats[n]=m
collections={}
def category(n):
 if n not in collections:
  c=bpy.data.collections.new(n);S.collection.children.link(c);collections[n]=c
 return collections[n]
def move(o,group):
 for c in list(o.users_collection):c.objects.unlink(o)
 category(group).objects.link(o);return o
def box(n,p,d,mat,bevel=.015,group='Furniture'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Manufactured chamfer','BEVEL');mod.width=min(bevel,min(d)*.3);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mats[mat]);return move(o,group)
def cyl(n,p,r,h,mat,axis='z',group='Details'):
 rot={'z':(0,0,0),'x':(0,math.pi/2,0),'y':(math.pi/2,0,0)}[axis];bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=h,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(mats[mat]);return move(o,group)
def text(n,body,p,size=.065,mat='Paper'):
 bpy.ops.object.text_add(location=p,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=n;o.data.body=body;o.data.size=size;o.data.extrude=.0004;o.data.materials.append(mats[mat]);bpy.ops.object.convert(target='MESH');return move(bpy.context.object,'Signs')
# Real shell: 4.4 x 4.6 m clear interior, 2.8 m height, 1.2 m entrance.
for x in range(6):
 for y in range(7):box('Floor tile',((x+.5)*4.4/6,(y+.5)*5.2/7-.6,-.055),(4.4/6-.009,5.2/7-.009,.11),'Floor',.007,'Architecture')
box('Entry apron',(2.8,-1.05,-.07),(1.8,1,.14),'Floor',.005,'Architecture')
for side in ('back','left','right'):
 length=4.4 if side=='back' else 4.6;count=4
 for i in range(count):
  along=(i+.5)*length/count
  for z,h,mat in ((.50,1,'Green'),(1.88,1.76,'Ivory')):
   p=(along,4.65,z) if side=='back' else ((-.05 if side=='left' else 4.45),along,z)
   d=(length/count-.012,.10,h-.012) if side=='back' else (.10,length/count-.012,h-.012)
   box('Wall panel '+side,p,d,mat,.012,'Architecture')
 for z,h in ((.07,.14),(1.02,.045),(2.73,.14)):
  p=(2.2,4.58,z) if side=='back' else ((.02 if side=='left' else 4.38),2.3,z)
  d=(4.4,.07,h) if side=='back' else (.07,4.6,h)
  box('Wall band '+side,p,d,'Graphite',.01,'Architecture')
for a,b in ((0,2.25),(3.45,4.4)):
 box('Front wall',((a+b)/2,-.05,1.4),(b-a,.1,2.8),'Ivory',.012,'Architecture')
box('Door header',(2.85,-.05,2.55),(1.2,.1,.5),'Green',.015,'Architecture')
for x in (2.23,3.47):box('Entry jamb',(x,0,1.15),(.12,.22,2.3),'Graphite',.025,'Architecture')
box('Entry lintel',(2.85,0,2.28),(1.36,.22,.14),'Graphite',.025,'Architecture')
box('Ceiling',(2.2,2.3,2.86),(4.6,4.8,.12),'Ivory',.008,'Ceiling')
for y in (.65,2.3,3.95):box('Ceiling structural rib',(2.2,y,2.73),(4.4,.12,.18),'Graphite',.018,'Ceiling')
for x in (.07,4.33):
 for y in (.1,2.3,4.5):box('Structural pier',(x,y,1.4),(.14,.18,2.8),'Graphite',.018,'Architecture')
# Bed uses one isolated group so it can become the existing native Bed actor.
bx,by=1.17,3.14
for x in (bx-.43,bx+.43):
 for y in (by-.87,by+.87):box('Bed foot',(x,y,.135),(.115,.13,.27),'Graphite',.025,'Bed')
box('Bed chassis',(bx,by,.30),(1.11,2.18,.20),'Graphite',.045,'Bed')
box('Mattress lower',(bx,by,.435),(1.01,2.03,.19),'Linen',.06,'Bed')
box('Headboard',(bx,by+1.03,.61),(1.15,.12,.85),'Graphite',.05,'Bed')
box('Head insert',(bx,by+.955,.76),(.94,.05,.38),'Green',.025,'Bed')
box('Footboard',(bx,by-1.03,.41),(1.15,.12,.48),'Graphite',.035,'Bed')
box('Pillow',(bx,by+.69,.585),(.76,.40,.145),'Linen',.065,'Bed')
# Shaped blanket with few folds, not stacked rigid slabs.
verts=[];faces=[];nx,ny=16,24
for j in range(ny+1):
 y=by-.97+j/ny*1.48
 for i in range(nx+1):
  x=bx-.55+i/nx*1.10;edge=max(0,abs(x-bx)-.45)
  z=.555-edge*1.9+.012*math.sin(j*.65+i*.33)+.008*math.sin(i*.9)
  verts.append((x,y,z))
for j in range(ny):
 for i in range(nx):a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
me=bpy.data.meshes.new('Blanket shaped surface');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Blanket',me);category('Bed').objects.link(o);o.data.materials.append(mats['Teal']);md=o.modifiers.new('Fabric thickness','SOLIDIFY');md.thickness=.013;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=md.name)
for f in o.data.polygons:f.use_smooth=True
# Desk and wall shelf, enough thickness and joinery to read as furniture.
box('Desktop',(.43,1.92,.77),(.72,1.48,.065),'Wood',.025)
for y in (1.29,2.56):box('Desk trestle',(.43,y,.36),(.58,.07,.72),'Graphite',.018)
box('Desk rear stretcher',(.16,1.92,.31),(.07,1.35,.07),'Green',.014)
for z in (1.65,2.03):
 box('Floating shelf',(.28,1.95,z),(.50,1.46,.055),'Ochre',.012)
 for y in (1.36,2.54):box('Shelf bracket',(.08,y,z-.09),(.10,.045,.18),'Graphite',.008)
box('Monitor case',(.29,1.96,1.12),(.12,.70,.43),'Graphite',.025)
box('Monitor glass',(.36,1.96,1.12),(.008,.61,.34),'Green',.006)
box('Monitor base',(.44,1.96,.82),(.28,.35,.035),'Graphite',.01)
box('Monitor stand',(.29,1.96,.875),(.05,.09,.14),'Graphite',.01)
box('Keyboard',(.64,1.96,.817),(.19,.56,.035),'Rubber',.008)
for i in range(7):box('Keyboard key',(.68,1.74+i*.068,.84),(.06,.048,.014),'Ivory',.003,'Details')
box('Stool seat',(1.04,1.51,.46),(.48,.48,.08),'Green',.035)
for x in (.86,1.22):
 for y in (1.33,1.69):box('Stool leg',(x,y,.22),(.045,.045,.44),'Graphite',.008)
for i in range(3):
 box('Notebook',(.29,1.56+i*.30,1.71),(.30,.20,.055),'Green' if i%2 else 'Ivory',.008,'Details')
box('Storage chest',(.48,.55,.26),(.72,.49,.49),'Ochre',.035)
box('Chest lid',(.48,.55,.52),(.76,.53,.09),'Graphite',.025)
for x in (.21,.75):box('Chest latch',(x,.282,.45),(.07,.025,.13),'Steel',.01,'Details')
# Native-style storage study has actual open shelves, no inventory props promised.
box('Locker back',(3.81,4.40,1.12),(.90,.055,2.15),'Green',.018)
for x in (3.36,4.26):box('Locker side',(x,4.12,1.12),(.055,.62,2.15),'Green',.018)
for z in (.10,.65,1.20,1.75,2.18):box('Locker shelf',(3.81,4.12,z),(.88,.61,.04),'Graphite',.01)
for i,(x,y) in enumerate(((3.40,3.88),(3.40,4.35),(4.22,3.88),(4.22,4.35))):box('Locker foot_'+str(i),(x,y,.04),(.08,.08,.08),'Rubber',.01)
for z in (.2,.75):
 box('Personal box',(3.82,4.15,z+.065),(.61,.43,.29),'Ivory',.025,'Details');box('Label',(3.82,3.924,z+.085),(.22,.007,.08),'Green',.002,'Details')
box('Rolled linen',(3.82,4.14,1.32),(.55,.40,.20),'Teal',.035,'Details')
box('Bedside cabinet',(2.12,3.98,.34),(.48,.49,.68),'Green',.025)
box('Bedside top',(2.12,3.98,.70),(.52,.53,.055),'Wood',.015)
box('Drawer',(2.12,3.719,.49),(.39,.018,.22),'Ivory',.01,'Details')
box('Pull',(2.12,3.69,.51),(.15,.035,.03),'Graphite',.008,'Details')
cyl('Water bottle',(2.12,3.98,.86),.043,.25,'Blue');cyl('Bottle cap',(2.12,3.98,1.0),.032,.04,'Graphite')
# Original civil-defence signage, small belongings and pipework.
box('Wall notice frame',(2.70,4.565,1.89),(1.0,.045,.57),'Graphite',.025,'Signs');box('Wall notice face',(2.70,4.536,1.89),(.92,.018,.49),'Paper',.008,'Signs')
text('Notice heading','DEFESA CIVIL',(2.30,4.522,2.015),.085,'Green');text('Notice line','ABRIGO 13  /  SANTA AURORA',(2.30,4.52,1.88),.043,'Green');text('Notice foot','DESCANSAR TAMBEM E RESISTIR',(2.30,4.52,1.76),.035,'Green')
cyl('Vent pipe',(.21,4.31,1.44),.075,2.62,'Green')
for z in (.35,1.30,2.3):cyl('Pipe collar',(.21,4.31,z),.09,.08,'Graphite')
box('Vent grille',(3.56,4.545,2.49),(.58,.04,.22),'Graphite',.014,'Details')
for x in range(7):box('Grille fin',(3.32+x*.078,4.513,2.49),(.025,.022,.16),'Steel',.003,'Details')
for i,(p,d) in enumerate([((1.35,4.53,2.48),(1.5,.13,.13)),((.1,1.95,2.4),(.13,1.4,.13)),((3.4,.9,2.65),(1.0,.18,.12))]):
 box('Lamp housing',p,d,'Graphite',.025,'Fixtures');emit=box('Lamp diffuser',(p[0],p[1]-.025 if i==0 else p[1],p[2]-.04),(d[0]*.90,d[1]*.8,d[2]*.75),'Light',.018,'Fixtures')
def lamp(n,p,energy,color,size,target):
 data=bpy.data.lights.new(n,'AREA');data.energy=energy;data.color=color;data.shape='DISK';data.size=size;o=bpy.data.objects.new(n,data);category('PreviewLights').objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
lamp('Warm bedside',(1.4,4.3,2.42),140,(1,.80,.58),1.1,(1.4,2.7,.7));lamp('Desk practical',(.35,2.0,2.3),100,(1,.85,.68),1,(1.6,2.0,.7));lamp('Ceiling practical',(3.1,1.4,2.62),170,(1,.91,.77),1.4,(2.4,2.3,.1))
# UVs and separate authored collections exported as modular grouped meshes.
manifest={}
for group,c in collections.items():
 obs=[o for o in c.objects if o.type=='MESH']
 if not obs:continue
 for o in obs:
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');uv=o.data.uv_layers.new(name='Meters')
  for face in o.data.polygons:
   ax=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=ax]
   for li in face.loop_indices:
    co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
  o.select_set(False)
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 key='SM_Bedroom_'+group
 if group=='Bed':
  for o in obs:o.location.x-=bx;o.location.y-=by
 bpy.ops.export_scene.fbx(filepath=str(O/(key+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False)
 if group=='Bed':
  for o in obs:o.location.x+=bx;o.location.y+=by
 manifest[key]={'objects':len(obs),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs),'materials':sorted({m.name for o in obs for m in o.data.materials})}
def camera(n,p,target,lens=24):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return o
S.camera=camera('CAM_Perspective',(3.87,.68,1.67),(1.6,3.45,1.25),23)
top=camera('CAM_Top',(2.2,2.3,8),(2.2,2.3,0));top.data.type='ORTHO';top.data.ortho_scale=7.8
S.world.color=(.12,.12,.12);S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True;S.render.resolution_x=1280;S.render.resolution_y=960;S.render.resolution_percentage=100
S['scope']='Original bedroom style study, not replacement bunker; shelf contents are decorative.'
S['contact_correction_v1']=True
S['dimensions_m']=[4.4,4.6,2.8];S['entrance_clear_width_m']=1.2
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bedroom_StyleStudy_v001.blend'))
(O/'manifest.json').write_text(json.dumps({'palette':palette,'meshes':manifest},indent=2))
report={'objects':sum(x['objects'] for x in manifest.values()),'triangles':sum(x['triangles'] for x in manifest.values()),'uv_layers_min':min(len(o.data.uv_layers) for o in S.objects if o.type=='MESH'),'dimensions_m':[4.4,4.6,2.8],'entry_m':1.2,'packed_images':len([i for i in bpy.data.images if i.packed_file])};(R/'logs/bedroom_blender.json').write_text(json.dumps(report,indent=2))
S.render.filepath=str(R/'screenshots/bedroom_blender.png');bpy.ops.render.render(write_still=True)
collections['Ceiling'].hide_render=True;S.camera=top;S.render.filepath=str(R/'screenshots/bedroom_top.png');bpy.ops.render.render(write_still=True)
print('C13_BEDROOM_SOURCE_OK',json.dumps(report))
