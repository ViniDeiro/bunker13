"""Create v002 from the editable v001; export native-sized cabinet and room cleanup."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'exports/bedroom_cabinet';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Bedroom_StyleStudy_v001.blend'))
for o in list(bpy.data.objects):
 if o.name.startswith(('Locker ','Personal box','Label','Rolled linen')):bpy.data.objects.remove(o,do_unlink=True)
groups={}
for n in ('CabinetBody','CabinetLeaf'):
 c=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(c);groups[n]=c
def box(n,p,d,mat,group):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 m=o.modifiers.new('Manufactured edge','BEVEL');m.width=min(.012,min(d)*.22);m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name);o.data.materials.append(bpy.data.materials['M_Bedroom_'+mat])
 for c in list(o.users_collection):c.objects.unlink(o)
 groups[group].objects.link(o);return o
B='CabinetBody';L='CabinetLeaf'
box('Cabinet back',(0,.26,1),(1.2,.02,1.92),'Green',B)
for x in (-.59,.59):box('Cabinet side',(x,0,1),(.02,.54,1.92),'Green',B)
for i in range(5):box('Usable shelf',(0,0,.05+.45*i),(1.18,.54,.024),'Graphite',B)
box('Cabinet crown',(0,0,1.95),(1.2,.54,.05),'Green',B)
for x in (-.53,.53):
 for y in (-.20,.20):box('Cabinet support',(x,y,.02),(.07,.07,.04),'Rubber',B)
# Leaf export origin is the physical hinge; front maps to positive Unreal Y.
box('Hinged door',(.576,0,1),(1.152,.04,1.88),'Ivory',L)
box('Door lower painted panel',(.576,-.025,.47),(1.04,.012,.65),'Green',L)
for z in (.35,1.0,1.65):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.023,depth=.12,location=(0,0,z));o=bpy.context.object;o.name='Visible hinge';o.data.materials.append(bpy.data.materials['M_Bedroom_Steel'])
 for c in list(o.users_collection):c.objects.unlink(o)
 groups[L].objects.link(o)
for z in (.97,1.18):box('Pull mount',(1.035,-.047,z),(.045,.06,.035),'Graphite',L)
box('Door pull',(1.035,-.085,1.075),(.04,.035,.25),'Graphite',L)
for i in range(6):box('Door vent',(.36+i*.085,-.023,1.68),(.055,.008,.018),'Graphite',L)
stats={}
for group in ('Furniture','Details',B,L):
 obs=[o for o in bpy.data.collections[group].objects if o.type=='MESH']
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:
  o.select_set(True);bpy.context.view_layer.objects.active=o
  if len(o.data.uv_layers)<2:
   bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');o.data.uv_layers.new(name='Meters')
   # Planar physical scale for painted surfaces.
   uv=o.data.uv_layers['Meters']
   for f in o.data.polygons:
    normal=f.normal;axis=max(range(3),key=lambda i:abs(normal[i]));a,b=[i for i in range(3) if i!=axis]
    for li in f.loop_indices:
     p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p[a],p[b])
 key='SM_Bedroom_'+group
 bpy.ops.export_scene.fbx(filepath=str(O/(key+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False)
 stats[key]={'objects':len(obs),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs)}
# Place local export pieces in the editable room for inspection.
for o in groups[B].objects:o.location+=__import__('mathutils').Vector((3.73,4.11,0))
for o in groups[L].objects:o.location+=__import__('mathutils').Vector((3.73-.576,4.11-.27,0))
bpy.context.scene['scope']='v002: real cabinet body, shelves, separate hinged leaf; item contents are runtime inventory.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bedroom_StyleStudy_v002.blend'))
(O/'manifest.json').write_text(json.dumps({'meshes':stats,'body_dimensions_cm':[120,54,197.5],'hinge_local_cm':[-57.6,27,0],'location_cm':[373,-411,0],'source':'blender/Bedroom_StyleStudy_v002.blend'},indent=2))
print('C13_BEDROOM_CABINET_SOURCE_OK',flush=True)
