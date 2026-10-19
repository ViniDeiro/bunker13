"""Convert the four authored lockers and place two pantry cabinets, initially empty."""
import unreal as u
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
level.load_level('/Game/Bunker/Lvl_Bunker');mesh=u.load_asset('/Game/Bunker/HeroKit/SM_Hero_Locker');assert mesh
existing={a.get_actor_label():a for a in actors.get_all_level_actors()};created=[]
for i in range(1,5):
 label=f'INT_Storage_Dorm_{i}';old=existing.get(f'Dorm_Locker_{i}');a=existing.get(label)
 if not a:
  assert old,f'Missing locker {i}'
  a=actors.spawn_actor_from_class(u.BunkerContainer,old.get_actor_location(),old.get_actor_rotation());actors.destroy_actor(old);a.set_actor_label(label)
 a.mesh.set_static_mesh(mesh);a.set_actor_scale3d(u.Vector(1,1,1));a.set_editor_property('display_name',f'Armário do dormitório {i}');a.set_editor_property('max_slots',12);a.set_editor_property('max_weight_kg',30.0);created.append(label)
for i,(x,y) in enumerate(((2600,-1510),(2660,-1510))):
 label=f'INT_Storage_Pantry_{i}';a=existing.get(label)
 if not a:a=actors.spawn_actor_from_class(u.BunkerContainer,u.Vector(x,y,0));a.set_actor_label(label)
 a.mesh.set_static_mesh(mesh);a.set_actor_scale3d(u.Vector(1,1,1));a.set_editor_property('display_name','Despensa — suprimentos' if i==0 else 'Despensa — reserva');a.set_editor_property('max_slots',24);a.set_editor_property('max_weight_kg',60.0);created.append(label)
assert len(created)==6
level.save_current_level();(ROOT/'logs/storage_install.json').write_text(json.dumps({'containers':created,'production_initial_contents':'empty','shared_access':'unlocked cooperative containers','persisted_across_sessions':False,'architecture_changed':False},indent=2));u.log('C13_STORAGE_INSTALLED')
