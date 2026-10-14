"""Apply original PBR maps with world-space triplanar mapping to all bunker assets."""
import json
from pathlib import Path
import unreal as u

ROOT = Path(__file__).resolve().parents[1]
DEST = '/Game/Bunker/Textures'
u.EditorAssetLibrary.make_directory(DEST)
textures = {}
for name in ('Concrete','PaintedMetal','Wood','Fabric','Floor','Steel'):
    for kind in ('BaseColor','Normal','ORM'):
        stem = f'T_{name}_{kind}'
        task = u.AssetImportTask()
        task.filename = str(ROOT / 'assets/textures' / (stem + '.png'))
        task.destination_path = DEST
        task.automated = True
        task.replace_existing = True
        task.save = True
        u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        tex = u.load_asset(f'{DEST}/{stem}')
        tex.set_editor_property('srgb', kind == 'BaseColor')
        if kind == 'Normal': tex.set_editor_property('compression_settings', u.TextureCompressionSettings.TC_NORMALMAP)
        elif kind == 'ORM': tex.set_editor_property('compression_settings', u.TextureCompressionSettings.TC_MASKS)
        u.EditorAssetLibrary.save_loaded_asset(tex)
        textures[name,kind] = tex

def node(mat, cls, x=0, y=0):
    return u.MaterialEditingLibrary.create_material_expression(mat, cls, x, y)

def custom(mat, code, inputs):
    expr = node(mat, u.MaterialExpressionCustom)
    expr.set_editor_property('code', code)
    expr.set_editor_property('output_type', u.CustomMaterialOutputType.CMOT_FLOAT3)
    entries=[]
    for name, source in inputs:
        entry = u.CustomInput()
        entry.set_editor_property('input_name', name)
        entries.append(entry)
    expr.set_editor_property('inputs', entries)
    for name, source in inputs: u.MaterialEditingLibrary.connect_material_expressions(source, '', expr, name)
    return expr

sample = '''float3 w=pow(abs(N),4); w/=max(w.x+w.y+w.z,0.001);
float3 p=P/Scale;
return Texture2DSample(T,TSampler,p.yz).rgb*w.x + Texture2DSample(T,TSampler,p.xz).rgb*w.y + Texture2DSample(T,TSampler,p.xy).rgb*w.z;'''

mapping = {
 'M_B1_Concrete':('Concrete',200), 'M_B1_Floor':('Floor',100),
 'M_B1_Door':('PaintedMetal',120), 'M_B1_Furniture':('Wood',120),
 'M_B1_Medical':('PaintedMetal',150), 'M_B1_Social':('Floor',120),
 'M_B1_Steel':('Steel',100), 'M_B1_Technical':('Floor',100),
 'M_B2_Concrete':('Concrete',200), 'M_B2_DarkSteel':('Steel',100),
 'M_B2_ModuleWhite':('Concrete',200), 'M_B2_Wood':('Wood',120),
 'M_B2_BedFabric':('Fabric',55), 'M_B2_UtilityGreen':('PaintedMetal',120),
 'M_EXT_Mercado':('Concrete',200), 'M_EXT_Asphalt':('Concrete',300),
}
for name, (surface, scale_cm) in mapping.items():
    mat=u.load_asset('/Game/Bunker/Materials/'+name)
    if not mat: raise RuntimeError('Missing material '+name)
    u.MaterialEditingLibrary.delete_all_material_expressions(mat)
    pos=node(mat,u.MaterialExpressionWorldPosition)
    normal=node(mat,u.MaterialExpressionVertexNormalWS)
    scale=node(mat,u.MaterialExpressionConstant)
    scale.set_editor_property('r',float(scale_cm))
    for kind, prop in (('BaseColor',u.MaterialProperty.MP_BASE_COLOR),('ORM',None)):
        tex=node(mat,u.MaterialExpressionTextureObject)
        tex.set_editor_property('texture',textures[surface,kind])
        result=custom(mat,sample,[('T',tex),('P',pos),('N',normal),('Scale',scale)])
        if prop: u.MaterialEditingLibrary.connect_material_property(result,'',prop)
        else:
            for channel, prop in (('r',u.MaterialProperty.MP_AMBIENT_OCCLUSION),('g',u.MaterialProperty.MP_ROUGHNESS),('b',u.MaterialProperty.MP_METALLIC)):
                mask=node(mat,u.MaterialExpressionComponentMask)
                mask.set_editor_property(channel,True)
                # ComponentMask defaults can include R/G, clear explicitly.
                for other in ('r','g','b','a'):
                    mask.set_editor_property(other,other==channel)
                if not u.MaterialEditingLibrary.connect_material_expressions(result,'',mask,''):
                    raise RuntimeError('Could not connect ORM mask for '+name)
                u.MaterialEditingLibrary.connect_material_property(mask,'',prop)
    tex=node(mat,u.MaterialExpressionTextureObject)
    tex.set_editor_property('texture',textures[surface,'Normal'])
    ncode='''float3 w=pow(abs(N),4); w/=max(w.x+w.y+w.z,0.001); float3 p=P/Scale;
float3 a=Texture2DSample(T,TSampler,p.yz).xyz;
float3 b=Texture2DSample(T,TSampler,p.xz).xyz;
float3 c=Texture2DSample(T,TSampler,p.xy).xyz;
a.xy=a.xy*2-1; a.z=sqrt(saturate(1-dot(a.xy,a.xy)));
b.xy=b.xy*2-1; b.z=sqrt(saturate(1-dot(b.xy,b.xy)));
c.xy=c.xy*2-1; c.z=sqrt(saturate(1-dot(c.xy,c.xy)));
return normalize(float3(a.z*sign(N.x),a.x,a.y)*w.x+float3(b.x,b.z*sign(N.y),b.y)*w.y+float3(c.x,c.y,c.z*sign(N.z))*w.z);'''
    n=custom(mat,ncode,[('T',tex),('P',pos),('N',normal),('Scale',scale)])
    mat.set_editor_property('tangent_space_normal',False)
    u.MaterialEditingLibrary.connect_material_property(n,'',u.MaterialProperty.MP_NORMAL)
    u.MaterialEditingLibrary.recompile_material(mat)
    u.EditorAssetLibrary.save_loaded_asset(mat)

u.EditorAssetLibrary.save_directory('/Game/Bunker',only_if_is_dirty=True,recursive=True)

# Assign upholstery to soft furnishings rather than painted utility metal.
u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
fabric = u.load_asset('/Game/Bunker/Materials/M_B2_BedFabric')
for actor in u.EditorLevelLibrary.get_all_level_actors():
    label=actor.get_actor_label()
    # Exterior shadowless lamps must not shine through the bunker ceiling.
    # Separate lighting channels preserve warm interiors without costly shadows.
    if label.startswith('EXT_'):
        comp=actor.get_component_by_class(u.StaticMeshComponent)
        if comp: comp.set_editor_property('lighting_channels',u.LightingChannels(False,True,False))
    if isinstance(actor,u.PointLight) and actor.get_actor_location().z > 400:
        actor.point_light_component.set_editor_property('lighting_channels',u.LightingChannels(False,True,False))
    if label.startswith('Social_Sofa') or (label.startswith('Social_Chair') and '_Back' in label):
        comp=actor.get_component_by_class(u.StaticMeshComponent)
        if comp: comp.set_material(0,fabric)
u.EditorLevelLibrary.save_current_level()
(ROOT/'logs/pbr_materials.json').write_text(json.dumps({'materials':len(mapping),'textures':18,'mapping':'world-space triplanar','resolution':512},indent=2))
u.log_warning('PBR_MATERIALS_OK '+str(len(mapping)))
