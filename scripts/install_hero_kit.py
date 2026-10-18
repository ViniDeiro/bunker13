"""Import the refined kit and replace existing beds/lockers without moving routes."""
from pathlib import Path
import json
import unreal as u

ROOT=Path(__file__).resolve().parents[1]
DEST='/Game/Bunker/HeroKit'
u.EditorAssetLibrary.make_directory(DEST)
u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
slots={'Paint':'M_B2_UtilityGreen','Steel':'M_B2_DarkSteel','Fabric':'M_B2_BedFabric',
       'Rubber':'M_B2_Rubber','Linen':'M_B2_ModuleWhite','Safety':'M_B2_SafetyOrange'}
meshes={}
report={}
for name in ('SM_Hero_Bed','SM_Hero_Locker','SM_Hero_BlastDoor'):
    task=u.AssetImportTask();task.filename=str(ROOT/'exports/hero_kit'/(name+'.fbx'))
    task.destination_path=DEST;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
    options=u.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=False
    options.import_materials=False;options.import_textures=False
    options.static_mesh_import_data.combine_meshes=True
    options.static_mesh_import_data.generate_lightmap_u_vs=True
    options.static_mesh_import_data.auto_generate_collision=True
    task.options=options;u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=u.load_asset(DEST+'/'+name)
    if not isinstance(mesh,u.StaticMesh):raise RuntimeError('Import failed: '+name)
    materials=list(mesh.get_editor_property('static_materials'))
    for i,slot in enumerate(materials):
        key=str(slot.material_slot_name).removeprefix('M_Hero_')
        if key not in slots:raise RuntimeError('Unexpected material slot '+key)
        slot.set_editor_property('material_interface',u.load_asset('/Game/Bunker/Materials/'+slots[key]))
    mesh.set_editor_property('static_materials',materials)
    u.EditorAssetLibrary.save_loaded_asset(mesh)
    bounds=mesh.get_bounds().box_extent*2
    report[name]={'dimensions_cm':[bounds.x,bounds.y,bounds.z],'materials':len(materials)}
    meshes[name]=mesh
assert 100<report['SM_Hero_Bed']['dimensions_cm'][0]<120,'Bed import scale invalid'
assert 180<report['SM_Hero_Locker']['dimensions_cm'][2]<190,'Locker import scale invalid'

beds=lockers=0
for actor in u.EditorLevelLibrary.get_all_level_actors():
    label=actor.get_actor_label()
    if label.startswith(('BedFrame_','Pillow_','Dorm_BedHead_','Dorm_Blanket_','Dorm_LockerDoor_','Dorm_LockerHandle_')):
        u.EditorLevelLibrary.destroy_actor(actor);continue
    if label.startswith('INT_Bed_'):
        actor.set_actor_scale3d(u.Vector(1,1,1))
        actor.mesh.set_static_mesh(meshes['SM_Hero_Bed'])
        for i in range(actor.mesh.get_num_materials()):actor.mesh.set_material(i,None)
        beds+=1
    elif label.startswith('Dorm_Locker_'):
        loc=actor.get_actor_location();loc.z=0;actor.set_actor_location(loc,False,False)
        actor.set_actor_scale3d(u.Vector(1,1,1))
        actor.static_mesh_component.set_static_mesh(meshes['SM_Hero_Locker'])
        for i in range(actor.static_mesh_component.get_num_materials()):actor.static_mesh_component.set_material(i,None)
        lockers+=1
assert beds==4 and lockers==4,(beds,lockers)
u.EditorLevelLibrary.save_current_level()
report.update({'beds_replaced':beds,'lockers_replaced':lockers,'door':'Imported asset; existing baked doors not replaced','painter_used':False})
(ROOT/'logs/hero_kit_unreal.json').write_text(json.dumps(report,indent=2))
u.log_warning('HERO_KIT_UNREAL_OK '+json.dumps(report))
