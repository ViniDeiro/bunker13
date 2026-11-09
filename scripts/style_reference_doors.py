"""Only common-room door surfaces; authoritative names, pivots and collision stay intact."""
import unreal as u
u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
D='/Game/Bunker/ReferenceRoom/Materials/'
for a in u.EditorLevelLibrary.get_all_level_actors():
 if a.get_actor_label().startswith('INT_Door_Convivencia'):
  for i in range(a.mesh.get_num_materials()):
   slot=str(a.mesh.get_material_slot_names()[i]);key='Steel' if 'Steel' in slot else 'Rubber' if 'Rubber' in slot else 'Amber' if 'Safety' in slot else 'Paint'
   a.mesh.set_material(i,u.load_asset(D+'M_Ref_'+key))
  a.mesh.set_editor_property('lighting_channels',u.LightingChannels(False,False,True))
u.EditorLevelLibrary.save_current_level();u.log_warning('REFERENCE_DOOR_STYLE_OK')
