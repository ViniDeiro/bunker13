"""Preserve authored art; migrate only network game mode and player starts."""
import unreal
from pathlib import Path
import json
ROOT=Path('/Users/vini_deiro/bankers')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level.load_level('/Game/Bunker/Lvl_Bunker')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in actors.get_all_level_actors():
    if isinstance(actor, (unreal.BunkerInteractionManager, unreal.PlayerStart)):
        actors.destroy_actor(actor)
world=unreal.EditorLevelLibrary.get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode', unreal.BunkerGameMode)
for i,(x,y) in enumerate([(1800,-1000),(1800,-1120),(1920,-1000),(1920,-1120)]):
    a=actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(x,y,110),unreal.Rotator(0,0,0))
    a.set_actor_label(f'PlayerStart_Bunker_{i+1}')
level.save_current_level()
(ROOT/'logs/network_map.json').write_text(json.dumps({'game_mode':'BunkerGameMode','starts':4,'legacy_managers':0},indent=2))
unreal.log('C13_NETWORK_MAP_OK')
