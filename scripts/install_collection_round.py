"""Isolated MVP map. Existing review maps and their inventory identities are untouched."""
from pathlib import Path
import unreal as u,json,wave,math,struct
R=Path(__file__).resolve().parents[1];target='/Game/Bunker/Lvl_CollectionRound'
if not u.EditorAssetLibrary.does_asset_exist(target):assert u.EditorAssetLibrary.duplicate_asset('/Game/Bunker/Lvl_Bunker_OpenPlan',target)
u.EditorLevelLibrary.load_level(target)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
 if a.get_actor_label()=='INT_Door_AntecamaraS':a.set_editor_property('tags',[u.Name('C13_CollectionGate')])
existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
for i,(x,y) in enumerate(((2500,1300),(2600,1300),(2700,1300),(2800,1300))):
 a=existing.get('ROUND_PlayerStart_'+str(i)) or actors.spawn_actor_from_class(u.PlayerStart,u.Vector(x,y,410),u.Rotator(yaw=90));a.set_actor_label('ROUND_PlayerStart_'+str(i));a.set_actor_location(u.Vector(x,y,410),False,False);a.set_editor_property('player_start_tag','C13_RoundMarket')
templates={a.get_editor_property('item_type'):a for a in actors.get_all_level_actors() if a.get_actor_label() in ('INT_Water_01','INT_Can_01','INT_Medkit','INT_Battery','INT_Tool')}
for a in actors.get_all_level_actors():
 if a.get_actor_label() in ('EXT_Shelf_2_2250','EXT_Shelf_3_2250'):
  p=a.get_actor_location();p.x=2120;a.set_actor_location(p,False,False)
geometry=[]
floor=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='EXT_SupermarketFloor'),None)
floor_mat=floor.static_mesh_component.get_material(0) if floor else u.load_asset('/Game/Bunker/ReferenceRoom/Materials/M_Ref_Concrete')
if floor:actors.destroy_actor(floor)
def cube(label,loc,dim,material):
 a=existing.get(label) or actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*loc));a.set_actor_label(label);a.set_actor_location(u.Vector(*loc),False,False);a.set_actor_scale3d(u.Vector(*(d/100 for d in dim)));a.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));a.static_mesh_component.set_material(0,material);geometry.append({'name':label,'position_cm':loc,'dimensions_cm':dim});return a
for name,x0,x1,y0,y1 in [('Left',550,2440,-600,2400),('Right',2660,4550,-600,2400),('Bottom',2440,2660,-600,20),('Top',2440,2660,820,2400)]:cube('ROUND_MarketFloor_'+name,((x0+x1)/2,(y0+y1)/2,300),(x1-x0,y1-y0,25),floor_mat)
rail_mat=u.load_asset('/Game/Bunker/ReferenceRoom/Materials/M_Ref_Steel')
for x in (2420,2680):
 cube('ROUND_Rail_'+str(x),(x,420,412.5),(6,800,6),rail_mat)
 for y in (40,290,540,790):cube(f'ROUND_RailPost_{x}_{y}',(x,y,362.5),(6,6,100),rail_mat)
cube('ROUND_RailEnd',(2550,20,412.5),(260,6,6),rail_mat)
for i,(y,z) in enumerate(((650,280),(450,230),(200,130))):
 cube(f'ROUND_StairHousing_{i}',(2469,y,z),(12,45,18),rail_mat)
 lens=cube(f'ROUND_StairLens_{i}',(2477,y,z),(4,35,8),u.load_asset('/Game/Bunker/ReferenceRoom/Materials/M_Ref_Light'));lens.static_mesh_component.set_editor_property('lighting_channels',u.LightingChannels(True,False,True))
 light=existing.get(f'ROUND_StairLight_{i}') or actors.spawn_actor_from_class(u.PointLight,u.Vector(2490,y,z));light.set_actor_label(f'ROUND_StairLight_{i}');c=light.point_light_component;c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(400);c.set_attenuation_radius(450);c.set_cast_shadows(False);c.set_editor_property('lighting_channels',u.LightingChannels(True,False,True));c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3800)
# The old seat crossed the central walking lane. Keep it, aligned to the side.
for a in actors.get_all_level_actors():
 n=a.get_actor_label()
 if n=='Airlock_Bench' or n.startswith('Airlock_BenchLeg_'):
  y=-500 if n=='Airlock_Bench' else -500+(int(n.rsplit('_',1)[1])-2470)
  z=48 if n=='Airlock_Bench' else 23
  a.set_actor_location(u.Vector(2415,y,z),False,False);a.set_actor_rotation(u.Rotator(yaw=90),False)
  geometry.append({'name':'ROUND_'+n,'position_cm':[2415,y,z],'dimensions_cm':[55,230,12] if n=='Airlock_Bench' else [42,8,46]})
