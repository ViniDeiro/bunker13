"""An actual Unreal map: geometry, camera, real PBR surfaces, lights and a native UMG menu."""
import unreal as u, json, math
from pathlib import Path
R=Path(__file__).resolve().parents[1];D='/Game/Bunker/MainMenu'
a=u.EditorAssetLibrary;tools=u.AssetToolsHelpers.get_asset_tools()
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
a.make_directory(D)
audio=u.AssetImportTask();audio.filename=str(R/'assets/main_menu/S_Menu_Hum.wav');audio.destination_path=D;audio.automated=True;audio.save=True;audio.replace_existing=True;tools.import_asset_tasks([audio])
radio=u.AssetImportTask();radio.filename=str(R/'assets/main_menu/S_Menu_Radio.wav');radio.destination_path=D;radio.automated=True;radio.save=True;radio.replace_existing=True;tools.import_asset_tasks([radio])
hum=u.load_asset(D+'/S_Menu_Hum');hum.set_editor_property('looping',True);a.save_loaded_asset(hum)

if a.does_asset_exist(D+'/L_MainMenu'):
 assert levels.load_level(D+'/L_MainMenu')
 for actor in actors.get_all_level_actors():
  if actor.get_actor_label().startswith('Menu_'):actors.destroy_actor(actor)
else:assert levels.new_level(D+'/L_MainMenu')
task=u.AssetImportTask();task.filename=str(R/'exports/main_menu/SM_Menu_Respirator.fbx');task.destination_path=D;task.automated=True;task.save=True;task.replace_existing=True
opt=u.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;task.options=opt
tools.import_asset_tasks([task])
lamp_task=u.AssetImportTask();lamp_task.filename=str(R/'exports/main_menu/SM_Menu_DeskLamp.fbx');lamp_task.destination_path=D;lamp_task.automated=True;lamp_task.save=True;lamp_task.replace_existing=True;lamp_task.options=opt
tools.import_asset_tasks([lamp_task])
pipe_task=u.AssetImportTask();pipe_task.filename=str(R/'exports/main_menu/SM_Menu_Pipe.fbx');pipe_task.destination_path=D;pipe_task.automated=True;pipe_task.save=True;pipe_task.replace_existing=True;pipe_task.options=opt;tools.import_asset_tasks([pipe_task])

fan_task=u.AssetImportTask();fan_task.filename=str(R/'exports/main_menu/SM_Menu_Fan.fbx');fan_task.destination_path=D;fan_task.automated=True;fan_task.save=True;fan_task.replace_existing=True;fan_task.options=opt;tools.import_asset_tasks([fan_task])
mats={k:u.load_asset('/Game/Bunker/ReferenceRoom/Materials/M_Ref_'+k) for k in ('Concrete','Steel','Wood','Paper','Paint','Rubber','Light','Amber')}
count=0
def fit(name,path,center,size,yaw=0,mat=None):
 global count
 mesh=u.load_asset(path);assert mesh,path
 o=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*center),u.Rotator(yaw=yaw));o.set_actor_label('Menu_'+name)
 c=o.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 b=mesh.get_bounds();dim=b.box_extent*2
 scale=u.Vector(*(size[i]/max(.001,(dim.x,dim.y,dim.z)[i]) for i in range(3)))
 o.set_actor_scale3d(scale)
 v=b.origin*scale; angle=math.radians(yaw)
 offset=u.Vector(v.x*math.cos(angle)-v.y*math.sin(angle),v.x*math.sin(angle)+v.y*math.cos(angle),v.z)
 o.set_actor_location(u.Vector(*center)-offset,False,False)
 if mat:
  for i in range(c.get_num_materials()):c.set_material(i,mats[mat])
 count+=1;return o
ref='/Game/Bunker/ReferenceRoom/Meshes/'
# Modeled modular wall panels, not generic box surfaces.
for i in range(8):
 for side in (-1,1):
  fit(f'Wall_{side}_{i}',ref+'SM_Ref_WallPanel',(120+i*148,side*238,145),(148,10,290),0 if side==1 else 180, 'Concrete')
 for j in range(4):
  fit(f'Floor_{i}_{j}',ref+'SM_Ref_FloorTile',(80+i*148,-180+j*120,-3),(147,119,8),0,'Concrete')
# Ceiling ribs and longitudinal ducts from the original detailed kit.
for i in range(7):
 fit('Ceiling_'+str(i),ref+'SM_Ref_FloorTile',(130+i*170,0,298),(169,480,8),0,'Concrete')
for y in (-170,175):
 for i in range(4):
  fit(f'Pipe_{y}_{i}',D+'/SM_Menu_Pipe',(250+i*300,y,270),(300,21,21),0,'Steel')
