"""Reopen the saved source and verify exports, dimensions and embedded textures."""
import bpy, bmesh, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/Bunker_Items_v001.blend'))
manifest=json.loads((ROOT/'logs/item_kit.json').read_text());checks=[]
for entry in manifest['assets']:
    o=bpy.data.objects.get(entry['name']);assert o and o.type=='MESH',entry['name']
    assert len(o.data.materials)==1 and o.data.uv_layers.active
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
    assert all(-.001<=c<=1.001 for loop in o.data.uv_layers.active.data for c in loop.uv)
    assert all(abs(a-b)<.0001 for a,b in zip(o.dimensions,entry['dimensions_m']))
    assert len(bpy.data.collections['ITEM_'+entry['name'].removeprefix('SM_Item_')].objects)==entry['parts']
    assert o.scale==__import__('mathutils').Vector((1,1,1))
    source=ROOT/'exports/items'/(o.name+'.fbx');assert source.stat().st_size>1000
    for part in bpy.data.collections['ITEM_'+entry['name'].removeprefix('SM_Item_')].objects:
        bm=bmesh.new();bm.from_mesh(part.data)
        if all(e.is_manifold for e in bm.edges):assert bm.calc_volume(signed=True)>0,part.name+' inverted shell'
        bm.free()
    checks.append({'asset':o.name,'reopened':True,'dimensions_verified':True,'uv_finite_in_0_1':True,'editable_parts':entry['parts'],'export_bytes':source.stat().st_size})
images=[im for im in bpy.data.images if im.name.startswith('T_Item_')];assert len(images)==15
assert all(im.packed_file and tuple(im.size)==(1024,1024) for im in images)
(ROOT/'logs/item_validation.json').write_text(json.dumps({'passed':True,'blend_reopened':True,'embedded_images':len(images),'assets':checks,'limit':'Visual manufacture shells overlap intentionally; label overlays are open surfaces, not watertight solids.'},indent=2))
print('C13_ITEM_SOURCE_VALIDATED')
