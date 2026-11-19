"""Import sampled Blender bone tracks without the failing skeletal-FBX exporter."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];D='/Game/Bunker/BedroomRest';A=u.AssetToolsHelpers.get_asset_tools();M=json.loads((R/'exports/bedroom_rest_animation.json').read_text())
u.EditorAssetLibrary.make_directory(D)
factory=u.AnimSequenceFactory();factory.set_editor_property('target_skeleton',u.load_asset(M['skeleton']));factory.set_editor_property('preview_skeletal_mesh',u.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'))
seq=u.load_asset(D+'/A_Bedroom_Rest') or A.create_asset('A_Bedroom_Rest',D,u.AnimSequence,factory);assert seq
ctrl=seq.get_editor_property('controller');assert ctrl
ctrl.open_bracket(u.Text('Import editable Blender resting action'),False);ctrl.remove_all_bone_tracks(False)
rate=u.FrameRate();rate.numerator=M['fps'];rate.denominator=1;ctrl.set_frame_rate(rate,False)
frames=u.FrameNumber();frames.value=M['frames']-1;ctrl.set_number_of_frames(frames,False)
for name,t in M['tracks'].items():
 assert ctrl.add_bone_curve(name,False)
 assert ctrl.set_bone_track_keys(name,[u.Vector(*p) for p in t['positions']],[u.Quat(*q) for q in t['rotations']],[u.Vector(*s) for s in t['scales']],False)
ctrl.close_bracket(False);u.EditorAssetLibrary.save_loaded_asset(seq)
Map=D+'/Lvl_Bedroom_Study_Rest'
if not u.EditorAssetLibrary.does_asset_exist(Map):assert u.EditorAssetLibrary.duplicate_asset('/Game/Bunker/BedroomCabinet/Lvl_Bedroom_Study_Cabinet',Map)
u.EditorLevelLibrary.load_level(Map);u.EditorLevelLibrary.save_current_level();u.EditorAssetLibrary.save_directory(D,only_if_is_dirty=True,recursive=True)
(R/'logs/bedroom_rest_import.json').write_text(json.dumps({'map':Map,'animation':seq.get_path_name(),'tracks':len(M['tracks']),'frames':M['frames'],'fps':M['fps'],'original_maps_saved':False},indent=2));u.log('C13_REST_ANIMATION_IMPORT_OK')
