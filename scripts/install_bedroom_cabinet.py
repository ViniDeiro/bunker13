"""New map only: retain the v001 study and all published bunker assets."""
from pathlib import Path
import unreal as u,json
R=Path(__file__).resolve().parents[1];D='/Game/Bunker/BedroomCabinet';Map=D+'/Lvl_Bedroom_Study_Cabinet';A=u.AssetToolsHelpers.get_asset_tools()
u.EditorAssetLibrary.make_directory(D)
if not u.EditorAssetLibrary.does_asset_exist(Map):
 assert u.EditorAssetLibrary.duplicate_asset('/Game/Bunker/BedroomStudy/Lvl_Bedroom_Study',Map)
u.EditorLevelLibrary.load_level(Map)
manifest=json.loads((R/'exports/bedroom_cabinet/manifest.json').read_text());meshes={}
for name in manifest['meshes']:
 t=u.AssetImportTask();t.filename=str(R/'exports/bedroom_cabinet'/(name+'.fbx'));t.destination_path=D+'/Meshes';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 o=u.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=False;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=o;A.import_asset_tasks([t]);m=u.load_asset(D+'/Meshes/'+name);assert m
 slots=list(m.get_editor_property('static_materials'))
 for s in slots:s.set_editor_property('material_interface',u.load_asset('/Game/Bunker/BedroomStudy/Materials/'+str(s.material_slot_name)))
 m.set_editor_property('static_materials',slots);m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);u.EditorAssetLibrary.save_loaded_asset(m);meshes[name]=m
for a in u.EditorLevelLibrary.get_all_level_actors():
 n=a.get_actor_label()
 if n in ('SM_Bedroom_Furniture','SM_Bedroom_Details'):a.static_mesh_component.set_static_mesh(meshes[n])
 if n in ('Bedroom_PhysicalCabinet','Bedroom_BounceProxy'):u.EditorLevelLibrary.destroy_actor(a)
cab=u.EditorLevelLibrary.spawn_actor_from_class(u.load_class(None,'/Script/Condominio13.BunkerReferenceCabinet'),u.Vector(373,-411,0));cab.set_actor_label('Bedroom_PhysicalCabinet');cab.set_editor_property('persistent_key','C13_Bedroom_Cabinet_v002');cab.set_editor_property('display_name',u.Text('Armário pessoal — quarto de referência'));cab.mesh.set_static_mesh(meshes['SM_Bedroom_CabinetBody']);cab.get_editor_property('leaf').set_static_mesh(meshes['SM_Bedroom_CabinetLeaf'])
for part in (cab.mesh,cab.get_editor_property('leaf')):part.set_editor_property('lighting_channels',u.LightingChannels(True,False,False))
items=[]
for i,kind in enumerate(('Water','Food')):
 guid,ok=u.GuidLibrary.parse_string_to_guid('C13000130000B00200000000'+f'{i+1:08X}');assert ok
 e=u.BunkerCabinetSeed();e.set_editor_property('id',guid);e.set_editor_property('item_type',kind);e.set_editor_property('name','Garrafa de água' if i==0 else 'Alimento enlatado');e.set_editor_property('storage_slot',6+i);e.set_editor_property('world_mesh',u.load_asset('/Game/Bunker/Items/'+kind+'/SM_Item_'+kind));e.set_editor_property('world_scale',u.Vector(1,1,1));items.append(e)
cab.set_editor_property('starting_items',items)
for kind in ('Open','Close'):cab.set_editor_property(kind.lower()+'_sound',u.load_asset('/Game/Bunker/ReferenceRoom/Audio/S_Cabinet_'+kind))
assert cab.get_editor_property('open_sound') and cab.get_editor_property('close_sound')
# Low-cost proxy for the practicals' wall bounce while the Mac profile has GI disabled.
fill=u.EditorLevelLibrary.spawn_actor_from_class(u.PointLight,u.Vector(400,-240,200));fill.set_actor_label('Bedroom_BounceProxy');light=fill.point_light_component;light.set_editor_property('mobility',u.ComponentMobility.MOVABLE);light.set_editor_property('intensity_units',u.LightUnits.LUMENS);light.set_editor_property('intensity',300);light.set_editor_property('attenuation_radius',400);light.set_editor_property('source_radius',35);light.set_editor_property('cast_shadows',False);light.set_editor_property('use_temperature',True);light.set_editor_property('temperature',3800)
# Two real spawn points; the engine chooses an unoccupied start.
if not any(a.get_actor_label()=='Bedroom_PlayerStart2' for a in u.EditorLevelLibrary.get_all_level_actors()):
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.PlayerStart,u.Vector(373,-175,100),u.Rotator(yaw=-90));a.set_actor_label('Bedroom_PlayerStart2')
u.EditorLevelLibrary.save_current_level();u.EditorAssetLibrary.save_directory(D,only_if_is_dirty=True,recursive=True)
assert cab.get_editor_property('persistent_key')!='C13_Reference_CommonCabinet_v1'
(R/'logs/bedroom_cabinet_import.json').write_text(json.dumps({'map':Map,'new_key':str(cab.get_editor_property('persistent_key')),'seed_items':len(items),'body_bounds_cm':list((meshes['SM_Bedroom_CabinetBody'].get_bounds().box_extent*2).to_tuple()),'legacy_map_saved':False},indent=2))
u.log('C13_BEDROOM_CABINET_IMPORT_OK')
