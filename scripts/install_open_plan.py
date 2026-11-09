"""Separate Unreal comparison map; original map and saves remain intact."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];dest='/Game/Bunker/Lvl_Bunker_OpenPlan';original='/Game/Bunker/Lvl_Bunker'
if u.EditorAssetLibrary.does_asset_exist(dest):u.EditorAssetLibrary.delete_asset(dest)
assert u.EditorAssetLibrary.duplicate_asset(original,dest)
assert u.EditorLevelLibrary.load_level(dest)
actors=list(u.EditorLevelLibrary.get_all_level_actors())
base=next(a for a in actors if a.get_actor_label()=='Bunker_B1_Merged');c=base.static_mesh_component
materials={str(n):c.get_material(i) for i,n in enumerate(c.get_material_slot_names())}
t=u.AssetImportTask();t.filename=str(R/'exports/Bunker_OpenPlanShell.fbx');t.destination_path='/Game/Bunker/OpenPlan';t.destination_name='SM_OpenPlanShell';t.automated=True;t.replace_existing=True;t.save=True
o=u.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.import_as_skeletal=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=o
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);m=u.load_asset('/Game/Bunker/OpenPlan/SM_OpenPlanShell');m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
slots=list(m.get_editor_property('static_materials'))
for slot in slots:slot.set_editor_property('material_interface',materials[str(slot.material_slot_name)])
m.set_editor_property('static_materials',slots);c.set_static_mesh(m)
for i,n in enumerate(c.get_material_slot_names()):c.set_material(i,materials[str(n)])
u.EditorAssetLibrary.save_loaded_asset(m)
opened_positions=[(1060,-740),(690,-125),(1895,-540),(2445,-1190),(175,-1190),(1295,-1610),(1295,-1190),(695,-1190)]
disabled=[];deleted=[];native_before={}
for a in actors:
 n=a.get_actor_label();p=a.get_actor_location()
 if a.get_class().get_name().startswith('Bunker'):native_before[a.get_name()]=list(p.to_tuple())
 if a.get_class().get_name()=='BunkerDoor' and n in ['INT_Door_'+v for v in ('ConvivenciaN','ConvivenciaW','CozinhaN','DespensaS','EnfermariaS','OficinaN','OficinaS','Radio_ComandoS')]:
  a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.set_folder_path('OpenPlan/Portas_Legadas_Inativas');disabled.append(a.get_name())
 if n.startswith(('REF_Panel_East','REF_Panel_West','REF_Panel_South','REF_CoveFixture','REF_CoveLight')):
  u.EditorLevelLibrary.destroy_actor(a);deleted.append(n)
# A backing panel, not a new enclosed room, supports the existing dart interaction.
screen=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(1515,-705,110));screen.set_actor_label('OP_DartScreen');screen.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));screen.set_actor_scale3d(u.Vector(1.2,.12,2.2));screen.static_mesh_component.set_material(0,u.load_asset('/Game/Bunker/ReferenceRoom/Materials/M_Ref_Paint'));screen.set_folder_path('OpenPlan/Arquitetura')
# Leave a 2 m circulation route clearly legible without new full-height partitions.
for x,y in [(1150,-980),(1900,-800),(2400,-980),(750,-1710)]:
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.PointLight,u.Vector(x,y,260));a.set_actor_label(f'OP_Circulation_{x}_{y}');a.light_component.set_editor_property('intensity_units',u.LightUnits.LUMENS);a.light_component.set_intensity(500);a.light_component.set_attenuation_radius(650);a.light_component.set_cast_shadows(False);a.light_component.set_light_color(u.LinearColor(.72,.8,1));a.set_folder_path('OpenPlan/Luzes_Preview')
assert len(disabled)==8,(disabled,'Expected eight former interior doors')
native_after={a.get_name():list(a.get_actor_location().to_tuple()) for a in u.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name().startswith('Bunker')}
assert native_before==native_after,'Native identities/transforms changed'
u.EditorLevelLibrary.save_current_level()
exec(compile((R/'scripts/refine_open_plan.py').read_text(),str(R/'scripts/refine_open_plan.py'),'exec'))
(R/'logs/open_plan_unreal.json').write_text(json.dumps({'map':dest,'inactive_legacy_doors':disabled,'removed_decorative_partitions':deleted,'native_actor_roots_preserved':True,'original_map_preserved':True,'campaign_saves_disabled_by_review_launcher':True},indent=2));u.log_warning('OPEN_PLAN_INSTALLED_OK')
