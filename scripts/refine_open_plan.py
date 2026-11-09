"""Unify the comparison hall and remove obsolete fixtures, only in its own map."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker_OpenPlan')
D='/Game/Bunker/ReferenceRoom/';channels=u.LightingChannels(False,False,True)
mats={k:u.load_asset(D+'Materials/M_Ref_'+k) for k in ('Concrete','Paint','Steel','Rubber','Ivory','Light','Amber')}
actors=list(u.EditorLevelLibrary.get_all_level_actors());removed=[]
for a in actors:
 n=a.get_actor_label();p=a.get_actor_location()
 if n.startswith(('OP_Circulation_','OP_HallLight','OP_HallFixture','OP_HallFill','B2_SocialAmber','B2_WhiteModule')):
  removed.append(n);u.EditorLevelLibrary.destroy_actor(a);continue
 if n in ('INT_Door_ConvivenciaN','INT_Door_ConvivenciaW','INT_Door_CozinhaN','INT_Door_DespensaS','INT_Door_EnfermariaS','INT_Door_OficinaN','INT_Door_OficinaS','INT_Door_Radio_ComandoS'):
  a.set_editor_property('tags',[u.Name('C13_OpenPlanRetiredDoor')]);a.mesh.set_visibility(False,True);a.mesh.set_hidden_in_game(True,True)
 if isinstance(a,u.PointLight) and p.z<290 and not n.startswith('REF_'):a.point_light_component.set_intensity(0)
 for c in a.get_components_by_class(u.StaticMeshComponent):
  if p.z<290 or n=='Bunker_B1_Merged':c.set_editor_property('lighting_channels',channels)
  if n.startswith('B2_'):
   key='Amber' if 'FloorStrip' in n or 'SafetyBand' in n else 'Light' if 'CorridorLight' in n else 'Steel' if 'Duct' in n or 'Pipe' in n else 'Concrete'
   for i in range(c.get_num_materials()):c.set_material(i,mats[key])
  if n=='Bunker_B1_Merged':
   for i,slot in enumerate(c.get_material_slot_names()):
    key={'M_Concrete':'Concrete','M_Floor':'Rubber','M_Technical':'Rubber','M_Social':'Rubber','M_Medical':'Rubber','M_Door':'Paint','M_Steel':'Steel','M_Furniture':'Paint'}.get(str(slot),'Concrete');c.set_material(i,mats[key])
 if n in ('REF_Floor','REF_Ceiling'):
  a.set_actor_location(u.Vector(1400,-1000,2.6 if n=='REF_Floor' else 286),False,False);a.set_actor_scale3d(u.Vector(27.4,19.4,1 if n=='REF_Floor' else 2));a.static_mesh_component.set_material(0,mats['Rubber' if n=='REF_Floor' else 'Concrete'])
 if n=='REF_Exposure':a.set_editor_property('unbound',True);a.set_editor_property('priority',100)
 if n=='OP_DartScreen':a.set_actor_location(u.Vector(1515,-705,173),False,False);a.set_actor_scale3d(u.Vector(.6,.08,.6));a.static_mesh_component.set_material(0,mats['Paint'])
 if n.startswith('OP_DartStand'):u.EditorLevelLibrary.destroy_actor(a)
for n,loc,scale in [('Post',(1515,-705,86),(.06,.06,1.7)),('Base',(1515,-705,4.1),(.5,.5,.03))]:
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*loc));a.set_actor_label('OP_DartStand'+n);c=a.static_mesh_component;c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));a.set_actor_scale3d(u.Vector(*scale));c.set_material(0,mats['Steel']);c.set_editor_property('lighting_channels',channels)
for i,(x,y,temp) in enumerate(((1850,-300,3300),(2200,-900,3900),(2500,-1450,3900),(1400,-1400,3900),(750,-1400,3500),(250,-1400,3900),(1100,-950,3500))):
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.SpotLight,u.Vector(x,y,268),u.Rotator(pitch=-90));a.set_actor_label('OP_HallLight'+str(i));c=a.spot_light_component;c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(750);c.set_attenuation_radius(700);c.set_editor_property('inner_cone_angle',50);c.set_editor_property('outer_cone_angle',80);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',temp);c.set_cast_shadows(False);c.set_editor_property('lighting_channels',channels)
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,280));a.set_actor_label('OP_HallFixture'+str(i));c=a.static_mesh_component;c.set_static_mesh(u.load_asset(D+'Meshes/SM_Ref_Lamp'));c.set_editor_property('lighting_channels',channels);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
for i,(x,y) in enumerate(((1100,-600),(1300,-1000),(2100,-900),(800,-1500))):
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.PointLight,u.Vector(x,y,230));a.set_actor_label('OP_HallFill'+str(i));c=a.point_light_component;c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(400);c.set_attenuation_radius(700);c.set_cast_shadows(False);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3800);c.set_editor_property('lighting_channels',channels)
u.EditorLevelLibrary.save_current_level();(R/'logs/open_plan_finish.json').write_text(json.dumps({'removed_obsolete_finish':removed,'continuous_floor_and_ceiling':True,'lighting_unified':True,'retired_door_runtime_tag':True},indent=2));u.log_warning('OPEN_PLAN_FINISH_OK')
