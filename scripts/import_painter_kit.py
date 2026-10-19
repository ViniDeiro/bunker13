"""Use UV-mapped Painter exports on the refined kit, preserving gameplay actors."""
from pathlib import Path
import json
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'logs/painter_production.json').read_text())
assert manifest['complete'],'Painter batch incomplete'
report=[]
for item in manifest['assets']:
    asset=item['asset'];dest='/Game/Bunker/Painter/'+asset
    u.EditorAssetLibrary.make_directory(dest)
    mesh=u.load_asset('/Game/Bunker/HeroKit/'+asset)
    assert isinstance(mesh,u.StaticMesh),asset
    slots=list(mesh.get_editor_property('static_materials'))
    for slot in slots:
        setname=str(slot.material_slot_name)
        textures={}
        for kind in ('BaseColor','Normal','ORM'):
            source=ROOT/'assets/painter'/asset/(setname+'_'+kind+'.png')
            assert source.is_file(),str(source)
            task=u.AssetImportTask();task.filename=str(source);task.destination_path=dest
            task.destination_name='T_'+setname+'_'+kind;task.automated=True;task.replace_existing=True;task.save=True
            u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            texture=u.load_asset(dest+'/'+task.destination_name)
            texture.set_editor_property('srgb',kind=='BaseColor')
            if kind=='Normal':texture.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
            if kind=='ORM':texture.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
            u.EditorAssetLibrary.save_loaded_asset(texture);textures[kind]=texture
        name='M_Painter_'+setname.removeprefix('M_Hero_')
        mat=u.load_asset(dest+'/'+name)
        if not mat:mat=u.AssetToolsHelpers.get_asset_tools().create_asset(name,dest,u.Material,u.MaterialFactoryNew())
        u.MaterialEditingLibrary.delete_all_material_expressions(mat)
        def sample(kind,sampler):
            expr=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionTextureSample)
            expr.set_editor_property('texture',textures[kind]);expr.set_editor_property('sampler_type',sampler)
            return expr
        base=sample('BaseColor',u.MaterialSamplerType.SAMPLERTYPE_COLOR)
        normal=sample('Normal',u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        orm=sample('ORM',u.MaterialSamplerType.SAMPLERTYPE_MASKS)
        for node,output,prop in [(base,'RGB',u.MaterialProperty.MP_BASE_COLOR),(normal,'RGB',u.MaterialProperty.MP_NORMAL),
            (orm,'R',u.MaterialProperty.MP_AMBIENT_OCCLUSION),(orm,'G',u.MaterialProperty.MP_ROUGHNESS),(orm,'B',u.MaterialProperty.MP_METALLIC)]:
            assert u.MaterialEditingLibrary.connect_material_property(node,output,prop),str(prop)
        mat.set_editor_property('tangent_space_normal',True)
        u.MaterialEditingLibrary.recompile_material(mat);u.EditorAssetLibrary.save_loaded_asset(mat)
        slot.set_editor_property('material_interface',mat)
        report.append({'asset':asset,'set':setname,'material':dest+'/'+name})
    mesh.set_editor_property('static_materials',slots);u.EditorAssetLibrary.save_loaded_asset(mesh)
u.EditorAssetLibrary.save_directory('/Game/Bunker',only_if_is_dirty=True,recursive=True)
(ROOT/'logs/painter_unreal.json').write_text(json.dumps({'materials':report,'texture_count':len(report)*3,'normal_format':'DirectX','mapping':'UV0'},indent=2))
u.log_warning('PAINTER_UNREAL_OK '+str(len(report)))
