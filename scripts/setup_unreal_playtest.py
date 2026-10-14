"""Import the merged B1 bunker and create the playable Unreal level."""
import json
from pathlib import Path

import unreal


ROOT = Path(__file__).resolve().parents[1]
FBX = ROOT / "exports" / "Bunker_Playtest_Merged.fbx"
REPORT = ROOT / "logs" / "unreal_setup.json"
ASSET_DIR = "/Game/Bunker/Geometry"
MATERIAL_DIR = "/Game/Bunker/Materials"
LEVEL = "/Game/Bunker/Lvl_Bunker"

MATERIAL_COLORS = {
    "M_Concrete": (0.34, 0.36, 0.37),
    "M_Door": (0.34, 0.18, 0.07),
    "M_Floor": (0.20, 0.23, 0.24),
    "M_Furniture": (0.30, 0.23, 0.16),
    "M_Medical": (0.32, 0.46, 0.43),
    "M_Social": (0.48, 0.30, 0.16),
    "M_Steel": (0.15, 0.22, 0.24),
    "M_Technical": (0.12, 0.24, 0.34),
}


def import_bunker():
    task = unreal.AssetImportTask()
    task.filename = str(FBX)
    task.destination_path = ASSET_DIR
    task.destination_name = "SM_Bunker_Playtest_Merged"
    task.automated = True
    task.replace_existing = True
    task.save = True

    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = False
    options.import_materials = True
    options.import_textures = False
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    options.static_mesh_import_data.combine_meshes = True
    options.static_mesh_import_data.import_translation = unreal.Vector(0.0, 0.0, 0.0)
    options.static_mesh_import_data.import_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    options.static_mesh_import_data.import_uniform_scale = 1.0
    options.static_mesh_import_data.convert_scene = True
    options.static_mesh_import_data.force_front_x_axis = False
    options.static_mesh_import_data.generate_lightmap_u_vs = False
    options.static_mesh_import_data.auto_generate_collision = False
    task.options = options

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if not task.imported_object_paths:
        raise RuntimeError("FBX import produced no assets")
    mesh_paths = [path for path in task.imported_object_paths if path.rsplit("/", 1)[-1].startswith("SM_")]
    if not mesh_paths:
        raise RuntimeError(f"FBX import produced no StaticMesh path: {task.imported_object_paths}")
    asset = unreal.load_asset(mesh_paths[0])
    if not isinstance(asset, unreal.StaticMesh):
        raise RuntimeError(f"Imported object is not a StaticMesh: {mesh_paths[0]}")
    body_setup = asset.get_editor_property("body_setup")
    body_setup.set_editor_property(
        "collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
    )
    unreal.EditorAssetLibrary.save_loaded_asset(asset)
    return asset, [str(path) for path in task.imported_object_paths]


def add_point_light(location, color, intensity=4800.0, radius=900.0):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, location)
    component = actor.point_light_component
    component.set_editor_property("intensity", intensity)
    component.set_editor_property("attenuation_radius", radius)
    component.set_editor_property("light_color", color)
    component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    # B1 uses broad, shadowless navigation light so the greybox remains
    # readable before the final baked/virtual-shadow lighting pass.
    component.set_editor_property("cast_shadows", False)
    return actor


