"""Import a separate art study map. Never load/save an existing bunker map."""
from pathlib import Path
import json,unreal as u
R=Path(__file__).resolve().parents[1];D='/Game/Bunker/BedroomStudy';M=json.loads((R/'exports/bedroom_study/manifest.json').read_text())
A=u.AssetToolsHelpers.get_asset_tools();E=u.MaterialEditingLibrary
u.EditorAssetLibrary.make_directory(D)
if u.EditorAssetLibrary.does_asset_exist(D+'/Lvl_Bedroom_Study'):
 u.EditorLevelLibrary.load_level(D+'/Lvl_Bedroom_Study')
 for a in u.EditorLevelLibrary.get_all_level_actors():
  if a.get_actor_label().startswith(('SM_Bedroom_','Bedroom_')) or isinstance(a,(u.RectLight,u.PostProcessVolume,u.PlayerStart)):u.EditorLevelLibrary.destroy_actor(a)
else:u.EditorLevelLibrary.new_level(D+'/Lvl_Bedroom_Study')
def node(m,c):return E.create_material_expression(m,c,0,0)
normals={}
for kind in ('Coat','Weave'):
 name='T_Bedroom_'+kind+'_Normal';t=u.AssetImportTask();t.filename=str(R/'exports/bedroom_study'/(name+'.png'));t.destination_path=D+'/Textures';t.automated=True;t.replace_existing=True;t.save=True;A.import_asset_tasks([t]);tex=u.load_asset(D+'/Textures/'+name);tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);u.EditorAssetLibrary.save_loaded_asset(tex);normals[kind]=tex
mats={};bounds={}
for n,(rgb,metal,rough) in M['palette'].items():
 m=u.load_asset(D+'/Materials/M_Bedroom_'+n) or A.create_asset('M_Bedroom_'+n,D+'/Materials',u.Material,u.MaterialFactoryNew());E.delete_all_material_expressions(m)
 c=node(m,u.MaterialExpressionConstant3Vector);c.set_editor_property('constant',u.LinearColor(*rgb,1));E.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
 for value,prop in ((metal,u.MaterialProperty.MP_METALLIC),(rough,u.MaterialProperty.MP_ROUGHNESS)):
  v=node(m,u.MaterialExpressionConstant);v.set_editor_property('r',value);E.connect_material_property(v,'',prop)
 if n in ('Teal','Linen','Ivory','Green'):
  tex=node(m,u.MaterialExpressionTextureSample);tex.set_editor_property('texture',normals['Weave' if n in ('Teal','Linen') else 'Coat']);tex.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL);uv=node(m,u.MaterialExpressionTextureCoordinate);uv.set_editor_property('coordinate_index',1);E.connect_material_expressions(uv,'',tex,'UVs');E.connect_material_property(tex,'RGB',u.MaterialProperty.MP_NORMAL)
 if n=='Light':
  c=node(m,u.MaterialExpressionConstant3Vector);c.set_editor_property('constant',u.LinearColor(3,2.34,1.32,1));E.connect_material_property(c,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 E.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m);mats[n]=m
for name in M['meshes']:
 t=u.AssetImportTask();t.filename=str(R/'exports/bedroom_study'/(name+'.fbx'));t.destination_path=D+'/Meshes';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 opts=u.FbxImportUI();opts.import_mesh=True;opts.import_as_skeletal=False;opts.import_materials=False;opts.import_textures=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.generate_lightmap_u_vs=False;opts.static_mesh_import_data.auto_generate_collision=False;t.options=opts;A.import_asset_tasks([t]);mesh=u.load_asset(D+'/Meshes/'+name)
 if not mesh:raise RuntimeError('Import failed '+name)
 bounds[name]=list((mesh.get_bounds().box_extent*2).to_tuple())
 slots=list(mesh.get_editor_property('static_materials'))
 for s in slots:s.set_editor_property('material_interface',mats[str(s.material_slot_name).removeprefix('M_Bedroom_')])
 mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);u.EditorAssetLibrary.save_loaded_asset(mesh)
 if name=='SM_Bedroom_Bed':
  cls=u.load_class(None,'/Script/Condominio13.BunkerInteractable');actor=u.EditorLevelLibrary.spawn_actor_from_class(cls,u.Vector(117,-314,0));actor.set_editor_property('interaction',u.BunkerInteraction.BED);actor.set_editor_property('display_name',u.Text('Cama — quarto de referência'));actor.set_editor_property('action_text',u.Text('descansar'));comp=actor.get_editor_property('mesh');comp.set_static_mesh(mesh)
 else:
  actor=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0));actor.static_mesh_component.set_static_mesh(mesh)
  if name.endswith(('Details','Signs','Fixtures')):actor.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 actor.set_actor_label(name)
assert 450<bounds['SM_Bedroom_Architecture'][0]<470 and 620<bounds['SM_Bedroom_Architecture'][1]<635,'Unexpected FBX scale/axes'
world=u.EditorLevelLibrary.get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Script/Condominio13.BunkerGameMode'))
u.EditorLevelLibrary.spawn_actor_from_class(u.PlayerStart,u.Vector(285,-90,100),u.Rotator(yaw=-130))
for i,(p,intensity,target) in enumerate([((140,-430,240),1100,(140,-270,80)),((35,-200,230),900,(140,-210,70)),((310,-140,260),1300,(240,-240,10))]):
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.RectLight,u.Vector(*p));a.set_actor_label('Bedroom_Practical_'+str(i));a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(*p),u.Vector(*target)),False);c=a.get_component_by_class(u.RectLightComponent);c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_editor_property('intensity',intensity);c.set_editor_property('attenuation_radius',650);c.set_editor_property('source_width',100);c.set_editor_property('source_height',15);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3400 if i<2 else 3900);c.set_editor_property('cast_shadows',True)
# Fixed exposure for the isolated evaluation only; original levels untouched.
pp=u.EditorLevelLibrary.spawn_actor_from_class(u.PostProcessVolume,u.Vector());pp.set_editor_property('unbound',True);p=pp.get_editor_property('settings');p.set_editor_property('override_auto_exposure_method',True);p.set_editor_property('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL);p.set_editor_property('override_auto_exposure_apply_physical_camera_exposure',True);p.set_editor_property('auto_exposure_apply_physical_camera_exposure',False);p.set_editor_property('override_auto_exposure_bias',True);p.set_editor_property('auto_exposure_bias',-4);pp.set_editor_property('settings',p)
u.EditorLevelLibrary.save_current_level();u.EditorAssetLibrary.save_directory(D,only_if_is_dirty=True,recursive=True)
actors=u.EditorLevelLibrary.get_all_level_actors();(R/'logs/bedroom_import.json').write_text(json.dumps({'map':D+'/Lvl_Bedroom_Study','actors':len(actors),'mesh_groups':len(M['meshes']),'bounds_cm':bounds,'bed_native':True,'original_maps_saved':False},indent=2));u.log('C13_BEDROOM_IMPORT_OK')
