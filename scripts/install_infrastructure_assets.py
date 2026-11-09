import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];dest='/Game/Bunker/Infrastructure/Meshes';u.EditorAssetLibrary.make_directory(dest)
tasks=[]
for f in sorted((R/'exports/infrastructure').glob('*.fbx')):
 t=u.AssetImportTask();t.filename=str(f);t.destination_path=dest;t.automated=True;t.replace_existing=True;t.save=True
 o=u.FbxImportUI();o.import_mesh=True;o.import_materials=True;o.import_textures=False;o.import_as_skeletal=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.generate_lightmap_u_vs=False;o.static_mesh_import_data.auto_generate_collision=True;t.options=o;tasks.append(t)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
mapping={'Paint':'Paint','Steel':'Steel','Rubber':'Rubber','Fuel':'Amber','Filter':'Ivory'}
for t in tasks:
 mesh=u.load_asset(dest+'/'+Path(t.filename).stem);slots=list(mesh.get_editor_property('static_materials'))
 for slot in slots:
  key=str(slot.material_slot_name).removeprefix('M_Infra_');slot.set_editor_property('material_interface',u.load_asset('/Game/Bunker/ReferenceRoom/Materials/M_Ref_'+mapping.get(key,'Steel')))
 mesh.set_editor_property('static_materials',slots);u.EditorAssetLibrary.save_loaded_asset(mesh)
rules=u.load_asset('/Game/Bunker/Data/DA_SurvivalRules');rows=list(rules.get_editor_property('items'));existing={str(x.get_editor_property('item_type')) for x in rows}
for name,weight in [('FuelCan',2.3),('RepairParts',.8),('FilterCartridge',.5)]:
 if name in existing:continue
 d=u.BunkerItemDefinition();d.set_editor_property('item_type',name);d.set_editor_property('weight_kg',weight);rows.append(d)
rules.set_editor_property('items',rows);u.EditorAssetLibrary.save_loaded_asset(rules)
(R/'logs/infra_import.json').write_text(json.dumps({'meshes':[str(x) for t in tasks for x in t.imported_object_paths],'item_types_added':['FuelCan','RepairParts','FilterCartridge'],'legacy_items_unchanged':True},indent=2));u.log_warning('C13_INFRA_IMPORT_OK')
