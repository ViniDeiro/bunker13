from pathlib import Path
import json,unreal as u
R=Path(__file__).resolve().parents[1];u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker');rows=[]
for a in u.EditorLevelLibrary.get_all_level_actors():
 if not (a.get_actor_label().startswith('REF_') or a.get_actor_label() in ('INT_Radio','INT_Dartboard')):continue
 c=a.get_component_by_class(u.StaticMeshComponent);mesh=c.get_editor_property('static_mesh') if c else None
 rows.append({'label':a.get_actor_label(),'mesh':mesh.get_name() if mesh else None,'position':list(a.get_actor_location().to_tuple()),'rotation':list(a.get_actor_rotation().to_tuple()),'scale':list(a.get_actor_scale3d().to_tuple()),'class':a.get_class().get_name()})
(R/'exports/reference_room/scene_placements.json').write_text(json.dumps(rows,indent=2));u.log_warning('REFERENCE_SCENE_SNAPSHOT_OK')
