"""Editable, meter-scale reference kit. No inventory units are authored as decor."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'exports/reference_room';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
mats={}
# PBR values are linear reflectance, not display RGB. Wear is restrained.
for name,color,metal,rough in [('Concrete',(.25,.265,.26),0,.88),('Paint',(.105,.17,.145),0,.42),('Steel',(.17,.19,.20),1,.3),('Rubber',(.014,.018,.019),0,.84),('Fabric',(.12,.17,.155),0,.9),('Wood',(.26,.14,.065),0,.48),('Ivory',(.58,.52,.40),0,.48),('Paper',(.67,.61,.46),0,.95),('Amber',(.75,.35,.055),0,.3),('Light',(.9,.66,.35),0,.22)]:
 m=bpy.data.materials.new('M_Ref_'+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value={'Concrete':65,'Fabric':650,'Wood':12}.get(name,140);noise.inputs['Roughness'].default_value=.7
 bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.0007 if name!='Concrete' else .002;m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal']);mats[name]=m
parts=[];assets={}
def box(n,loc,size,mat,bevel=.005):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  md=o.modifiers.new('Manufactured edge radius','BEVEL');md.width=min(bevel,min(size)*.32);md.segments=3;bpy.ops.object.modifier_apply(modifier=md.name)
 o.data.materials.append(mats[mat]);parts.append(o);return o
def cyl(n,loc,r,depth,mat,rot=(0,0,0),verts=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(mats[mat]);parts.append(o)
 md=o.modifiers.new('Edge','BEVEL');md.width=.0015;md.segments=2;bpy.ops.object.modifier_apply(modifier=md.name)
 for f in o.data.polygons:f.use_smooth=True
 return o
def finish(n):
 global parts
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=n;scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 # Second UV stores physical tiling in meters, independent of atlas packing.
 uv=o.data.uv_layers.new(name='PhysicalMeters')
 for p in o.data.polygons:
  norm=p.normal;ax=max(range(3),key=lambda a:abs(norm[a]));axes=[a for a in range(3) if a!=ax]
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 bpy.ops.export_scene.fbx(filepath=str(OUT/(n+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False)
 assets[n]={'dimensions_m':list(o.dimensions),'polygons':len(o.data.polygons),'materials':[m.name for m in o.data.materials]};parts=[];return o
# Modular concrete wall panel with actual recessed seams and formwork ties.
box('Concrete slab',(0,.035,1.45),(1.48,.07,2.90),'Concrete',.006)
for x in (-.57,.57):
 for z in (.35,1.45,2.55):cyl('Form tie recess',(x,-.001,z),.011,.004,'Steel',(math.pi/2,0,0))
box('Impact rail',(0,-.025,.80),(1.48,.045,.11),'Paint',.006)
box('Skirting',(0,-.018,.055),(1.48,.035,.11),'Rubber',.004)
finish('SM_Ref_WallPanel')
box('Floor mat slab',(0,0,-.0125),(1,1,.025),'Rubber',.003);finish('SM_Ref_FloorTile')
# Communal table: 74cm height, laminated planks, steel frame, joinery.
for x in (-.80,.80):
 for y in (-.38,.38):
  box('Square tube leg',(x,y,.35),(.045,.045,.69),'Paint');box('Foot cap',(x,y,.025),(.06,.06,.04),'Rubber')
for y in (-.38,.38):box('Apron',(0,y,.66),(1.70,.035,.08),'Steel')
for y in (-.36,-.12,.12,.36):box('Laminated timber plank',(0,y,.723),(2.05,.237,.034),'Wood',.004)
for x in (-.8,.8):
 for y in (-.35,.35):cyl('Countersunk fixing',(x,y,.741),.005,.001,'Steel')
finish('SM_Ref_Table')
# Adult chair: seat45cm, back84cm; independently editable source parts retained via meshes.
for x in (-.205,.205):
 for y in (-.20,.20):
  box('Chair tube',(x,y,.23),(.026,.026,.43),'Steel');box('Chair foot',(x,y,.025),(.035,.035,.04),'Rubber')
box('Seat plywood',(0,0,.445),(.46,.46,.025),'Wood',.015)
box('Seat upholstery',(0,-.005,.47),(.44,.43,.035),'Fabric',.018)
for x in (-.205,.205):box('Back support',(x,.19,.64),(.026,.026,.40),'Steel')
box('Curved back',(0,.205,.73),(.46,.045,.24),'Wood',.025);finish('SM_Ref_Chair')
# Sofa with seams, frame, arms and separate cushions, no solid cube silhouette.
for x in (-1.02,1.02):
 for y in (-.28,.28):box('Sofa steel leg',(x,y,.10),(.04,.04,.19),'Steel')
box('Sofa lower frame',(0,0,.24),(2.4,.82,.20),'Paint',.018)
box('Sofa back',(0,.30,.68),(2.40,.20,.78),'Fabric',.045)
for x in (-1.10,1.10):box('Padded arm',(x,0,.56),(.20,.82,.42),'Fabric',.045)
for x in (-.66,0,.66):
 box('Seat cushion',(x,-.045,.47),(.645,.65,.18),'Fabric',.045)
 box('Back cushion',(x,.19,.76),(.64,.16,.48),'Fabric',.04)
 for xx in (-.29,.29):box('Upholstery piping',(x+xx,-.047,.56),(.004,.57,.004),'Ivory',.001)
finish('SM_Ref_Sofa')
# Physically openable steel cabinet. Body and leaf share meter scale, distinct pivots.
box('Cabinet back',(0,.255,1.0),(1.2,.018,1.9),'Paint',.002)
for x in (-.59,.59):box('Folded side',(x,0,1.0),(.02,.53,1.9),'Paint',.002)
for z in (.05,.50,.95,1.40,1.95):
 box('Shelf',(0,0,z),(1.18,.53,.022),'Paint',.002)
 box('Folded shelf lip',(0,-.257,z-.015),(1.14,.015,.04),'Paint',.002)
for x in (-.48,.48):
 for y in (-.18,.18):box('Cabinet foot',(x,y,.025),(.06,.06,.05),'Rubber')
for x in (-.55,.55):
 for z in (.2,1.0,1.8):cyl('Body rivet',(x,-.272,z),.004,.004,'Steel',(math.pi/2,0,0))
finish('SM_Ref_CabinetBody')
# Leaf origin at hinge; UE local X runs 0..112cm. Front is Blender -Y / Unreal +Y.
box('Folded leaf',(.56,-.012,1.0),(1.12,.024,1.87),'Paint',.004)
for x in (.025,1.095):box('Door fold',(x,.008,1.0),(.025,.03,1.83),'Steel',.003)
for z in (.24,1.0,1.76):cyl('Hinge barrel',(0,0,z),.013,.085,'Steel')
for z in (1.03,1.17):cyl('Handle mount',(.99,-.043,z),.012,.045,'Steel',(math.pi/2,0,0))
cyl('Pull grip',(.99,-.066,1.10),.012,.14,'Rubber')
for z in (1.58,1.64,1.70):box('Louver shadow',(.55,-.026,z),(.50,.006,.018),'Rubber',.002)
box('Designation plate',(.55,-.028,1.25),(.22,.008,.075),'Ivory',.003)
finish('SM_Ref_CabinetLeaf')
# Fixture, enamel shade with visible emitter and steel guards.
box('Light housing',(0,0,0),(.90,.18,.08),'Paint',.014)
box('Frosted diffuser',(0,0,-.05),(.78,.12,.025),'Light',.012)
for x in (-.32,0,.32):box('Lamp guard',(x,0,-.07),(.012,.17,.025),'Steel')
finish('SM_Ref_Lamp')
# Everyday believable props: mugs, notebooks, folded blanket, civic sign and duct.
for z,r in ((.012,.036),(.09,.035)):
 cyl('Mug base or lip',(0,0,z),r,.008,'Ivory')
cyl('Mug body',(0,0,.05),.035,.08,'Ivory')
bpy.ops.mesh.primitive_torus_add(major_radius=.023,minor_radius=.005,location=(.041,0,.055),rotation=(math.pi/2,0,0));o=bpy.context.object;o.data.materials.append(mats['Ivory']);parts.append(o)
cyl('Dark tea',(0,0,.094),.029,.001,'Wood');finish('SM_Ref_Mug')
box('Book cover',(0,0,.008),(.22,.16,.016),'Paint',.002);box('Paper edges',(0,0,.022),(.208,.148,.013),'Paper',.001);box('Upper cover',(0,0,.032),(.22,.16,.006),'Paint',.001);finish('SM_Ref_Notebook')
for i in range(5):box('Fold of blanket',(0,0,.018+i*.026),(.66-i*.007,.43,.03),'Fabric',.012)
finish('SM_Ref_Blanket')
box('Enamel sign',(0,0,0),(1.1,.018,.24),'Paint',.007)
# True raised typography; UE FBX triangulated as mesh.
bpy.ops.object.text_add(location=(-.49,-.014,-.055),rotation=(math.pi/2,0,0));o=bpy.context.object;o.data.body='ABRIGO 13  /  CONVIVÊNCIA';o.data.size=.065;o.data.extrude=.0007;o.data.materials.append(mats['Ivory']);bpy.ops.object.convert(target='MESH');parts.append(bpy.context.object);finish('SM_Ref_Sign')
box('Duct',(0,0,0),(2,.32,.22),'Steel',.008)
for x in (-.94,.94):
 box('Duct flange',(x,0,0),(.025,.36,.26),'Steel',.003)
 for y in (-.14,.14):cyl('Flange bolt',(x,y,.14),.007,.015,'Steel')
finish('SM_Ref_Duct')
# Source library is staged in separate collections; assembled editable room is a second collection.
lib=bpy.data.collections.new('ASSET_LIBRARY');scene.collection.children.link(lib)
for o in list(scene.objects):
 for c in list(o.users_collection):c.objects.unlink(o)
 lib.objects.link(o);o.hide_render=True;o.hide_set(True)
placements=[('SM_Ref_Sofa',(7.95,4.2,0),90),('SM_Ref_Table',(11.4,3.7,0),0)]
for x in (10.75,12.05):
 for y,yaw in ((3.05,180),(4.35,0)):placements.append(('SM_Ref_Chair',(x,y,0),yaw))
placements.extend([('SM_Ref_CabinetBody',(14.35,1.0,0),180),('SM_Ref_CabinetLeaf',(14.91,1.30,0),180)])
room=bpy.data.collections.new('REFERENCE_ROOM_ASSEMBLY');scene.collection.children.link(room)
for n,loc,yaw in placements:
 o=bpy.data.objects[n].copy();o.data=bpy.data.objects[n].data;room.objects.link(o);o.location=loc;o.rotation_euler[2]=math.radians(-yaw);o.hide_render=False;o.hide_set(False)
scene['scope']='Living room reference only. Cabinet begins empty; decor is not inventory.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Convivencia_Reference_v001.blend'))
(OUT/'manifest.json').write_text(json.dumps(assets,indent=2));print('C13_REFERENCE_KIT_OK',json.dumps(assets))
