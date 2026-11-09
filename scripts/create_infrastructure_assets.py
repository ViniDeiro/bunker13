import bpy,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
mats={}
for name,col,metal,rough in [('Paint',(.22,.29,.22),.45,.42),('Steel',(.32,.36,.38),.85,.3),('Rubber',(.025,.03,.035),0,.75),('Fuel',(.55,.32,.055),.45,.4),('Filter',(.63,.65,.58),.25,.55)]:
 m=bpy.data.materials.new('M_Infra_'+name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;mats[name]=m
for name,target in [('Paint','Paint'),('Steel','Steel'),('Rubber','Rubber'),('Fuel','Amber'),('Filter','Ivory')]:
 m=mats[name];nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF');uv=nodes.new('ShaderNodeUVMap');uv.uv_map='PhysicalMeters'
 for kind in ('BaseColor','Normal','ORM'):
  t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'assets/reference_room'/f'T_Ref_{target}_{kind}.png'),check_existing=True);t.image.pack();links.new(uv.outputs['UV'],t.inputs['Vector'])
  if kind=='BaseColor':links.new(t.outputs['Color'],p.inputs['Base Color'])
  else:
   t.image.colorspace_settings.name='Non-Color'
   if kind=='Normal':n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.25;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],p.inputs['Normal'])
   else:n=nodes.new('ShaderNodeSeparateColor');links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Green'],p.inputs['Roughness']);links.new(n.outputs['Blue'],p.inputs['Metallic'])
parts=[];rows={}
def box(n,p,d,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[m]);b=o.modifiers.new('Manufactured edges','BEVEL');b.width=.004;b.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name);parts.append(o);return o
def cyl(n,p,r,depth,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(mats[m]);parts.append(o);return o
def label(t,p,size):
 bpy.ops.object.text_add(location=p,rotation=(math.pi/2,0,0));o=bpy.context.object;o.data.body=t;o.data.size=size;o.data.extrude=.0004;o.data.materials.append(mats['Steel']);bpy.ops.object.convert(target='MESH');parts.append(bpy.context.object)
def finish(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 uv=o.data.uv_layers.new(name='PhysicalMeters')
 for poly in o.data.polygons:
  axis=max(range(3),key=lambda a:abs(poly.normal[a]));axes=[a for a in range(3) if a!=axis]
  for li in poly.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 bpy.ops.export_scene.fbx(filepath=str(R/'exports/infrastructure'/f'{name}.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,mesh_smooth_type='FACE');rows[name]={'dimensions_m':list(o.dimensions),'vertices':len(o.data.vertices),'uv':len(o.data.uv_layers),'finite':all(math.isfinite(x) for v in o.data.vertices for x in v.co)};o.location.x=len(rows)*2;parts.clear()
box('Can body',(0,0,.15),(.22,.12,.30),'Fuel');box('Shoulder',(0,0,.31),(.19,.10,.04),'Fuel')
for x in (-.07,.07):box('Handle uprights',(x,0,.36),(.025,.025,.08),'Paint')
box('Handle grip',(0,0,.4),(.165,.025,.025),'Paint');cyl('Sealed cap',(.07,0,.345),.024,.025,'Rubber');label('2 L',(-.06,-.061,.16),.035)
for z in (.07,.23):box('Stamped rib',(0,-.064,z),(.16,.006,.012),'Fuel')
finish('SM_Infra_FuelCan')
box('Parts box',(0,0,.055),(.24,.16,.11),'Paint');box('Lid',(0,0,.115),(.25,.17,.018),'Steel')
for x in (-.075,.075):box('Latch',(x,-.087,.10),(.025,.012,.045),'Rubber')
for x in (-.04,0,.04):cyl('Spare fasteners',(x,0,.135),.009,.02,'Steel')
label('SERVICE',(-.09,-.082,.05),.022);finish('SM_Infra_RepairParts')
cyl('Cartridge',(0,0,.13),.055,.24,'Filter')
for z in (.025,.235):cyl('Seal band',(0,0,z),.058,.025,'Paint')
cyl('Inlet',(0,0,.265),.018,.04,'Steel');finish('SM_Infra_Filter')
box('Control plate',(0,0,0),(.16,.025,.2),'Paint');box('Switch lever',(0,-.035,0),(.035,.05,.06),'Rubber');cyl('Indicator',(.05,-.018,.065),.012,.008,'Steel',(math.pi/2,0,0));finish('SM_Infra_Control')
box('Treatment housing',(0,0,.65),(.55,.2,.60),'Paint');cyl('Filter bowl',(-.16,-.15,.65),.065,.36,'Filter');cyl('Pipe',(-.16,-.15,.9),.018,.18,'Steel');cyl('Outlet',(.15,-.19,.48),.018,.18,'Steel',(math.pi/2,0,0));box('Basin',(.12,-.23,.27),(.3,.25,.035),'Steel')
for x in (-.04,.28):box('Basin rim',(x,-.23,.30),(.02,.25,.06),'Steel')
for x in (-.22,.22):box('Station legs',(x,0,.17),(.035,.10,.34),'Steel')
label('AGUA / FILTRO',(-.22,-.102,.81),.027);finish('SM_Infra_WaterStation')
box('Service backboard',(0,0,1.25),(1.2,.04,.7),'Paint')
for x in (-.48,.48):box('Stand support',(x,0,.48),(.045,.045,.96),'Steel');box('Stand foot',(x,0,.025),(.15,.20,.05),'Steel')
for row,names in enumerate((('COMB.','REPARO','ESTADO'),('GERADOR','LUZ','SERV.'))):
 for j,n in enumerate(names):label(n,(-.54+j*.4,-.026,1.0+row*.35),.025)
finish('SM_Infra_ServiceStand')
box('Emergency housing',(0,0,0),(.22,.12,.08),'Paint');box('Emergency lens',(0,-.065,0),(.17,.02,.045),'Filter');cyl('Ceiling suspension',(0,0,.27),.008,.5,'Steel');finish('SM_Infra_Emergency')
sc['scope']='Infrastructure props only. Existing approved environment remains unchanged.';bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bunker_Infrastructure_v001.blend'));(R/'logs/infra_assets.json').write_text(json.dumps(rows,indent=2));assert all(v['finite'] and v['uv'] for v in rows.values());print('INFRA_ASSETS_OK')
