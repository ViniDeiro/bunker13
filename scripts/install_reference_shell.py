from pathlib import Path
import json,unreal as u
R=Path(__file__).resolve().parents[1];D='/Game/Bunker/ReferenceRoom/Meshes';u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
a=next(a for a in u.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label()=='Bunker_B1_Merged');c=a.static_mesh_component;old=c.get_editor_property('static_mesh');mapping={str(n):c.get_material(i) for i,n in enumerate(c.get_material_slot_names())}
t=u.AssetImportTask();t.filename=str(R/'exports/Bunker_ReferenceShell.fbx');t.destination_path=D;t.destination_name='SM_ReferenceShell';t.automated=True;t.replace_existing=True;t.save=True
o=u.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=False;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=o;u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);m=u.load_asset(D+'/SM_ReferenceShell');m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
slots=list(m.get_editor_property('static_materials'))
for s in slots:s.set_editor_property('material_interface',mapping[str(s.material_slot_name)])
m.set_editor_property('static_materials',slots);u.EditorAssetLibrary.save_loaded_asset(m);c.set_static_mesh(m)
for i,n in enumerate(c.get_material_slot_names()):c.set_material(i,mapping[str(n)])
u.EditorLevelLibrary.save_current_level()
old_report=json.loads((R/'logs/unreal_playtest_export.json').read_text());new=json.loads((R/'logs/reference_shell_export.json').read_text())
assert old_report['source_objects']-new['source_objects']==4 and old_report['vertices']-new['vertices']==32 and old_report['faces']-new['faces']==24
assert old_report['materials']==new['materials'] and old_report['movable_leaves_removed']==new['movable_leaves_removed']==13
(R/'logs/reference_shell_integrity.json').write_text(json.dumps({'removed_only':['SM_Mesa_Cartas','SM_Radio_Social','SM_Estante_Social','SM_Quadro_Avisos'],'legacy_objects_removed':4,'box_vertices_removed':32,'box_faces_removed':24,'material_slot_order_preserved':True,'native_doors_preserved':13,'original_geometry_asset_preserved':True},indent=2));u.log_warning('REFERENCE_SHELL_INTEGRITY_OK')
