"""Use Unreal's normal-map decoder and tangent basis rather than raw compressed samples."""
from pathlib import Path
import unreal as u
u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker');D='/Game/Bunker/ReferenceRoom';E=u.MaterialEditingLibrary
for name in ('Concrete','Paint','Steel','Rubber','Fabric','Wood','Ivory','Paper','Amber','Light'):
 m=u.load_asset(D+'/Materials/M_Ref_'+name)
 old=E.get_material_property_input_node(m,u.MaterialProperty.MP_NORMAL)
 if old:E.delete_material_expression(m,old)
 uv=E.create_material_expression(m,u.MaterialExpressionTextureCoordinate);uv.set_editor_property('coordinate_index',1)
 tex=E.create_material_expression(m,u.MaterialExpressionTextureSample);tex.set_editor_property('texture',u.load_asset(D+'/Textures/T_Ref_'+name+'_Normal'));tex.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL);E.connect_material_expressions(uv,'',tex,'Coordinates')
 n=E.create_material_expression(m,u.MaterialExpressionCustom);n.set_editor_property('code','return normalize(float3(N.xy*.25,max(N.z,.1)));');n.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3);entry=u.CustomInput();entry.set_editor_property('input_name','N');n.set_editor_property('inputs',[entry]);E.connect_material_expressions(tex,'RGB',n,'N');E.connect_material_property(n,'',u.MaterialProperty.MP_NORMAL);m.set_editor_property('tangent_space_normal',True);E.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
R=Path(__file__).resolve().parents[1];exec(compile((R/'scripts/style_reference_doors.py').read_text(),str(R/'scripts/style_reference_doors.py'),'exec'));u.log_warning('REFERENCE_NATIVE_NORMALS_OK')
