"""Downward practical lights avoid unreal uplight through opaque lamp housings."""
from pathlib import Path
import unreal as u
R=Path(__file__).resolve().parents[1];u.EditorLevelLibrary.load_level('/Game/Bunker/Lvl_Bunker')
for a in list(u.EditorLevelLibrary.get_all_level_actors()):
 n=a.get_actor_label()
 if n in ('REF_Light0','REF_Light1','REF_Light2'):u.EditorLevelLibrary.destroy_actor(a)
 if n.startswith('REF_CoveLight'):a.point_light_component.set_editor_property('intensity',600)
for i,(x,y,temp,power) in enumerate(((1000,-330,3000,600),(1330,-530,3300,450),(1400,-150,3700,400))):
 a=u.EditorLevelLibrary.spawn_actor_from_class(u.SpotLight,u.Vector(x,y,268),u.Rotator(pitch=-90));a.set_actor_label(f'REF_Light{i}');a.set_folder_path('Convivencia_Reference/Iluminacao');c=a.spot_light_component;c.set_editor_property('mobility',u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_editor_property('intensity',power);c.set_editor_property('attenuation_radius',650);c.set_editor_property('inner_cone_angle',50);c.set_editor_property('outer_cone_angle',80);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',temp);c.set_editor_property('cast_shadows',True);c.set_editor_property('source_radius',12);c.set_editor_property('lighting_channels',u.LightingChannels(False,False,True))
u.EditorLevelLibrary.save_current_level();exec(compile((R/'scripts/snapshot_reference_scene.py').read_text(),str(R/'scripts/snapshot_reference_scene.py'),'exec'));u.log_warning('REFERENCE_PRACTICALS_FINAL_OK')
