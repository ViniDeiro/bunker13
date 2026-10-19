"""Import original item meshes/PBR maps and replace only the six live pickups."""
from pathlib import Path
import json
import unreal as u
ROOT=Path(__file__).resolve().parents[1];DEST='/Game/Bunker/Items'
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
level.load_level('/Game/Bunker/Lvl_Bunker');tools=u.AssetToolsHelpers.get_asset_tools();report=[];meshes={}
for key in ('Water','Food','Medkit','Battery','Tool'):
    dest=DEST+'/'+key;u.EditorAssetLibrary.make_directory(dest);name='SM_Item_'+key
    task=u.AssetImportTask();task.filename=str(ROOT/'exports/items'/(name+'.fbx'));task.destination_path=dest;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
    options=u.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=False;options.import_materials=False;options.import_textures=False
    options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.generate_lightmap_u_vs=False;options.static_mesh_import_data.auto_generate_collision=True
    task.options=options;tools.import_asset_tasks([task]);mesh=u.load_asset(dest+'/'+name);assert isinstance(mesh,u.StaticMesh),name
    textures={}
    for kind in ('BaseColor','ORM','Normal'):
        task=u.AssetImportTask();task.filename=str(ROOT/'assets/items'/f'T_Item_{key}_{kind}.png');task.destination_path=dest;task.destination_name=f'T_Item_{key}_{kind}';task.automated=True;task.replace_existing=True;task.save=True;tools.import_asset_tasks([task])
        tex=u.load_asset(dest+'/'+task.destination_name);tex.set_editor_property('srgb',kind=='BaseColor')
        if kind=='Normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
        if kind=='ORM':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
        u.EditorAssetLibrary.save_loaded_asset(tex);textures[kind]=tex
    mat=u.load_asset(dest+'/M_Item_'+key)
    if not mat:mat=tools.create_asset('M_Item_'+key,dest,u.Material,u.MaterialFactoryNew())
    u.MaterialEditingLibrary.delete_all_material_expressions(mat)
    for kind,sampler,connections in [
        ('BaseColor',u.MaterialSamplerType.SAMPLERTYPE_COLOR,[('RGB',u.MaterialProperty.MP_BASE_COLOR)]),
        ('Normal',u.MaterialSamplerType.SAMPLERTYPE_NORMAL,[('RGB',u.MaterialProperty.MP_NORMAL)]),
        ('ORM',u.MaterialSamplerType.SAMPLERTYPE_MASKS,[('R',u.MaterialProperty.MP_AMBIENT_OCCLUSION),('G',u.MaterialProperty.MP_ROUGHNESS),('B',u.MaterialProperty.MP_METALLIC)])]:
        node=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionTextureSample);node.set_editor_property('texture',textures[kind]);node.set_editor_property('sampler_type',sampler)
        for channel,prop in connections:assert u.MaterialEditingLibrary.connect_material_property(node,channel,prop)
    u.MaterialEditingLibrary.recompile_material(mat);u.EditorAssetLibrary.save_loaded_asset(mat)
    slots=list(mesh.get_editor_property('static_materials'));assert len(slots)==1,(key,len(slots));slots[0].set_editor_property('material_interface',mat);mesh.set_editor_property('static_materials',slots);u.EditorAssetLibrary.save_loaded_asset(mesh)
    dims=mesh.get_bounds().box_extent*2;assert 2<max(dims.x,dims.y,dims.z)<35,(key,dims)
    meshes[key]=mesh;report.append({'type':key,'mesh':dest+'/'+name,'dimensions_cm':[dims.x,dims.y,dims.z],'material_slots':len(slots),'normal':'DirectX','uv_channel':0})
labels={'INT_Water_01':'Water','INT_Water_02':'Water','INT_Can_01':'Food','INT_Medkit':'Medkit','INT_Battery':'Battery','INT_Tool':'Tool'}
updated=[]
for actor in actors.get_all_level_actors():
    label=actor.get_actor_label()
    if label not in labels:continue
    key=labels[label];mesh=meshes[key];position=actor.get_actor_location()
    # Real support surfaces, clear of the former massing proxies and walking lanes.
    placements={'INT_Water_01':(2360,-1570,70.5),'INT_Water_02':(2010,-300,78.5),
                'INT_Can_01':(2040,-300,78.5),'INT_Medkit':(305,-1335,78.5),
                'INT_Battery':(805,-1460,80.5),'INT_Tool':(1155,-1470,96.5)}
    position=u.Vector(*placements[label])
    actor.set_actor_scale3d(u.Vector(1,1,1));actor.set_actor_location(position,False,False);actor.mesh.set_static_mesh(mesh)
    for i in range(actor.mesh.get_num_materials()):actor.mesh.set_material(i,None)
    # Dropped mesh replication uses its source mesh/slots and the same real-world scale.
    actor.set_editor_property('item_type',key);updated.append(label)
assert len(updated)==6,updated
level.save_current_level();u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
(ROOT/'logs/item_unreal.json').write_text(json.dumps({'assets':report,'world_pickups':updated,'scale':'FBX meters to UE cm; actor scale 1','physics':'No rigid-body for critical items','materials':'Original procedural PBR atlases; not Painter exports'},indent=2))
u.log('C13_ITEM_KIT_INSTALLED')