def configure_blockout_materials(mesh):
    """Keep B1 readable even when indirect lighting is unavailable in a build."""
    # Resolve materials from the imported mesh. During an FBX reimport UE 5.8
    # may temporarily hide their packages from the asset registry even though
    # the mesh already owns valid loaded references to them.
    loaded_materials = {
        slot.material_interface.get_name(): slot.material_interface
        for slot in mesh.get_editor_property("static_materials")
        if slot.material_interface
    }
    unreal.log(f"B1 mesh material slots: {sorted(loaded_materials)}")
    replacements = {}
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    unreal.EditorAssetLibrary.make_directory(MATERIAL_DIR)
    for name, rgb in MATERIAL_COLORS.items():
        blockout_name = f"M_B1_{name.removeprefix('M_')}"
        source = (
            loaded_materials.get(name)
            or loaded_materials.get(name.removeprefix("M_"))
            or loaded_materials.get(blockout_name)
        )
        if source is None:
            raise RuntimeError(f"Missing imported material: {name}")
        material = unreal.load_asset(f"{MATERIAL_DIR}/{blockout_name}.{blockout_name}")
        if material is None:
            material = asset_tools.create_asset(
                blockout_name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew()
            )
        unreal.MaterialEditingLibrary.delete_all_material_expressions(material)

        base = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -320, -40
        )
        base.set_editor_property("constant", unreal.LinearColor(*rgb, 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(
            base, "", unreal.MaterialProperty.MP_BASE_COLOR
        )

        emissive = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -320, 80
        )
        emissive.set_editor_property(
            "constant", unreal.LinearColor(rgb[0] * 0.80, rgb[1] * 0.80, rgb[2] * 0.80, 1.0)
        )
        unreal.MaterialEditingLibrary.connect_material_property(
            emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR
        )

        roughness = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant, -320, 190
        )
        roughness.set_editor_property("r", 0.82)
        unreal.MaterialEditingLibrary.connect_material_property(
            roughness, "", unreal.MaterialProperty.MP_ROUGHNESS
        )
        unreal.MaterialEditingLibrary.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        replacements[name] = material
        replacements[blockout_name] = material

    static_materials = list(mesh.get_editor_property("static_materials"))
    for slot in static_materials:
        slot_name = slot.material_interface.get_name() if slot.material_interface else ""
        replacement = replacements.get(slot_name)
        if replacement:
            slot.set_editor_property("material_interface", replacement)
    mesh.set_editor_property("static_materials", static_materials)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)


mesh, imported_paths = import_bunker()
configure_blockout_materials(mesh)
if unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
    unreal.EditorLevelLibrary.load_level(LEVEL)
    # Rebuild deterministically: previous setup runs must not accumulate old
    # PlayerStarts, bunker meshes or lights in the persistent level.
    for existing_actor in unreal.EditorLevelLibrary.get_all_level_actors():
        unreal.EditorLevelLibrary.destroy_actor(existing_actor)
else:
    unreal.EditorLevelLibrary.new_level(LEVEL)

bunker_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0)
)
bunker_actor.set_actor_label("Bunker_B1_Merged")
bunker_actor.static_mesh_component.set_static_mesh(mesh)
bunker_actor.static_mesh_component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)

# Start in the two-metre main circulation axis, clear of furniture and doors.
player_start = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.PlayerStart,
    unreal.Vector(1800.0, -1000.0, 110.0),
    unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
)
player_start.set_actor_label("PlayerStart_Bunker")

warm = unreal.Color(255, 176, 105, 255)
neutral = unreal.Color(210, 224, 255, 255)
cold = unreal.Color(125, 185, 255, 255)

for x, y, z in ((950, -260, 235), (1320, -520, 235), (1900, -250, 235), (2500, -300, 235)):
    add_point_light(unreal.Vector(float(x), float(y), float(z)), warm, 5200.0, 850.0)
for x, y, z in ((250, -650, 235), (750, -950, 235), (1350, -950, 235), (1950, -950, 235)):
    add_point_light(unreal.Vector(float(x), float(y), float(z)), neutral, 4200.0, 800.0)
for x, y, z in ((250, -1400, 235), (750, -1400, 235), (1350, -1400, 235), (1930, -1770, 235), (2500, -1450, 235)):
    add_point_light(unreal.Vector(float(x), float(y), float(z)), cold, 4600.0, 800.0)

# Guaranteed readable light at the first playable position.
add_point_light(unreal.Vector(1800.0, -1000.0, 225.0), neutral, 7000.0, 1100.0)

sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0.0, 0.0, 300.0))
sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
sky_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

world = unreal.EditorLevelLibrary.get_editor_world()
settings = world.get_world_settings()
settings.set_editor_property("kill_z", -2000.0)

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory("/Game/Bunker", only_if_is_dirty=False, recursive=True)

bounds = mesh.get_bounds()
result = {
    "engine": unreal.SystemLibrary.get_engine_version(),
    "level": LEVEL,
    "imported_paths": imported_paths,
    "mesh_extent_cm": [bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z],
    "mesh_origin_cm": [bounds.origin.x, bounds.origin.y, bounds.origin.z],
    "player_start_cm": [1800.0, -1000.0, 110.0],
    "lights": 15,
}
REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
unreal.log_warning("CONDOMINIO13_SETUP_OK " + json.dumps(result))