fit('Desk',ref+'SM_Ref_Table',(255,-145,42),(180,88,84),0)
fit('Radio',ref+'SM_Ref_Radio',(250,-165,103),(58,28,34),90)
fit('Mug',ref+'SM_Ref_Mug',(225,-120,92),(18,16,20),0)
fit('Map',ref+'SM_Ref_Notebook',(190,-145,86),(52,42,3),0,'Paper')
fit('Documents',ref+'SM_Ref_Notebook',(285,-120,88),(35,27,7),12,'Paper')
fit('Notice',ref+'SM_Ref_NoticeBoard',(470,-158,190),(120,5,100),90)
fit('DeskLamp',D+'/SM_Menu_DeskLamp',(185,-186,123),(44,33,74),0,'Steel')
# Framed armoured door is a detailed existing hero mesh authored in this project.
door=fit('B13Door','/Game/Bunker/HeroKit/SM_Hero_BlastDoor',(525,195,121),(165,35,242),125)
# A menu-only graphite paint grade preserves all Painter roughness/normal detail.
paint=a.load_asset(D+'/M_Menu_Graphite') if a.does_asset_exist(D+'/M_Menu_Graphite') else tools.create_asset('M_Menu_Graphite',D,u.Material,u.MaterialFactoryNew())
me=u.MaterialEditingLibrary;me.delete_all_material_expressions(paint)
def sample_painter(suffix):
 t=me.create_material_expression(paint,u.MaterialExpressionTextureSample)
 t.set_editor_property('texture',u.load_asset('/Game/Bunker/Painter/SM_Hero_BlastDoor/T_M_Hero_Paint_'+suffix))
 if suffix=='Normal':t.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
 return t
base=sample_painter('BaseColor');mono=me.create_material_expression(paint,u.MaterialExpressionDesaturation)
one=me.create_material_expression(paint,u.MaterialExpressionConstant);one.set_editor_property('r',1.)
me.connect_material_expressions(base,'RGB',mono,'Input');me.connect_material_expressions(one,'',mono,'Fraction')
multiply=me.create_material_expression(paint,u.MaterialExpressionMultiply)
tint=me.create_material_expression(paint,u.MaterialExpressionConstant3Vector);tint.set_editor_property('constant',u.LinearColor(.34,.37,.38,1))
me.connect_material_expressions(mono,'',multiply,'A');me.connect_material_expressions(tint,'',multiply,'B')
me.connect_material_property(multiply,'',u.MaterialProperty.MP_BASE_COLOR)
orm=sample_painter('ORM');me.connect_material_property(orm,'G',u.MaterialProperty.MP_ROUGHNESS);me.connect_material_property(orm,'B',u.MaterialProperty.MP_METALLIC)
normal=sample_painter('Normal');me.connect_material_property(normal,'RGB',u.MaterialProperty.MP_NORMAL)
me.recompile_material(paint);a.save_loaded_asset(paint)
for index,slot in enumerate(door.static_mesh_component.get_editor_property('static_mesh').get_editor_property('static_materials')):
 name=str(slot.material_slot_name)
 kind='Safety' if 'Safety' in name else 'Steel' if 'Steel' in name else 'Paint'
 mat=u.load_asset('/Game/Bunker/Painter/SM_Hero_BlastDoor/M_Painter_'+kind)
 if mat:door.static_mesh_component.set_material(index,paint if kind=='Paint' else mat)

fit('EquipmentCrate',ref+'SM_Ref_CabinetBody',(395,178,28),(80,60,56),0,'Wood')
fit('Respirator',D+'/SM_Menu_Respirator',(390,162,72),(31,25,32),90,'Rubber')
fit('ForegroundCase',ref+'SM_Ref_CabinetBody',(70,-135,23),(68,70,46),0,'Rubber')
def sign(name,words,p,yaw,size,color):
 o=actors.spawn_actor_from_class(u.TextRenderActor,u.Vector(*p),u.Rotator(yaw=yaw));o.set_actor_label('Menu_'+name)
 c=o.text_render;c.set_text(u.Text(words));c.set_world_size(size);c.set_text_render_color(u.Color(*color));return o
sign('DoorNumber','B-13',(505,171,177),-145,25,(233,217,184))
sign('Civil','DEFESA CIVIL',(463,-158,235),180,14,(201,174,107))
sign('Protocol','PROTOCOLO 13',(463,-158,218),180,9,(201,174,107))
def light(name,p,lumens,radius,kelvin):
 o=actors.spawn_actor_from_class(u.PointLight,u.Vector(*p));o.set_actor_label('Menu_'+name)
 c=o.point_light_component;c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
 c.set_intensity(lumens);c.set_attenuation_radius(radius);c.set_cast_shadows(False);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',kelvin)
 return o,c
