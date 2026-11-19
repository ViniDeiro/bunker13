"""Create the isolated art pass; never save changes back into the reference map."""
import unreal as u

root = '/Game/Bunker/BedroomVisual'
source = '/Game/Bunker/BedroomRest/Lvl_Bedroom_Study_Rest'
target = root + '/Lvl_Bedroom_Study_Rest_Visual'
assets = u.EditorAssetLibrary
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assets.make_directory(root)
if not assets.does_asset_exist(target):
    assert assets.duplicate_asset(source, target)
assert levels.load_level(target)
by_name = {a.get_actor_label(): a for a in actors.get_all_level_actors()}

# Keep existing practical positions; reduce their wash and let shadows separate the volumes.
for i, (intensity, kelvin, radius) in enumerate(((850, 3600, 430), (660, 4150, 400), (670, 4650, 440))):
    light = by_name[f'Bedroom_Practical_{i}'].get_component_by_class(u.RectLightComponent)
    for prop, value in dict(intensity=intensity, temperature=kelvin, attenuation_radius=radius,
                            use_temperature=True, cast_shadows=True).items():
        light.set_editor_property(prop, value)

# Indirect bounce proxies have no shadow pass and affect a limited area.
def bounce(label, location, intensity, kelvin, radius):
    a = by_name.get(label)
    if not a:
        a = actors.spawn_actor_from_class(u.PointLight, u.Vector(*location))
        a.set_actor_label(label)
    c = a.get_component_by_class(u.PointLightComponent)
    for prop, value in dict(mobility=u.ComponentMobility.MOVABLE, intensity_units=u.LightUnits.LUMENS,
                            intensity=intensity, use_temperature=True, temperature=kelvin,
                            attenuation_radius=radius, source_radius=28, cast_shadows=False).items():
        c.set_editor_property(prop, value)

bounce('Visual_BenchBounce', (92,-219,135), 465, 4350, 345)
bounce('Visual_EntryBounce', (255,-112,162), 390, 4800, 370)

# Material overrides belong to this level; shared meshes and earlier materials remain untouched.
edit = u.MaterialEditingLibrary
tool = u.AssetToolsHelpers.get_asset_tools()
def material(name, color, roughness, normal_name=None):
    path = root + '/' + name
    m = assets.load_asset(path) if assets.does_asset_exist(path) else tool.create_asset(name, root, u.Material, u.MaterialFactoryNew())
    edit.delete_all_material_expressions(m)
    diffuse = edit.create_material_expression(m, u.MaterialExpressionConstant3Vector)
    diffuse.set_editor_property('constant', u.LinearColor(*color, 1))
    edit.connect_material_property(diffuse, '', u.MaterialProperty.MP_BASE_COLOR)
    rough = edit.create_material_expression(m, u.MaterialExpressionConstant)
    rough.set_editor_property('r', roughness)
    edit.connect_material_property(rough, '', u.MaterialProperty.MP_ROUGHNESS)
    if normal_name:
        texture = u.load_asset('/Game/Bunker/BedroomStudy/Textures/T_Bedroom_Weave_Normal')
        assert texture
        sample = edit.create_material_expression(m, u.MaterialExpressionTextureSample)
        sample.set_editor_property('texture', texture)
        sample.set_editor_property('sampler_type', u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        uv = edit.create_material_expression(m, u.MaterialExpressionTextureCoordinate)
        uv.set_editor_property('coordinate_index', 1)
        edit.connect_material_expressions(uv, '', sample, 'UVs')
        edit.connect_material_property(sample, 'RGB', u.MaterialProperty.MP_NORMAL)
    if name == 'M_Board_Ink':
        m.set_editor_property('used_with_instanced_static_meshes', True)
    edit.recompile_material(m)
    assert assets.save_loaded_asset(m)
    return m

teal = material('M_Blanket_DeepTeal', (.027,.23,.24), .87, 'Teal')
bed = by_name['SM_Bedroom_Bed'].get_component_by_class(u.StaticMeshComponent)
idx = bed.get_material_index('M_Bedroom_Teal')
assert idx >= 0
bed.set_material(idx,teal)
second = by_name.get('SM_Bedroom_Bed_02')
if not second:
    second = actors.spawn_actor_from_class(u.load_class(None,'/Script/Condominio13.BunkerInteractable'),
                                         u.Vector(113,-59,0),u.Rotator(yaw=-90))
    second.set_actor_label('SM_Bedroom_Bed_02')
second.set_editor_property('interaction',u.BunkerInteraction.BED)
second.set_editor_property('display_name',u.Text('Cama 02 — entrada'))
second.set_editor_property('action_text',u.Text('descansar'))
secondary_mesh=second.get_editor_property('mesh')
secondary_mesh.set_static_mesh(bed.get_editor_property('static_mesh'))
secondary_mesh.set_material(idx,teal)

board_cls = u.load_class(None, '/Script/Condominio13.BedroomDrawingBoard')
assert board_cls, 'Compile first: drawing board actor missing'
board = by_name.get('Visual_TurnBoard')
if not board:
    board = actors.spawn_actor_from_class(board_cls, u.Vector(437,-148,154), u.Rotator(yaw=180))
    board.set_actor_label('Visual_TurnBoard')
board.set_actor_location(u.Vector(437,-148,154),False,False)
for field, name, color, roughness in (
    ('frame', 'M_Board_Frame', (.035,.065,.057), .67),
    ('surface', 'M_Board_Enamel', (.67,.69,.57), .71),
    ('pen', 'M_Board_Pen', (.055,.12,.25), .52),
    ('ink', 'M_Board_Ink', (.018,.048,.13), .82),
):
    board.get_editor_property(field).set_material(0,material(name,color,roughness))
assert levels.save_current_level()
u.log('C13_BEDROOM_VISUAL_PASS_OK')
