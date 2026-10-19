"""Editable real-scale C13 item meshes, UV atlases, exports and close-up renders."""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'exports/items';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
parts=[];assets=[];report=[];name=''
# Atlas coordinates below are Blender UV coordinates, origin bottom-left.
zones={'paint':(0,.5),'steel':(.5,.5),'rubber':(0,0),'label':(.5,0)}
def finish_part(o,zone,bevel=0):
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=o.modifiers.new('Manufactured edge radii','BEVEL');m.width=bevel;m.segments=2
        bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    if zone!='label':
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        ox,oy=zones[zone]
        for loop in o.data.uv_layers.active.data:loop.uv=(ox+.02+loop.uv.x*.46,oy+.02+loop.uv.y*.46)
    for f in o.data.polygons:f.use_smooth=len(f.vertices)==4 and o.name.startswith(('Body','Ring','Cap','Rim','Terminal','Neck'))
    parts.append(o);return o
def box(label,loc,size,zone='paint',bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=label;o.dimensions=size
    return finish_part(o,zone,min(bevel,min(size)*.2))
def cyl(label,loc,r,depth,zone='steel',vertices=32,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=label
    return finish_part(o,zone,min(.0008,depth*.15))
def ring(label,loc,r,t,zone='steel',rot=(0,0,0),scale=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,major_radius=r,minor_radius=t,location=loc,rotation=rot)
    o=bpy.context.object;o.name=label
    if scale:o.scale=scale
    return finish_part(o,zone)
def lathe(label,profile,zone='paint',n=40):
    verts=[(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z) for z,r in profile for i in range(n)]
    faces=[]
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
    mesh=bpy.data.meshes.new(label);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(label,mesh);scene.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);return finish_part(o,zone)
def label_patch(width,height,z,r=None,y=None):
    n=40 if r else 1;verts=[]
    for zz in (z,z+height):
        for i in range(n+1):
            t=i/n-.5
            if r:angle=t*width/r;verts.append((r*math.sin(angle),-r*math.cos(angle),zz))
            else:verts.append((t*width,y,zz))
    faces=[(i,i+1,n+2+i,n+1+i) for i in range(n)]
    m=bpy.data.meshes.new('Printed label');m.from_pydata(verts,[],faces);m.uv_layers.new(name='UVMap')
    for poly in m.polygons:
        poly.use_smooth=bool(r)
        for li in poly.loop_indices:
            vi=m.loops[li].vertex_index;u=(vi%(n+1))/n;v=vi//(n+1);m.uv_layers.active.data[li].uv=(.515625+.46875*u,.015625+.46875*v)
    o=bpy.data.objects.new('Original printed label',m);scene.collection.objects.link(o);parts.append(o)
def material(key):
    mat=bpy.data.materials.new('M_Item_'+key);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');samples={}
    for kind in ('BaseColor','ORM','Normal'):
        t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets/items'/f'T_Item_{key}_{kind}.png'));t.image.pack()
        if kind!='BaseColor':t.image.colorspace_settings.name='Non-Color'
        samples[kind]=t
    l.new(samples['BaseColor'].outputs['Color'],bs.inputs['Base Color']);sep=n.new('ShaderNodeSeparateColor');l.new(samples['ORM'].outputs['Color'],sep.inputs[0]);l.new(sep.outputs['Green'],bs.inputs['Roughness']);l.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    sep=n.new('ShaderNodeSeparateColor');l.new(samples['Normal'].outputs['Color'],sep.inputs[0]);inv=n.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;l.new(sep.outputs['Green'],inv.inputs[1]);comb=n.new('ShaderNodeCombineColor');l.new(sep.outputs['Red'],comb.inputs['Red']);l.new(inv.outputs[0],comb.inputs['Green']);l.new(sep.outputs['Blue'],comb.inputs['Blue']);norm=n.new('ShaderNodeNormalMap');l.new(comb.outputs[0],norm.inputs['Color']);l.new(norm.outputs[0],bs.inputs['Normal']);return mat
def finish(key):
    mat=material(key);collection=bpy.data.collections.new('ITEM_'+key);scene.collection.children.link(collection)
    for o in parts:
        o.data.materials.clear();o.data.materials.append(mat)
        for c in list(o.users_collection):c.objects.unlink(o)
        collection.objects.link(o)
    # Preserve separate editable manufacturing parts; export a merged evaluated copy.
    bpy.ops.object.select_all(action='DESELECT');copies=[]
    for o in parts:
        cp=o.copy();cp.data=o.data.copy();scene.collection.objects.link(cp);cp.select_set(True);copies.append(cp)
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_Item_'+key;scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    tri=sum(len(p.vertices)-2 for p in o.data.polygons)
    assert tri<12000,(key,tri)
    assert all(math.isfinite(v) and -.001<=v<=1.001 for loop in o.data.uv_layers.active.data for v in loop.uv)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
    report.append({'name':o.name,'triangles':tri,'dimensions_m':list(o.dimensions),'parts':len(parts),'materials':1,'pivot':'base at Z0','uv_valid':True})
    assets.append(o)
    for part in parts:part.hide_render=True;part.hide_set(True)
    parts.clear()

# Reusable 500 ml emergency drinking-water flask; ribbed body and cap.
lathe('Body bottle',[(0,.024),(.004,.032),(.014,.034),(.145,.034),(.163,.031),(.184,.017),(.198,.014)])
for z in (.022,.032,.139,.150):ring('Ring bottle grip',(0,0,z),.034,.0013,'paint')
cyl('Neck tamper seal',(0,0,.198),.0155,.007,'rubber')
cyl('Cap threaded',(0,0,.207),.017,.015,'paint')
for i in range(24):
    a=i*math.tau/24;box('Cap grip knurl',(.017*math.sin(a),.017*math.cos(a),.207),(.0014,.0014,.012),'paint',.0002)
label_patch(.062,.094,.041,r=.0346);finish('Water')
# Food can with rolled seams, corrugations, inset lid and pull-tab.
lathe('Body preserve',[(0,.039),(.004,.042),(.008,.042),(.115,.042),(.12,.04)],'steel')
for z in (.005,.012,.105,.116):ring('Rim rolled seam',(0,0,z),.042,.0015)
for z in (.027,.035,.086,.094):ring('Ring reinforcing',(0,0,z),.042,.0007)
cyl('Recessed lid',(0,0,.120),.038,.001)
ring('Ring lid stamp',(0,0,.121),.029,.0006)
ring('Ring pull tab',(0,-.006,.124),.011,.002,'steel',scale=(.7,1,1))
cyl('Tab rivet',(0,.007,.123),.003,.003)
label_patch(.105,.074,.023,r=.0435);finish('Food')
# Portable hard-shell medical case: seam, rubber gasket, latches and raised handle.
box('Lower case',(0,0,.061),(.28,.11,.122),'paint',.012)
box('Rubber gasket',(0,0,.125),(.278,.109,.004),'rubber',.001)
box('Upper lid',(0,0,.146),(.28,.11,.038),'paint',.010)
for x in (-.095,.095):
    box('Latch', (x,-.058,.122),(.024,.009,.035),'steel',.002)
    cyl('Back hinge',(x,.054,.124),.006,.038,'steel',rot=(0,math.pi/2,0))
for x in (-.055,.055):box('Handle foot',(x,0,.178),(.018,.021,.035),'steel',.003)
box('Carry handle',(0,0,.197),(.125,.023,.018),'rubber',.005)
label_patch(.12,.10,.018,y=-.0557)
for x in (-.125,.125):
    for z in (.018,.102):cyl('Case fastener',(x,-.056,z),.003,.002,'steel',vertices=12,rot=(math.pi/2,0,0))
finish('Medkit')
# A single D cell; no mystery cuboid representing batteries.
cyl('Body alkaline',(0,0,.0295),.017,.059,'paint')
for z in (.002,.057):ring('Rim cell',(0,0,z),.0165,.0009)
cyl('Negative terminal',(0,0,.0007),.014,.0014)
cyl('Top insulation',(0,0,.059),.0135,.0015,'rubber')
cyl('Terminal positive',(0,0,.061),.005,.003)
label_patch(.050,.048,.006,r=.0174);finish('Battery')
# Adjustable maintenance wrench: open jaws are real extruded geometry.
box('Handle steel',(0,0,.007),(.039,.205,.014),'steel',.004)
box('Grip rubber',(0,-.022,.007),(.034,.132,.016),'rubber',.004)
# Head polygon leaves an open jaw at its top.
poly=[(-.019,.084),(-.037,.108),(-.037,.150),(-.025,.166),(-.018,.166),(-.018,.130),(.012,.130),(.012,.163),(.027,.163),(.039,.147),(.035,.108),(.019,.084)]
verts=[(x,y,z) for z in (0,.016) for x,y in poly];n=len(poly)
faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
m=bpy.data.meshes.new('Forged open jaw');m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('Forged open jaw',m);scene.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);finish_part(o,'steel',.0015)
cyl('Adjustment worm',(0,.108,.018),.006,.025,'steel',rot=(0,math.pi/2,0))
for x in (-.010,-.006,-.002,.002,.006,.010):ring('Ring worm gear',(x,.108,.018),.006,.0008,'steel',rot=(0,math.pi/2,0))
# Put a printed asset tag along the broad face of the handle.
label_patch(.024,.062,.02,y=-.030)
# Rotate all parts to lie on the ground with a base origin, preserving 28 cm length.
# Tool is authored flat already; the vertical tag above is removed in favor of a horizontal one.
parts.pop().name='Unused tag';bpy.data.objects.remove(bpy.data.objects['Unused tag'],do_unlink=True)
label_patch(.026,.075,0,y=0)
tag=parts[-1];tag.rotation_euler.x=-math.pi/2;tag.location=(0,-.055,.0161)
finish('Tool')