mainlamp,maincomponent=light('LampWarm',(185,-175,142),520,300,2800)
maincomponent.set_cast_shadows(True);maincomponent.set_editor_property('source_radius',9)
light('DoorWarm',(470,147,225),510,370,3400)
light('FrontFill',(-20,0,200),410,650,4200)
light('PropFill',(260,80,145),240,290,4600)
light('BackgroundRead',(1000,10,120),260,440,6500)
for i,x in enumerate((680,980,1280)):
 light('Corridor_'+str(i),(x,0,245),170-i*45,320,6500)
o,c=light('Emergency',(525,198,260),90,170,2400);c.set_editor_property('use_temperature',False);c.set_light_color(u.LinearColor(1,.015,.003,1));o.set_editor_property('tags',[u.Name('MenuEmergency')])
red=a.load_asset(D+'/M_Menu_Red') if a.does_asset_exist(D+'/M_Menu_Red') else tools.create_asset('M_Menu_Red',D,u.Material,u.MaterialFactoryNew())
edit=u.MaterialEditingLibrary;edit.delete_all_material_expressions(red)
rgb=edit.create_material_expression(red,u.MaterialExpressionConstant3Vector);rgb.set_editor_property('constant',u.LinearColor(2,.035,.008,1));edit.connect_material_property(rgb,'',u.MaterialProperty.MP_EMISSIVE_COLOR);edit.recompile_material(red);a.save_loaded_asset(red)
lens_actor=fit('RedLens',ref+'SM_Ref_Lamp',(525,228,263),(32,18,20),90)
for slot in range(lens_actor.static_mesh_component.get_num_materials()):lens_actor.static_mesh_component.set_material(slot,red)

for j in range(12):
 fit('DrainBar_'+str(j),ref+'SM_Ref_Sign',(80+j*53,87,1),(45,27,2),0,'Steel')
fit('EndWall',ref+'SM_Ref_WallPanel',(1320,0,145),(460,10,290),90,'Concrete')
fan_actor=fit('VentFan',D+'/SM_Menu_Fan',(1250,0,182),(60,60,10),0,'Steel')
fan_actor.static_mesh_component.set_editor_property('mobility',u.ComponentMobility.MOVABLE)
fan_actor.set_actor_rotation(u.Rotator(pitch=90),False);fan_actor.set_editor_property('tags',[u.Name('MenuFan')])
# Sparse particles in world space, not a texture over the screen.
dustmat=a.load_asset(D+'/M_Menu_Dust') if a.does_asset_exist(D+'/M_Menu_Dust') else tools.create_asset('M_Menu_Dust',D,u.Material,u.MaterialFactoryNew())
edit.delete_all_material_expressions(dustmat);dustmat.set_editor_property('blend_mode',u.BlendMode.BLEND_ADDITIVE)
dustcol=edit.create_material_expression(dustmat,u.MaterialExpressionConstant3Vector);dustcol.set_editor_property('constant',u.LinearColor(.035,.027,.016,1))
edit.connect_material_property(dustcol,'',u.MaterialProperty.MP_EMISSIVE_COLOR);edit.recompile_material(dustmat);a.save_loaded_asset(dustmat)
import random
randomizer=random.Random(13)
for k in range(24):
 o=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(randomizer.uniform(150,620),randomizer.uniform(-180,120),randomizer.uniform(100,215)))
 o.set_actor_label('Menu_Dust_'+str(k));o.set_editor_property('tags',[u.Name('MenuDust')])
 c=o.static_mesh_component;c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'))
 c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);c.set_editor_property("cast_shadow",False);c.set_material(0,dustmat)
 o.set_actor_scale3d(u.Vector(.004,.004,.004))
cam=actors.spawn_actor_from_class(u.CameraActor,u.Vector(-260,0,158),u.Rotator());cam.set_actor_label('Menu_MainCamera');cam.camera_component.set_field_of_view(48)
pp=actors.spawn_actor_from_class(u.PostProcessVolume,u.Vector());pp.set_actor_label('Menu_Post');pp.set_editor_property('unbound',True)
s=pp.get_editor_property('settings')
for k,v in dict(override_auto_exposure_method=True,auto_exposure_method=u.AutoExposureMethod.AEM_MANUAL,override_auto_exposure_apply_physical_camera_exposure=True,auto_exposure_apply_physical_camera_exposure=False,override_auto_exposure_bias=True,auto_exposure_bias=-2.8).items():s.set_editor_property(k,v)
pp.set_editor_property('settings',s)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Script/Condominio13.CinematicMenuMode'))
assert levels.save_current_level()
(R/'logs/cinematic_menu_scene.json').write_text(json.dumps(dict(mesh_actors=count,level=D+'/L_MainMenu',fov=48,reference_used_as_texture=False),indent=2))
u.log('C13_CINEMATIC_MENU_SCENE_OK')
