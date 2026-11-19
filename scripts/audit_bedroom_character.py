"""Audit pawn asset metadata only. Use C13RestRigExport for bone data; do not use skeletal FBX export in commandlet mode."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
u.EditorLoadingAndSavingUtils.new_blank_map(False)
c=u.load_class(None,'/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter.BP_FirstPersonCharacter_C');assert c
a=u.EditorLevelLibrary.spawn_actor_from_class(c,u.Vector(0,0,100));rows=[]
for m in a.get_components_by_class(u.SkeletalMeshComponent):
 mesh=m.get_skeletal_mesh_asset()
 row={'component':m.get_name(),'asset':mesh.get_path_name() if mesh else None,'relative_location':list(m.get_editor_property('relative_location').to_tuple()),'relative_rotation':list(m.get_editor_property('relative_rotation').to_tuple()),'owner_no_see':m.get_editor_property('owner_no_see'),'only_owner_see':m.get_editor_property('only_owner_see')}
 if mesh:
  row['skeleton']=mesh.get_editor_property('skeleton').get_path_name();row['bounds_cm']=list((mesh.get_bounds().box_extent*2).to_tuple())
  (R/'logs/bedroom_character_audit.json').write_text(json.dumps(rows+[row],indent=2))
 rows.append(row)
(R/'logs/bedroom_character_audit.json').write_text(json.dumps(rows,indent=2));u.log('C13_CHARACTER_AUDIT_OK')
