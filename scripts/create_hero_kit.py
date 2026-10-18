"""Build editable, bevelled and UV-unwrapped bunker assets for Painter/UE."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'exports/hero_kit'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
materials={}
for name,color,metal,rough in [('Paint',(.12,.21,.16,1),.55,.6),('Steel',(.055,.075,.08,1),.8,.4),('Fabric',(.23,.29,.22,1),0,.92),('Rubber',(.018,.022,.02,1),0,.9),('Linen',(.59,.57,.46,1),0,.9),('Safety',(.65,.24,.035,1),.2,.6)]:
    m=bpy.data.materials.new('M_Hero_'+name); m.diffuse_color=color; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=color; bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    materials[name]=m
parts=[]
def box(name,loc,size,mat='Steel',bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Manufactured edges','BEVEL'); mod.width=min(bevel,min(size)*.24); mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(materials[mat]); parts.append(o); return o
def cyl(name,loc,r,depth,mat='Steel',rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object;o.name=name;o.data.materials.append(materials[mat]);parts.append(o);return o
def finish(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join();o=bpy.context.object;o.name=name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
    count=sum(len(p.vertices)-2 for p in o.data.polygons)
    uv=o.data.uv_layers.active
    assert uv and all(-.001<=v<=1.001 for d in uv.data for v in d.uv),name+' invalid UV'
    parts.clear();return o,{'name':name,'triangles':count,'dimensions_m':list(o.dimensions),'uv_layer':uv.name}

# Origin on mattress centre matches the current interactable actor.
box('Mattress',(0,0,.01),(1.00,2.00,.19),'Linen',.08)
box('Folded blanket',(0,.32,.117),(.98,1.25,.045),'Fabric',.025)
box('Pillow',(0,-.70,.15),(.70,.39,.12),'Linen',.055)
box('Bed deck',(0,0,-.125),(1.08,2.08,.07))
for x in (-.47,.47):
    for y in (-.91,.91):box('Bed leg',(x,y,-.34),(.055,.055,.43))
for x in (-.53,.53):
    box('Bed side rail',(x,0,-.08),(.035,2.08,.12))
    box('Head upright',(x,-1.03,-.06),(.055,.055,.91))
box('Head panel',(0,-1.03,.17),(1.04,.045,.39),'Paint')
box('Foot rail',(0,1.03,-.01),(1.04,.045,.18),'Paint')
bed,bed_info=finish('SM_Hero_Bed')

box('Locker back',(0,.34,.92),(.52,.035,1.84),'Paint')
for x in (-.25,.25):box('Locker side',(x,0,.92),(.035,.70,1.84),'Paint')
for z in (.035,1.805,.48,1.12):box('Locker shelf',(0,0,z),(.49,.70,.035),'Paint')
box('Door inner shadow',(0,-.357,.94),(.47,.025,1.75),'Rubber')
box('Locker door',(0,-.38,.94),(.45,.035,1.73),'Paint')
for z in (1.48,1.53,1.58,.31,.36,.41):box('Vent slot',(0,-.402,z),(.28,.012,.018),'Rubber',.003)
box('ID plaque',(0,-.405,1.32),(.21,.012,.09),'Linen',.003)
box('Handle',( .16,-.432,1.0),(.027,.045,.16),'Steel',.01)
cyl('Lock',(.16,-.428,.85),.018,.02,'Steel',(math.pi/2,0,0))
for z in (.27,1.61):cyl('Hinge',(-.23,-.40,z),.025,.13)
locker,locker_info=finish('SM_Hero_Locker')

# Door pivots at its hinge, allowing future server-authoritative rotation.
box('Armoured leaf',(.90,0,1.20),(1.80,.16,2.40),'Paint',.035)
box('Inset steel',(.90,-.092,1.20),(1.54,.04,2.12),'Steel')
box('Raised panel',(.90,-.12,1.20),(1.40,.045,1.94),'Paint')
for z in (.30,1.20,2.10):
    cyl('Heavy hinge',(0,0,z),.07,.24)
for x in (.25,1.55):
    for z in (.25,.65,1.75,2.15):cyl('Bolt',(x,-.155,z),.023,.024,'Steel',(math.pi/2,0,0))
cyl('Wheel hub',(1.25,-.22,1.15),.065,.13,'Steel',(math.pi/2,0,0))
bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=(1.25,-.30,1.15),rotation=(math.pi/2,0,0),major_radius=.24,minor_radius=.025)
o=bpy.context.object;o.name='Lock wheel';o.data.materials.append(materials['Safety']);parts.append(o)
for a in (0,math.pi/3,2*math.pi/3):
    o=box('Wheel spoke',(1.25,-.30,1.15),(.48,.025,.025),'Safety',.005);o.rotation_euler.y=a
door,door_info=finish('SM_Hero_BlastDoor')

# Presentation layout only; FBX files above retain asset-local pivots.
bed.location=(-1.25,0,.54);locker.location=(.25,.85,0);door.location=(1.05,.85,0)
box('Presentation floor',(0,0,-.08),(8,6,.1),'Rubber',0);parts.clear()
world=scene.world or bpy.data.worlds.new('World');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.09,.11,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.4
for loc,energy,color,size in [((-3,-4,6),1100,(1,.78,.53),5),((4,1,5),900,(.52,.72,1),4)]:
    d=bpy.data.lights.new('Studio','AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new('Studio',d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('CAM_Kit');o=bpy.data.objects.new('CAM_Kit',d);scene.collection.objects.link(o);o.location=(5,-7,4.2);o.rotation_euler=(Vector((.2,.2,1))-o.location).to_track_quat('-Z','Y').to_euler();d.lens=45;scene.camera=o
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Bunker_HeroKit_v001.blend'))
scene.render.filepath=str(ROOT/'screenshots/hero_kit.png');bpy.ops.render.render(write_still=True)
(ROOT/'logs/hero_kit.json').write_text(json.dumps({'assets':[bed_info,locker_info,door_info],'units':'meters','uv_checked':True,'painter_project_created':False},indent=2))
print('HERO_KIT_OK')
