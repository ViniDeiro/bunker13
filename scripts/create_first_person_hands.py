"""C13 low-cost gloved hands and utensils; editable parts, authored grip, real scale."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'exports/hands';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
mats={}
for key,color,rough,metal in [('Glove',(.10,.15,.12,1),.85,0),('Reinforcement',(.035,.045,.038,1),.72,0),('Cuff',(.27,.31,.23,1),.92,0),('Stitch',(.48,.47,.34,1),.8,0),('Steel',(.34,.39,.38,1),.32,.85),('Gauze',(.72,.69,.55,1),.98,0)]:
 m=bpy.data.materials.new('M_Hands_'+key);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=210
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0003;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal']);mats[key]=m
parts=[];report=[];models=[]
def finish_part(o,key):
 bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 o.data.materials.append(mats[key]);parts.append(o)
 return o
def box(name,loc,size,key,bevel=.004):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=min(bevel,min(size)*.25);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish_part(o,key)
def ellipsoid(name,loc,size,key):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=size
 for p in o.data.polygons:p.use_smooth=True
 return finish_part(o,key)
def segment(name,a,b,r,key):
 a=Vector(a);b=Vector(b);o=ellipsoid(name,(a+b)/2,(r,r,(b-a).length/2+r*.35),key);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def finish(name):
 col=bpy.data.collections.new('EDIT_'+name);s.collection.children.link(col)
 for o in parts:
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o)
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in parts:
  cp=o.copy();cp.data=o.data.copy();s.collection.objects.link(cp);cp.select_set(True);copies.append(cp)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
 report.append({'name':name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'parts':len(parts),'dimensions_m':list(o.dimensions),'rig':'Rigid grip pose; runtime procedural transforms, no finger skeleton'})
 for p in parts:p.hide_render=True;p.hide_set(True)
 parts.clear();models.append(o);return o
for hand,mirror in [('Left',1),('Right',-1)]:
 def p(x,y,z):return (x*mirror,y,z)
 box('Sleeve',p(0,.025,0),(.075,.075,.042),'Cuff',.009)
 box('Cuff closure',p(0,.064,.015),(.077,.020,.024),'Reinforcement')
 ellipsoid('Palm',p(0,.113,0),(.043,.052,.026),'Glove')
 box('Back reinforcement',p(0,.114,.024),(.061,.056,.008),'Reinforcement')
 for i,(x,length) in enumerate([(-.031,.045),(-.011,.054),(.011,.056),(.031,.047)]):
  y=.145+(1-abs(x)/.05)*.014
  a=p(x,y,.002);b=p(x,y+length*.55,-.005);c=p(x,y+length*.73,-.029);d=p(x,y+length*.48,-.043)
  for j,(u,v) in enumerate([(a,b),(b,c),(c,d)]):segment(f'Finger_{i}_joint_{j}',u,v,.009 if i!=0 else .008,'Glove')
  box('Knuckle pad',p(x,y+.009,.012),(.015,.019,.008),'Reinforcement',.002)
  segment('Seam',p(x-.004,y,.018),p(x-.004,y+.017,.017),.0007,'Stitch')
 segment('Thumb base',p(.034,.104,-.002),p(.057,.133,-.006),.015,'Glove')
 segment('Thumb grip',p(.057,.133,-.006),p(.046,.157,-.024),.011,'Glove')
 box('C13 wrist patch',p(0,.035,.024),(.035,.022,.003),'Stitch',.001)
 finish('SM_Hands_'+hand)
# Spoon points along +Y; bandage roll along Z.
box('Spoon handle',(0,.058,0),(.012,.12,.003),'Steel',.001)
ellipsoid('Spoon bowl',(0,.132,.001),(.020,.029,.004),'Steel');finish('SM_Hands_Spoon')
bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=12,major_radius=.022,minor_radius=.009);o=bpy.context.object;o.name='Bandage roll';o.scale.z=1.4;finish_part(o,'Gauze')
box('Bandage tail',(0,.028,-.002),(.035,.045,.002),'Gauze',.0004);finish('SM_Hands_Bandage')
for i,o in enumerate(models):o.location=(i*.21,0,0)
world=s.world or bpy.data.worlds.new('World');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[1].default_value=.4
for pos,energy,size in [((.2,-.4,.9),70,.8),((.7,.5,.6),45,.6)]:
 d=bpy.data.lights.new('Studio','AREA');d.energy=energy;d.size=size;o=bpy.data.objects.new('Studio',d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((.3,.1,0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('CAM_Hands');cam=bpy.data.objects.new('CAM_Hands',d);s.collection.objects.link(cam);cam.location=(.5,-.65,.65);cam.rotation_euler=(Vector((.3,.1,0))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=.95;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Bunker_Hands_v001.blend'));s.render.filepath=str(ROOT/'screenshots/hands_kit.png');bpy.ops.render.render(write_still=True)
(ROOT/'logs/hands_blender.json').write_text(json.dumps({'assets':report,'units':'meters','editable_sources':True,'materials':'Authored procedural preview; UE material import is separate'},indent=2));print('C13_HANDS_OK')
