"""Execute with Unreal's PythonScript commandlet after building the cloned project."""
import unreal

world = unreal.EditorLoadingAndSavingUtils.load_map("/Game/Bunker/Lvl_CollectionRound")
if not world:
    raise RuntimeError("Recovered expedition map could not be loaded")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
if len(actors) < 10:
    raise RuntimeError("Recovered map is unexpectedly empty")
paths = [
    "/Game/Bunker/Infrastructure/Meshes/SM_Infra_FuelCan",
    "/Game/Bunker/Infrastructure/Meshes/SM_Infra_RepairParts",
    "/Game/Bunker/Infrastructure/Meshes/SM_Infra_Filter",
    "/Game/Bunker/Data/DA_SurvivalRules",
    "/Game/Bunker/Materials/M_EXT_Asphalt",
]
for path in paths:
    if unreal.load_asset(path) is None:
        raise RuntimeError("Recovered dependency missing: " + path)
unreal.log("C13_REMOTE_RECOVERY map=1 actors={} dependencies={}".format(len(actors), len(paths)))
# Do not save the loaded world, enter play, reset fixtures or touch campaigns.
