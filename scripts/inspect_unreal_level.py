import json
from pathlib import Path
import unreal

LEVEL = "/Game/Bunker/Lvl_Bunker"
unreal.EditorLevelLibrary.load_level(LEVEL)
rows = []
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    row = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "location": list(actor.get_actor_location().to_tuple()),
        "rotation": list(actor.get_actor_rotation().to_tuple()),
    }
    rows.append(row)
report = {
    "actors": rows,
    "counts": {
        "total": len(rows),
        "player_starts": sum(r["class"] == "PlayerStart" for r in rows),
        "static_mesh_actors": sum(r["class"] == "StaticMeshActor" for r in rows),
        "point_lights": sum(r["class"] == "PointLight" for r in rows),
    },
}
output = Path(__file__).resolve().parents[1] / "logs" / "unreal_level_inspection.json"
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
unreal.log_warning(f"CONDOMINIO13_INSPECTION_OK {json.dumps(report['counts'])}")
