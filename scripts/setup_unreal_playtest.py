"""Import the merged B1 bunker and create the playable Unreal level."""
import json
import math
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

# B2 visual language: original Santa Aurora defense-civil identity, informed by
# the compact, monolithic Scandinavian bunker mood of The Rain without copying it.
def make_solid_material(name, rgb, emissive=0.0, roughness=0.75, metallic=0.0):
    path = f"{MATERIAL_DIR}/{name}.{name}"
    material = unreal.load_asset(path)
    if material is None:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew()
        )
    unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
    base = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, -360, -80
    )
    base.set_editor_property("constant", unreal.LinearColor(*rgb, 1.0))
    unreal.MaterialEditingLibrary.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    if emissive > 0:
        glow = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -360, 40
        )
        glow.set_editor_property("constant", unreal.LinearColor(*(v * emissive for v in rgb), 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(glow, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    rough = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant, -360, 150
    )
    rough.set_editor_property("r", roughness)
    unreal.MaterialEditingLibrary.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    metal = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant, -360, 230
    )
    metal.set_editor_property("r", metallic)
    unreal.MaterialEditingLibrary.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material


B2_MATS = {
    "concrete": make_solid_material("M_B2_Concrete", (0.12, 0.14, 0.14), roughness=0.96),
    "white": make_solid_material("M_B2_ModuleWhite", (0.52, 0.55, 0.52), roughness=0.72),
    "steel": make_solid_material("M_B2_DarkSteel", (0.035, 0.055, 0.06), roughness=0.55, metallic=0.65),
    "orange": make_solid_material("M_B2_SafetyOrange", (0.55, 0.12, 0.025), emissive=0.16, roughness=0.68),
    "amber": make_solid_material("M_B2_WarmLight", (1.0, 0.34, 0.07), emissive=2.2, roughness=0.45),
    "cyan": make_solid_material("M_B2_ColdLight", (0.05, 0.32, 0.50), emissive=1.8, roughness=0.45),
    "fabric": make_solid_material("M_B2_BedFabric", (0.20, 0.28, 0.25), roughness=0.98),
    "wood": make_solid_material("M_B2_Wood", (0.28, 0.14, 0.055), roughness=0.85),
    "asphalt": make_solid_material("M_EXT_Asphalt", (0.025, 0.032, 0.035), roughness=0.98),
    "store": make_solid_material("M_EXT_Mercado", (0.22, 0.28, 0.25), roughness=0.82),
    "forest": make_solid_material("M_EXT_Forest", (0.035, 0.11, 0.055), roughness=1.0),
    "warning": make_solid_material("M_EXT_Warning", (0.62, 0.035, 0.02), emissive=0.5, roughness=0.7),
}

cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
cylinder_mesh = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")


def spawn_shape(label, location, size_m, material_key, mesh=cube_mesh, rotation=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*location), rotation or unreal.Rotator()
    )
    actor.set_actor_label(label)
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_material(0, B2_MATS[material_key])
    actor.set_actor_scale3d(unreal.Vector(*size_m))
    actor.static_mesh_component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    return actor


def spawn_interactable(label, display, action, kind, location, size_m, material_key, rotation=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.BunkerInteractable, unreal.Vector(*location), rotation or unreal.Rotator()
    )
    actor.set_actor_label(label)
    actor.set_editor_property("display_name", display)
    actor.set_editor_property("action_text", action)
    actor.set_editor_property("interaction", kind)
    actor.mesh.set_material(0, B2_MATS[material_key])
    actor.set_actor_scale3d(unreal.Vector(*size_m))
    return actor


# Repeating white wall modules, dark reveals and inset lighting give the bunker
# a dense, manufactured silhouette while preserving the validated circulation.
for x in range(150, 2800, 200):
    spawn_shape(f"B2_CeilingSpine_{x}", (x, -1030, 272), (1.45, 0.12, 0.10), "steel")
    spawn_shape(f"B2_CorridorLight_{x}", (x, -1030, 264), (0.72, 0.035, 0.025), "cyan")
for x in (720, 960, 1200, 1440, 1680, 1920, 2160, 2400, 2640):
    spawn_shape(f"B2_WhiteModule_{x}", (x, -22, 145), (1.8, 0.07, 2.55), "white")
for x in (760, 1120, 1480):
    spawn_shape(f"B2_SocialAmber_{x}", (x, -700, 260), (2.2, 0.05, 0.04), "amber")
for x in (420, 860, 1300, 1740, 2180):
    spawn_shape(f"B2_SafetyBand_{x}", (x, -2010, 112), (1.6, 0.025, 0.12), "orange")

# Four functional sleeping places; slightly raised layers cover the original
# blockout beds and provide a stronger room identity.
bed_positions = [(100, -500), (300, -500), (100, -750), (300, -750)]
for index, (x, y) in enumerate(bed_positions, 1):
    spawn_interactable(
        f"INT_Bed_{index}", f"Cama {index}", "deitar",
        unreal.BunkerInteraction.BED, (x, y, 54), (1.04, 2.04, 0.18), "fabric"
    )
    spawn_shape(f"BedFrame_{index}", (x, y, 38), (1.10, 2.10, 0.12), "steel")
    spawn_shape(f"Pillow_{index}", (x, y - 72, 68), (0.72, 0.38, 0.13), "white")
    spawn_shape(f"ReadingLight_{index}", (x - 42, y - 88, 128), (0.08, 0.08, 0.18), "amber")

