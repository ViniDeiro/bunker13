"""Create one world-space FBX mesh for the first Unreal playtest.

The editable modular source remains Bunker_Blockout_v001.blend.  This derived
mesh exists only to make the B1 layout reliable to import and package.
"""
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "blender" / "Bunker_Blockout_v001.blend"
OUTPUT = ROOT / "exports" / "Bunker_ReferenceShell.fbx"
REPORT = ROOT / "logs" / "reference_shell_export.json"
COLLECTIONS = (
    "ARCH_Walls",
    "ARCH_Floors",
    "ARCH_Ceilings",
    "ARCH_Doors",
    "ARCH_Stairs",
    "PROPS_Blockout",
)


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
depsgraph = bpy.context.evaluated_depsgraph_get()

vertices = []
faces = []
face_materials = []
material_names = []
material_lookup = {}
source_objects = []
door_layout = []

for collection_name in COLLECTIONS:
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        raise RuntimeError(f"Missing collection: {collection_name}")
    for obj in sorted(collection.objects, key=lambda item: item.name):
        if obj.type != "MESH" or obj.hide_render:
            continue
        if collection_name == 'ARCH_Doors' and obj.name.startswith('SM_Door_') and obj.get('state') == 'OPEN_B1':
            hinge=obj.parent
            name=obj.name.removeprefix('SM_Door_')
            vertical=name.endswith(('E','W'))
            door_layout.append({
                'name':name,
                'hinge_cm':[hinge.location.x*100,-hinge.location.y*100,hinge.location.z*100],
                'opening_width_cm':obj['opening_width_m']*100,
                'height_cm':obj['opening_height_m']*100,
                'closed_yaw':-90 if vertical else 0,
                'open_angle':-90 if name.endswith('S') else 90,
            })
            continue
        # These B1 masses have been replaced by constructed furniture in UE.
        # Keeping them creates solid blocks inside the new tables and sofa.
        replaced = ('SM_Mesa_Cartas', 'SM_Radio_Social', 'SM_Estante_Social', 'SM_Quadro_Avisos', 'SM_Mesa_Social', 'SM_Cadeira_', 'SM_Sofa', 'SM_TV_Antiga',
                    'SM_Cozinha_Bancada', 'SM_Pia', 'SM_Fogao', 'SM_Geladeira',
                    'SM_Mesa_Cozinha', 'SM_Maca', 'SM_Medicamentos',
                    'SM_Bancada_Medica', 'SM_Radio_Console', 'SM_Transmissor',
                    'SM_Arquivo_Expedicoes', 'SM_Bancada_Oficina', 'SM_Sucata',
                    'SM_Vaso', 'SM_EPI', 'SM_Cama_', 'SM_Armario_Pessoal_')
        if collection_name == 'PROPS_Blockout' and obj.name.startswith(replaced):
            continue
        source_objects.append(obj.name)
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        offset = len(vertices)
        vertices.extend(tuple(obj.matrix_world @ vertex.co) for vertex in mesh.vertices)
        slots = list(obj.data.materials)
        for polygon in mesh.polygons:
            faces.append(tuple(offset + index for index in polygon.vertices))
            material = slots[polygon.material_index] if slots and polygon.material_index < len(slots) else None
            name = material.name if material else "M_Blockout_Default"
            if name not in material_lookup:
                material_lookup[name] = len(material_names)
                material_names.append(name)
            face_materials.append(material_lookup[name])
        evaluated.to_mesh_clear()

merged_mesh = bpy.data.meshes.new("SM_Bunker_Playtest_Merged")
merged_mesh.from_pydata(vertices, [], faces)
merged_mesh.update()
merged = bpy.data.objects.new("SM_Bunker_Playtest_Merged", merged_mesh)
bpy.context.scene.collection.objects.link(merged)

for material_name in material_names:
    material = bpy.data.materials.get(material_name) or bpy.data.materials.new(material_name)
    merged_mesh.materials.append(material)
for polygon, material_index in zip(merged_mesh.polygons, face_materials):
    polygon.material_index = material_index

bpy.ops.object.select_all(action="DESELECT")
merged.select_set(True)
bpy.context.view_layer.objects.active = merged

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.fbx(
    filepath=str(OUTPUT),
    use_selection=True,
    object_types={"MESH"},
    apply_unit_scale=True,
    apply_scale_options="FBX_SCALE_UNITS",
    axis_forward="-Z",
    axis_up="Y",
    bake_space_transform=False,
    use_mesh_modifiers=True,
    mesh_smooth_type="FACE",
    add_leaf_bones=False,
    path_mode="AUTO",
)

report = {
    "source": str(SOURCE.relative_to(ROOT)),
    "output": str(OUTPUT.relative_to(ROOT)),
    "source_objects": len(source_objects),
    "vertices": len(vertices),
    "faces": len(faces),
    "materials": material_names,
    "dimensions_m": [round(value, 4) for value in merged.dimensions],
}
(ROOT/'logs/doors_layout.json').write_text(json.dumps(door_layout,indent=2))
report['movable_leaves_removed']=len(door_layout)
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("UNREAL_PLAYTEST_EXPORT", json.dumps(report))