world=scene.world or bpy.data.worlds.new('World');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.085,.09,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
for loc,energy,color,size in [((-.7,-1,1.4),75,(1,.84,.63),1),((.6,.4,.9),60,(.60,.78,1),.7)]:
    d=bpy.data.lights.new('Studio','AREA');d.energy=energy;d.color=color;d.size=size;o=bpy.data.objects.new('Studio',d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.08))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('CAM_Item');cam=bpy.data.objects.new('CAM_Item',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO'
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
# Individually frame each item at its actual authored size.
for i,o in enumerate(assets):
    for other in assets:other.hide_render=other!=o
    bounds=[o.matrix_world@Vector(v) for v in o.bound_box];center=sum(bounds,Vector())/8;dim=max(o.dimensions)
    cam.location=center+Vector((dim*.95,-dim*1.7,dim*.85));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=dim*1.55
    scene.render.filepath=str(ROOT/'screenshots'/('item_'+report[i]['name'].removeprefix('SM_Item_')+'.png'));bpy.ops.render.render(write_still=True)
# Shared presentation camera and per-item sources in one editable master.
for i,o in enumerate(assets):o.hide_render=False;o.location.x=(i-2)*.25
cam.location=(.60,-1.3,.72);cam.rotation_euler=(Vector((0,0,.09))-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=1.55
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.filepath=str(ROOT/'screenshots/item_kit.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Bunker_Items_v001.blend'));bpy.ops.render.render(write_still=True)
(ROOT/'logs/item_kit.json').write_text(json.dumps({'assets':report,'units':'meters','textured':True,'texture_sets':5,'textures_per_set':3,'editable_parts_preserved':True},indent=2))
print('ITEM_KIT_OK')
