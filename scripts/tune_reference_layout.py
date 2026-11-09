"""Last ergonomic and editor-organization pass; no legacy native actor moves."""
from pathlib import Path
import unreal as u
R=Path(__file__).resolve().parents[1];u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
for a in u.EditorLevelLibrary.get_all_level_actors():
 n=a.get_actor_label()
 if not n.startswith('REF_'):continue
 p=a.get_actor_location()
 if n=='REF_Ceiling':p.z=286;a.set_actor_location(p,False,False)
 c=a.get_component_by_class(u.StaticMeshComponent)
 if c and c.get_editor_property('static_mesh'):
  mesh=c.get_editor_property('static_mesh')
  if mesh.get_name() in ('SM_Ref_Sofa','SM_Ref_Table','SM_Ref_Chair','SM_Ref_CabinetBody','SM_Ref_TV'):
   b=mesh.get_bounds();p.z=2.6-(b.origin.z-b.box_extent.z)*a.get_actor_scale3d().z;a.set_actor_location(p,False,False)
 if n.startswith('REF_Mug') or n in ('REF_Notebook','REF_SideTea','REF_Journal','REF_Radio'):p.z=76.15;a.set_actor_location(p,False,False)
 if n=='REF_Blanket':p.z=57.8;a.set_actor_location(p,False,False)
 if n.startswith('REF_Card') and n not in ('REF_CardChair','REF_CardTable'):p.z=76.175;a.set_actor_location(p,False,False)
 if n=='REF_CardTable' or n.startswith('REF_Card') and n not in ('REF_CardChair','REF_CardTable'):p.y=-565;a.set_actor_location(p,False,False)
 if n=='REF_CardChair':p.y=-515;a.set_actor_location(p,False,False)
 group='Iluminacao' if isinstance(a,(u.PointLight,u.PostProcessVolume)) else 'Interacao' if a.get_class().get_name()=='BunkerReferenceCabinet' else 'Arquitetura' if any(k in n for k in ('Panel','Floor','Ceiling','Duct')) else 'Moveis_e_objetos'
 a.set_folder_path('Convivencia_Reference/'+group)
 if n=='REF_Exposure':
  s=a.get_editor_property('settings');s.set_editor_property('override_ambient_occlusion_intensity',True);s.set_editor_property('ambient_occlusion_intensity',.6);s.set_editor_property('override_ambient_occlusion_radius',True);s.set_editor_property('ambient_occlusion_radius',80);a.set_editor_property('settings',s)
u.EditorLevelLibrary.save_current_level();exec(compile((R/'scripts/snapshot_reference_scene.py').read_text(),str(R/'scripts/snapshot_reference_scene.py'),'exec'));u.log_warning('REFERENCE_LAYOUT_FINAL_OK')