rows=[]
for t,(x,y) in enumerate(((1450,1430),(2250,1000),(3050,570))):
 a=existing.get('ROUND_SupplyTable_'+str(t)) or actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,312.0));a.set_actor_label('ROUND_SupplyTable_'+str(t));table_mesh=u.load_asset('/Game/Bunker/ReferenceRoom/Meshes/SM_Ref_Table');a.static_mesh_component.set_static_mesh(table_mesh);bounds=table_mesh.get_bounds();root_z=312.5-(bounds.origin.z-bounds.box_extent.z);a.set_actor_location(u.Vector(x,y,root_z),False,False);top_z=root_z+bounds.origin.z+bounds.box_extent.z
 light=existing.get('ROUND_SupplyLight_'+str(t)) or actors.spawn_actor_from_class(u.SpotLight,u.Vector(x,y,610),u.Rotator(pitch=-90));light.set_actor_label('ROUND_SupplyLight_'+str(t));c=light.spot_light_component;c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(1500);c.set_attenuation_radius(650);c.set_editor_property('inner_cone_angle',50);c.set_editor_property('outer_cone_angle',80);c.set_cast_shadows(False);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3500)
 fixture=existing.get('ROUND_SupplyFixture_'+str(t)) or actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,620));fixture.set_actor_label('ROUND_SupplyFixture_'+str(t));fixture.static_mesh_component.set_static_mesh(u.load_asset('/Game/Bunker/ReferenceRoom/Meshes/SM_Ref_Lamp'));fixture.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 for i,key in enumerate(('Water','Food','Medkit','Battery')):
  src=templates[u.Name(key)];b=existing.get(f'ROUND_Loot_{t}_{i}') or actors.spawn_actor_from_class(src.get_class(),u.Vector(x-40+i*27,y,386.2));b.mesh.set_static_mesh(src.mesh.get_editor_property('static_mesh'));b.set_actor_scale3d(src.get_actor_scale3d());b.set_editor_property('interaction',src.get_editor_property('interaction'));b.set_editor_property('item_type',src.get_editor_property('item_type'));b.set_editor_property('display_name',src.get_editor_property('display_name'));b.set_editor_property('action_text',src.get_editor_property('action_text'));b.set_actor_label(f'ROUND_Loot_{t}_{i}');item_bounds=b.mesh.get_editor_property('static_mesh').get_bounds();item_z=top_z-(item_bounds.origin.z-item_bounds.box_extent.z)*b.get_actor_scale3d().z+.05;b.set_actor_location(u.Vector(x-40+i*27,y,item_z),False,False);b.set_editor_property('active',True);b.set_editor_property('tags',[u.Name('C13_RoundLootFirst')] if t==0 and i==0 else [u.Name('C13_RoundLoot')]);rows.append({'type':key,'position':[x-40+i*27,y,item_z],'tabletop_z':top_z,'support_clearance_cm':.05})
# Original synthetic siren asset, not a downloaded sound or microphone recording.
audio=R/'assets/round';audio.mkdir(parents=True,exist_ok=True);wav=audio/'S_CollectionAlert.wav';rate=48000
with wave.open(str(wav),'wb') as w:
 w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<h',int(9000*math.sin(2*math.pi*(560*t/rate+65*(t/rate)**2))*min(1,t/1500)*max(0,min(1,(rate*1.2-t)/2000)))) for t in range(int(rate*1.2))))
task=u.AssetImportTask();task.filename=str(wav);task.destination_path='/Game/Bunker/Round/Audio';task.automated=True;task.replace_existing=True;task.save=True;u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
rules=u.load_asset('/Game/Bunker/Data/DA_SurvivalRules');rules.set_editor_property('collection_seconds',90);rules.set_editor_property('emergency_release_seconds',12);rules.set_editor_property('emergency_release_energy',15);u.EditorAssetLibrary.save_loaded_asset(rules)
u.EditorLevelLibrary.save_current_level();(R/'logs/round_map_install.json').write_text(json.dumps({'map':target,'market_pickups':rows,'geometry':geometry,'duration_seconds':90,'save_scope':'C13_MvpRoundSolo/Coop; test uses C13_TestRound','old_maps_preserved':True},indent=2));u.log_warning('C13_ROUND_MAP_INSTALLED')
