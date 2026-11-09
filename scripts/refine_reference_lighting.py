"""Quick exposure-only iteration; materials remain authored in install_reference_room.py."""
import unreal as u
u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
for a in u.EditorLevelLibrary.get_all_level_actors():
 if a.get_actor_label()=='REF_Exposure':
  p=a.get_editor_property('settings');p.set_editor_property('auto_exposure_bias',0.0);a.set_editor_property('settings',p)
u.EditorLevelLibrary.save_current_level()