# Usable bunker systems and physical resources.
spawn_interactable("INT_Dartboard", "alvo de dardos", "arremessar", unreal.BunkerInteraction.DARTS,
                   (1515, -690, 145), (0.62, 0.12, 0.62), "orange")
spawn_interactable("INT_Radio", "rádio de emergência", "sintonizar", unreal.BunkerInteraction.RADIO,
                   (805, -520, 108), (0.55, 0.40, 0.32), "steel")
spawn_interactable("INT_Generator", "gerador principal", "alternar", unreal.BunkerInteraction.GENERATOR,
                   (1920, -1780, 82), (2.3, 1.3, 1.6), "orange")
spawn_interactable("INT_StatusPanel", "painel de status", "consultar", unreal.BunkerInteraction.PANEL,
                   (2780, -500, 145), (0.15, 0.8, 0.65), "cyan")

pickup_specs = [
    ("Water_01", "garrafa de água", (2440, -1600, 48), (0.22, 0.22, 0.48), "cyan"),
    ("Water_02", "garrafa de água", (2490, -1600, 48), (0.22, 0.22, 0.48), "cyan"),
    ("Can_01", "lata de alimento", (2570, -1600, 22), (0.24, 0.24, 0.24), "orange"),
    ("Medkit", "kit médico", (370, -1460, 34), (0.52, 0.35, 0.22), "white"),
    ("Battery", "pilhas", (860, -1400, 22), (0.34, 0.20, 0.18), "orange"),
    ("Tool", "ferramenta", (1480, -1400, 20), (0.48, 0.16, 0.14), "steel"),
]
for label, display, location, size, mat_key in pickup_specs:
    spawn_interactable(f"INT_{label}", display, "pegar", unreal.BunkerInteraction.PICKUP,
                       location, size, mat_key)

# First exterior slice above the bunker: Mercado Aurora, parking, street,
# sealed clinic and forest edge. Geometry is physical and bounded.
spawn_shape("EXT_SupermarketFloor", (2550, 900, 300), (40, 30, 0.25), "concrete")
for label, loc, size in [
    ("North", (2550, -560, 500), (40, .35, 4)),
    ("West", (580, 900, 500), (.35, 30, 4)),
    ("East", (4520, 900, 500), (.35, 30, 4)),
    ("SouthL", (1350, 2360, 500), (15.5, .35, 4)),
    ("SouthR", (3950, 2360, 500), (11.0, .35, 4)),
]:
    spawn_shape(f"EXT_MercadoWall_{label}", loc, size, "store")
spawn_shape("EXT_MercadoSign", (2550, 2385, 610), (8.0, .18, 1.2), "warning")
for aisle in range(5):
    y = 1650 - aisle * 430
    for x in (1450, 2250, 3050, 3850):
        spawn_shape(f"EXT_Shelf_{aisle}_{x}", (x, y, 405), (5.2, .75, 1.85), "white")
for index, x in enumerate((1250, 1850, 2450, 3050)):
    spawn_shape(f"EXT_Checkout_{index}", (x, 2100, 350), (3.8, .75, .75), "steel")

spawn_shape("EXT_Parking", (2550, 3900, 285), (46, 28, .18), "asphalt")
spawn_shape("EXT_Street", (2550, 5900, 280), (60, 12, .20), "asphalt")
spawn_shape("EXT_ClinicFloor", (6900, 4800, 300), (18, 16, .24), "concrete")
for label, loc, size in [
    ("N", (6900, 4020, 500), (18, .3, 4)), ("S", (6900, 5580, 500), (18, .3, 4)),
    ("W", (6020, 4800, 500), (.3, 16, 4)), ("E", (7780, 4800, 500), (.3, 16, 4)),
]: spawn_shape(f"EXT_ClinicWall_{label}", loc, size, "white")
spawn_shape("EXT_ClinicWarning", (6035, 4800, 480), (.12, 3.2, 1.0), "warning")

for index in range(28):
    angle = index * 2.399
    radius = 3600 + (index % 5) * 520
    x = 2550 + math.cos(angle) * radius
    y = 3600 + math.sin(angle) * radius
    trunk = spawn_shape(f"EXT_Tree_{index}", (x, y, 540), (.34, .34, 5.2), "forest", cylinder_mesh)
    spawn_shape(f"EXT_Canopy_{index}", (x, y, 850), (2.2, 2.2, 2.2), "forest")

# Shadowless exterior fixtures keep the Mac profile inexpensive while making
# the collection routes readable at night and preserving the threatening mood.
for x in (1100, 1900, 2700, 3500, 4300):
    add_point_light(unreal.Vector(float(x), 900.0, 650.0), neutral, 6500.0, 1650.0)
for x, y in ((1100, 3500), (2500, 3500), (3900, 3500), (1500, 5200), (3500, 5200)):
    add_point_light(unreal.Vector(float(x), float(y), 620.0), cold, 5200.0, 1800.0)
for x, y in ((6400, 4500), (7300, 5100)):
    add_point_light(unreal.Vector(float(x), float(y), 620.0), neutral, 6000.0, 1500.0)

interaction_manager = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.BunkerInteractionManager, unreal.Vector(0, 0, 0)
)
interaction_manager.set_actor_label("SYS_InteractionManager")

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
    "lights": 27,
    "functional_beds": 4,
    "pickup_items": len(pickup_specs),
    "minigames": ["darts"],
    "exterior": ["Mercado Aurora", "parking", "street", "sealed clinic", "forest edge"],
}
REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
unreal.log_warning("CONDOMINIO13_SETUP_OK " + json.dumps(result))
