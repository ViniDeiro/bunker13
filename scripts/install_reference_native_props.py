from pathlib import Path
import json,unreal as u
R=Path(__file__).resolve().parents[1];D='/Game/Bunker/ReferenceRoom';u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker');A=u.AssetToolsHelpers.get_asset_tools()
manifest=json.loads((R/'exports/reference_room/manifest.json').read_text())
for name in manifest:
 t=u.AssetImportTask();t.filename=str(R/'exports/reference_room'/(name+'.fbx'));t.destination_path=D+'/Meshes';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 o=u.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=False;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=o;A.import_asset_tasks([t]);mesh=u.load_asset(D+'/Meshes/'+name)
 slots=list(mesh.get_editor_property('static_materials'))
 for s in slots:s.set_editor_property('material_interface',u.load_asset(D+'/Materials/'+str(s.material_slot_name)))
 mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);u.EditorAssetLibrary.save_loaded_asset(mesh)
actors=u.EditorLevelLibrary.get_all_level_actors();changes=[]
for a in actors:
 n=a.get_actor_label()
 if n=='REF_Radio':u.EditorLevelLibrary.destroy_actor(a);continue
 if n in ('INT_Radio','INT_Dartboard'):
  before=list(a.get_actor_location().to_tuple());scale=list(a.get_actor_scale3d().to_tuple());key='SM_Ref_RadioLegacy' if n=='INT_Radio' else 'SM_Ref_DartboardLegacy';a.mesh.set_static_mesh(u.load_asset(D+'/Meshes/'+key))
  for i in range(a.mesh.get_num_materials()):a.mesh.set_material(i,None)
  a.mesh.set_editor_property('lighting_channels',u.LightingChannels(False,False,True));a.set_folder_path('Convivencia_Reference/Interacao');assert before==list(a.get_actor_location().to_tuple()) and scale==list(a.get_actor_scale3d().to_tuple());changes.append({'actor':n,'root_preserved':before,'scale_preserved':scale,'mesh':key})
u.EditorLevelLibrary.save_current_level();(R/'logs/reference_native_props.json').write_text(json.dumps(changes,indent=2));exec(compile((R/'scripts/snapshot_reference_scene.py').read_text(),str(R/'scripts/snapshot_reference_scene.py'),'exec'));u.log_warning('REFERENCE_NATIVE_PROPS_INSTALLED')
