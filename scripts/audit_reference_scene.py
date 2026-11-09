from pathlib import Path
import json,unreal as u
R=Path(__file__).resolve().parents[1];u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker');rows=[]
for a in u.EditorLevelLibrary.get_all_level_actors():
 p=a.get_actor_location();label=a.get_actor_label()
 if not(label.startswith('REF_') or (650<p.x<1650 and -800<p.y<0)):continue
 row={'label':label,'name':a.get_name(),'class':a.get_class().get_name(),'position':list(p.to_tuple()),'scale':list(a.get_actor_scale3d().to_tuple()),'meshes':[]}
 for c in a.get_components_by_class(u.StaticMeshComponent):
  mesh=c.get_editor_property('static_mesh');ch=c.get_editor_property('lighting_channels')
  row['meshes'].append({'component':c.get_name(),'mesh':mesh.get_path_name() if mesh else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())],'channels':[ch.channel0,ch.channel1,ch.channel2],'relative_loc':list(c.get_editor_property('relative_location').to_tuple()),'bounds_cm':list((mesh.get_bounds().box_extent*2).to_tuple()) if mesh else None,'bounds_origin':list(mesh.get_bounds().origin.to_tuple()) if mesh else None})
 rows.append(row)
(R/'logs/reference_scene_audit.json').write_text(json.dumps(rows,indent=2));u.log_warning('REFERENCE_SCENE_AUDIT_OK')
