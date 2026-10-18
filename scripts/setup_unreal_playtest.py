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
        # A trace emission keeps unlit corners readable on the low-end profile
        # without making whole walls glow and flattening the room design.
        emissive.set_editor_property(
            "constant", unreal.LinearColor(rgb[0] * 0.06, rgb[1] * 0.06, rgb[2] * 0.06, 1.0)
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
    "red": make_solid_material("M_B2_EmergencyRed", (0.42, 0.018, 0.012), emissive=0.12, roughness=0.62),
    "green": make_solid_material("M_B2_UtilityGreen", (0.085, 0.19, 0.13), roughness=0.78),
    "rubber": make_solid_material("M_B2_Rubber", (0.012, 0.016, 0.017), roughness=0.98),
    "screen": make_solid_material("M_B2_Screen", (0.015, 0.22, 0.27), emissive=2.8, roughness=0.32),
    "porcelain": make_solid_material("M_B2_Porcelain", (0.68, 0.71, 0.68), roughness=0.42),
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


def furniture_box(label, location, size_m, material_key="steel", rotation=None):
    """Small static detail with collision disabled to keep dense rooms navigable."""
    actor = spawn_shape(label, location, size_m, material_key, rotation=rotation)
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return actor


def prop_cylinder(label, location, scale, material_key, rotation=None, collision=False):
    actor = spawn_shape(label, location, scale, material_key, cylinder_mesh, rotation)
    if not collision:
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return actor


def add_table(label, x, y, z=73, width=150, depth=85, material="wood"):
    furniture_box(label + "_Top", (x, y, z), (width / 100, depth / 100, .09), material)
    for ix in (-width * .42, width * .42):
        for iy in (-depth * .38, depth * .38):
            furniture_box(label + f"_Leg_{ix}_{iy}", (x + ix, y + iy, z / 2), (.07, .07, z / 100), "steel")


def add_chair(label, x, y, yaw=0):
    furniture_box(label + "_Seat", (x, y, 48), (.48, .48, .10), "wood", unreal.Rotator(yaw=yaw))
    furniture_box(label + "_Back", (x, y + 20, 78), (.48, .08, .62), "green", unreal.Rotator(yaw=yaw))
    for ix in (-18, 18):
        for iy in (-17, 17):
            furniture_box(label + f"_Leg_{ix}_{iy}", (x + ix, y + iy, 23), (.055, .055, .46), "steel")


def add_wall_panel(label, x, y, z, width, height, material="steel", horizontal=True):
    size = (width / 100, .055, height / 100) if horizontal else (.055, width / 100, height / 100)
    return furniture_box(label, (x, y, z), size, material)


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

# Architectural finish pass. The old shell remains structural; these pieces
# create a readable civil-defense facility rather than a room-shaped blockout.
for x in range(100, 2800, 200):
    furniture_box(f"B2_MainFloorStrip_{x}", (x, -1030, 2), (1.55, .16, .025), "orange")
for x in range(100, 2800, 400):
    furniture_box(f"B2_CorridorRibL_{x}", (x, -925, 145), (.10, .10, 2.75), "steel")
    furniture_box(f"B2_CorridorRibR_{x}", (x, -1135, 145), (.10, .10, 2.75), "steel")
    furniture_box(f"B2_CorridorRibTop_{x}", (x, -1030, 274), (.10, 2.15, .10), "steel")

# Rectangular ventilation trunks and color-coded services run continuously
# through the main axis, with visible drops into technical rooms.
for x in range(180, 2700, 360):
    furniture_box(f"B2_Duct_{x}", (x, -1165, 248), (3.1, .34, .32), "steel")
    furniture_box(f"B2_DuctJoint_{x}", (x, -1165, 248), (.08, .42, .39), "white")
for x in range(250, 2650, 300):
    furniture_box(f"B2_WaterPipe_{x}", (x, -865, 238), (2.6, .065, .065), "cyan")
    furniture_box(f"B2_PowerPipe_{x}", (x, -842, 220), (2.6, .055, .055), "orange")

# DORMITORY — lockers, bunks, privacy shelves, footwear and personal lights.
for index, y in enumerate((-435, -540, -645, -750), 1):
    furniture_box(f"Dorm_Locker_{index}", (585, y, 92), (.52, .74, 1.84), "green")
    furniture_box(f"Dorm_LockerDoor_{index}", (556, y, 102), (.035, .62, 1.48), "steel")
    furniture_box(f"Dorm_LockerHandle_{index}", (552, y - 20, 104), (.025, .07, .22), "orange")
for index, (x, y) in enumerate(((100, -500), (300, -500), (100, -750), (300, -750)), 1):
    furniture_box(f"Dorm_BedHead_{index}", (x, y - 101, 75), (1.1, .07, 1.35), "steel")
    furniture_box(f"Dorm_Blanket_{index}", (x, y + 35, 66), (.98, 1.25, .07), "green")
    furniture_box(f"Dorm_Shoe_{index}A", (x - 18, y + 115, 12), (.16, .34, .12), "rubber")
    furniture_box(f"Dorm_Shoe_{index}B", (x + 18, y + 115, 12), (.16, .34, .12), "rubber")
add_wall_panel("Dorm_NumberStrip", 300, -380, 220, 480, 26, "orange")

# SOCIAL ROOM — a communal table, mismatched chairs, sofa, old display and
# notice wall make the bunker feel occupied by four survivors.
add_table("Social_MainTable", 1140, -370, width=260, depth=120)
for i, (x, y, yaw) in enumerate(((1035, -275, 180), (1140, -275, 180), (1245, -275, 180),
                                 (1035, -465, 0), (1140, -465, 0), (1245, -465, 0)), 1):
    add_chair(f"Social_Chair_{i}", x, y, yaw)
furniture_box("Social_SofaBase", (805, -420, 38), (.85, 2.55, .55), "green")
furniture_box("Social_SofaBack", (770, -420, 88), (.18, 2.55, 1.05), "green")
for y in (-500, -420, -340):
    furniture_box(f"Social_SofaCushion_{y}", (825, y, 68), (.72, .70, .16), "fabric")
furniture_box("Social_TVCase", (805, -92, 105), (.92, .38, 1.35), "steel")
furniture_box("Social_TVScreen", (805, -70, 112), (.70, .035, .82), "screen")
furniture_box("Social_Rug", (1140, -370, 7), (3.9, 2.7, .035), "rubber")
add_wall_panel("Social_NoticeBoard", 1430, -35, 160, 180, 110, "wood")
for i, (x, z, mat) in enumerate(((1385, 175, "white"), (1440, 145, "orange"), (1480, 190, "white"))):
    furniture_box(f"Social_Notice_{i}", (x, -28, z), (.38, .018, .50), mat)

# KITCHEN — cabinet run, sink, stove controls, upper storage and refrigerator.
for i, y in enumerate((-90, -165, -240, -315, -390)):
    furniture_box(f"Kitchen_LowerCab_{i}", (1745, y, 46), (.68, .70, .88), "green")
    furniture_box(f"Kitchen_CabHandle_{i}", (1710, y, 55), (.025, .24, .035), "orange")
furniture_box("Kitchen_Counter", (1755, -245, 94), (.82, 3.85, .10), "steel")
furniture_box("Kitchen_Sink", (1740, -125, 99), (.58, .68, .035), "rubber")
for i, y in enumerate((-245, -305, -365, -425)):
    prop_cylinder(f"Kitchen_Burner_{i}", (1740, y, 100), (.24, .24, .025), "rubber")
for i, y in enumerate((-135, -260, -385)):
    furniture_box(f"Kitchen_UpperCab_{i}", (1740, y, 205), (.58, 1.05, .70), "white")
furniture_box("Kitchen_Fridge", (2135, -110, 98), (.85, .82, 1.96), "white")
furniture_box("Kitchen_FridgeSeal", (2090, -110, 105), (.025, .72, 1.72), "rubber")
furniture_box("Kitchen_FridgeHandle", (2085, -135, 118), (.025, .055, .52), "orange")
add_table("Kitchen_Breakfast", 2010, -300, width=130, depth=90, material="steel")

# INFIRMARY — examination bed, bedside trolley, locked medicine cabinet,
# illuminated monitor and privacy screen supports.
furniture_box("Medical_BedFrame", (120, -1350, 52), (.88, 2.10, .14), "steel")
furniture_box("Medical_Mattress", (120, -1350, 68), (.80, 2.00, .16), "porcelain")
furniture_box("Medical_Headrest", (120, -1435, 83), (.72, .45, .18), "white", unreal.Rotator(pitch=-18))
furniture_box("Medical_Trolley", (265, -1335, 74), (.55, .72, .08), "steel")
for x in (245, 285):
    for y in (-1360, -1310):
        prop_cylinder(f"Medical_TrolleyWheel_{x}_{y}", (x, y, 15), (.11, .11, .07), "rubber", unreal.Rotator(pitch=90))
furniture_box("Medical_Cabinet", (380, -1280, 100), (.58, 1.20, 1.90), "white")
furniture_box("Medical_CabinetCrossV", (348, -1280, 118), (.03, .12, .62), "red")
furniture_box("Medical_CabinetCrossH", (348, -1280, 118), (.03, .50, .15), "red")
furniture_box("Medical_Monitor", (300, -1455, 145), (.12, .72, .58), "steel")
furniture_box("Medical_MonitorScreen", (292, -1455, 148), (.018, .55, .38), "screen")

# RADIO/COMMAND — angled console impression, screen bank, map table and files.
furniture_box("Radio_ConsoleBase", (600, -1400, 63), (.72, 2.65, 1.15), "steel")
for i, y in enumerate((-1490, -1400, -1310)):
    furniture_box(f"Radio_Screen_{i}", (558, y, 135), (.035, .68, .54), "screen")
    for j in range(3):
        prop_cylinder(f"Radio_Dial_{i}_{j}", (552, y - 22 + j * 22, 92), (.07, .07, .035), "orange", unreal.Rotator(pitch=90))
add_table("Radio_MapTable", 790, -1460, width=130, depth=85, material="green")
furniture_box("Radio_Map", (790, -1460, 79), (1.12, .68, .018), "white")
for i, y in enumerate((-1310, -1380, -1450)):
    furniture_box(f"Radio_FileDrawer_{i}", (900, y, 90), (.48, .62, .55), "green")
    furniture_box(f"Radio_FileHandle_{i}", (873, y, 95), (.025, .20, .05), "orange")

# WORKSHOP — substantial workbench, pegboard, vise, tool silhouettes and crates.
furniture_box("Workshop_Bench", (1150, -1400, 88), (.78, 3.00, .16), "wood")
for y in (-1500, -1300):
    furniture_box(f"Workshop_BenchLeg_{y}", (1150, y, 43), (.14, .14, .86), "steel")
add_wall_panel("Workshop_Pegboard", 1115, -1400, 180, 250, 110, "green", horizontal=False)
for i, (y, z, length) in enumerate(((-1480, 190, 55), (-1410, 165, 75), (-1340, 205, 45))):
    furniture_box(f"Workshop_Tool_{i}", (1108, y, z), (.035, length / 100, .07), "orange")
furniture_box("Workshop_ViseBase", (1140, -1370, 104), (.34, .40, .22), "steel")
furniture_box("Workshop_ViseJaw", (1140, -1370, 119), (.42, .12, .16), "orange")
for i, (x, y) in enumerate(((1460, -1320), (1510, -1410), (1450, -1510))):
    furniture_box(f"Workshop_Crate_{i}", (x, y, 32), (.72, .72, .62), "green")
    furniture_box(f"Workshop_CrateBand_{i}", (x, y, 36), (.76, .10, .66), "steel")

# GENERATOR — machine casing, exhaust, coolant pipes, tanks and warning floor.
for x in (1810, 1920, 2030):
    furniture_box(f"Generator_Casing_{x}", (x, -1780, 96), (1.02, 1.32, 1.72), "green")
    furniture_box(f"Generator_Vent_{x}", (x, -1848, 105), (.72, .035, .78), "rubber")
for y in (-1740, -1820):
    prop_cylinder(f"Generator_Exhaust_{y}", (2065, y, 205), (.16, .16, 2.1), "steel")
for i, x in enumerate((1740, 1795, 1850)):
    prop_cylinder(f"Generator_FuelDrum_{i}", (x, -1910, 55), (.52, .52, 1.10), "red")
    furniture_box(f"Generator_DrumBand_{i}", (x, -1910, 55), (.56, .56, .06), "steel")
furniture_box("Generator_HazardFloor", (1930, -1780, 5), (4.8, 2.7, .028), "orange")

# SANITARY AND AIRLOCK — recognisable fixtures, changing bench and decon arch.
furniture_box("Sanitary_Partition", (165, -145, 108), (.10, 2.25, 2.16), "steel")
furniture_box("Sanitary_ToiletTank", (90, -105, 72), (.62, .30, .78), "porcelain")
furniture_box("Sanitary_ToiletSeat", (90, -135, 43), (.58, .72, .12), "porcelain")
furniture_box("Sanitary_Sink", (260, -75, 88), (.72, .48, .16), "porcelain")
furniture_box("Sanitary_Mirror", (260, -38, 162), (.75, .025, .92), "screen")
furniture_box("Airlock_Bench", (2470, -250, 48), (2.3, .55, .12), "wood")
for x in (2370, 2470, 2570):
    furniture_box(f"Airlock_BenchLeg_{x}", (x, -250, 23), (.08, .42, .46), "steel")
for i, y in enumerate((-110, -205, -300, -395)):
    furniture_box(f"Airlock_EPILocker_{i}", (2340, y, 98), (.62, .78, 1.92), "green")
furniture_box("Airlock_DeconLeft", (2700, -110, 125), (.16, .16, 2.50), "steel")
furniture_box("Airlock_DeconRight", (2800, -110, 125), (.16, .16, 2.50), "steel")
furniture_box("Airlock_DeconTop", (2750, -110, 245), (1.15, .16, .16), "steel")
for x in (2725, 2750, 2775):
    prop_cylinder(f"Airlock_Nozzle_{x}", (x, -110, 224), (.08, .08, .18), "orange")

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

# Regenerating the map must preserve the authored surface pass.
if (ROOT / 'assets/textures/T_Concrete_BaseColor.png').exists():
    import runpy
    runpy.run_path(str(ROOT / 'scripts/apply_surface_materials.py'))
if (ROOT / 'exports/hero_kit/SM_Hero_Bed.fbx').exists():
    import runpy
    runpy.run_path(str(ROOT / 'scripts/install_hero_kit.py'))
