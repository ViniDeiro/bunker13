"""Replace collection tables with open retail displays without replacing pickup actors."""
import unreal as u

levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert levels.load_level('/Game/Bunker/Lvl_CollectionRound')
by_name={a.get_actor_label():a for a in actors.get_all_level_actors()}
mesh=u.load_asset('/Engine/BasicShapes/Cube')
steel=u.load_asset('/Game/Bunker/Materials/M_B2_DarkSteel')
white=u.load_asset('/Game/Bunker/Materials/M_B2_ModuleWhite')
green=u.load_asset('/Game/Bunker/Materials/M_B2_UtilityGreen')
lens=u.load_asset('/Game/Bunker/ReferenceRoom/Materials/M_Ref_Light')
objects=[]
tables=[]
assert all(f'ROUND_Loot_{t}_{i}' in by_name for t in range(3) for i in range(4))
def box(name,location,dimensions,mat,solid=True):
    a=by_name.get(name) or actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*location))
    a.set_actor_label(name)
    a.set_actor_location(u.Vector(*location),False,False)
    c=a.static_mesh_component
    c.set_static_mesh(mesh);c.set_material(0,mat)
    c.set_world_scale3d(u.Vector(*(n/100 for n in dimensions)))
    c.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS if solid else u.CollisionEnabled.NO_COLLISION)
    c.set_editor_property('lighting_channels',u.LightingChannels(True,True,False))
    objects.append(a)
for t,(x,y) in enumerate(((1450,1430),(2250,1000),(3050,570))):
    table=by_name[f'ROUND_SupplyTable_{t}']
    p=table.get_actor_location()
    bounds=table.static_mesh_component.get_editor_property('static_mesh').get_bounds()
    top=p.z+bounds.origin.z+bounds.box_extent.z
    tag=f'MarketDisplay_{t}_'
    fridge=t==0
    box(tag+'Base',(x,y,(312.5+top)/2),(129,65,top-312.5),steel)
    box(tag+'Back',(x,y+36,top+38),(143,5,88),white if fridge else steel)
    for dx in (-69,69):
        box(tag+('Left' if dx<0 else 'Right'),(x+dx,y,top+41),(5,70,88),white if fridge else green)
    box(tag+'Header',(x,y,top+84),(143,77,7),green)
    box(tag+'Lens',(x,y-19,top+79),(114,5,2),lens,False)
    if fridge:
        box(tag+'AirGrille',(x,y-33,top-25),(108,4,11),green,False)
    light=by_name.get(tag+'Light') or actors.spawn_actor_from_class(u.PointLight,u.Vector(x,y-25,top+72))
    light.set_actor_label(tag+'Light')
    c=light.point_light_component
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
    c.set_intensity(175 if fridge else 145)
    c.set_attenuation_radius(165)
    c.set_cast_shadows(False)
    c.set_editor_property('lighting_channels',u.LightingChannels(True,True,False))
    c.set_editor_property('use_temperature',True)
    c.set_editor_property('temperature',5600 if fridge else 3900)
# Existing actors keep their identities and transforms, including checkpoints.
# The display deck matches the height of the table it replaces.
for t in range(3):
    c=by_name[f'ROUND_SupplyTable_{t}'].static_mesh_component
    c.set_visibility(False)
    c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
assert levels.save_current_level()
u.log('C13_MARKET_DISPLAYS_OK displays=3 loot_unchanged=12')
