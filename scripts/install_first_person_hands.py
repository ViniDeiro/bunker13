"""Import the editable hands/utensils and reuse the established Painter materials."""
import unreal as u
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];DEST='/Game/Bunker/Hands';u.EditorAssetLibrary.make_directory(DEST)
materials={'Glove':'/Game/Bunker/Painter/SM_Hero_Bed/M_Painter_Fabric','Reinforcement':'/Game/Bunker/Painter/SM_Hero_Locker/M_Painter_Rubber','Cuff':'/Game/Bunker/Painter/SM_Hero_Bed/M_Painter_Fabric','Stitch':'/Game/Bunker/Painter/SM_Hero_Bed/M_Painter_Linen','Steel':'/Game/Bunker/Painter/SM_Hero_Bed/M_Painter_Steel','Gauze':'/Game/Bunker/Painter/SM_Hero_Bed/M_Painter_Linen'}
report=[]
for name in ('SM_Hands_Left','SM_Hands_Right','SM_Hands_Spoon','SM_Hands_Bandage','SM_Use_Water','SM_Use_Food'):
 task=u.AssetImportTask();task.filename=str(ROOT/'exports/hands'/(name+'.fbx'));task.destination_path=DEST;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
 options=u.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=False;options.import_materials=False;options.import_textures=False;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.generate_lightmap_u_vs=False;options.static_mesh_import_data.auto_generate_collision=False;task.options=options
 u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=u.load_asset(DEST+'/'+name);assert mesh,name
 slots=list(mesh.get_editor_property('static_materials'))
 for slot in slots:
  if name.startswith('SM_Use_'):path='/Game/Bunker/Items/'+name.removeprefix('SM_Use_')+'/M_Item_'+name.removeprefix('SM_Use_')
  else:path=materials[str(slot.material_slot_name).removeprefix('M_Hands_')]
  mat=u.load_asset(path);assert mat,path;slot.set_editor_property('material_interface',mat)
 mesh.set_editor_property('static_materials',slots);u.EditorAssetLibrary.save_loaded_asset(mesh)
 dims=mesh.get_bounds().box_extent*2;assert max(dims.x,dims.y,dims.z)<35,(name,dims)
 report.append({'name':name,'dimensions_cm':[dims.x,dims.y,dims.z],'materials':[str(s.material_interface.get_path_name()) for s in slots],'collision':False})
(ROOT/'logs/hands_unreal.json').write_text(json.dumps(report,indent=2));u.log('C13_HANDS_IMPORTED')
