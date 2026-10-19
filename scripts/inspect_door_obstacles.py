from pathlib import Path
import unreal as u,json
ROOT=Path(__file__).resolve().parents[1]
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/Bunker/Lvl_Bunker')
failed=json.loads((ROOT/'logs/door_capsule_audit.json').read_text())
names={x['hit'] for x in failed['entries'] if not x['clear']}
results=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if a.get_name() not in names:continue
    loc=a.get_actor_location();origin,extent=a.get_actor_bounds(False)
    results.append({'name':a.get_name(),'label':a.get_actor_label(),'location':[loc.x,loc.y,loc.z],'bounds_origin':[origin.x,origin.y,origin.z],'bounds_extent':[extent.x,extent.y,extent.z]})
(ROOT/'logs/door_obstacles.json').write_text(json.dumps(results,indent=2))
u.log('C13_DOOR_OBSTACLES '+json.dumps(results))
