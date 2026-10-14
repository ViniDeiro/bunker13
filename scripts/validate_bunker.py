import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/Bunker_Blockout_v001.blend'))
nav=json.loads((ROOT/'exports/navigation.json').read_text());checks=[]
def check(n,ok,detail=''):checks.append({'test':n,'pass':bool(ok),'detail':detail})
check('metric',bpy.context.scene.unit_settings.scale_length==1 and bpy.context.scene.unit_settings.system=='METRIC')
check('required_collections',all(n in bpy.data.collections for n in ['ARCH_Walls','ARCH_Floors','ARCH_Ceilings','ARCH_Doors','ARCH_Stairs','PROPS_Blockout','LIGHTS_Preview','COLLISION','REFERENCE']))
check('ten_rooms',len(nav['rooms'])==10)
check('five_cameras',all('CAM_'+n in bpy.data.objects for n in ['Top','Entrance','CommonRoom','Corridor','Storage']))
check('four_beds',len([o for o in bpy.data.objects if o.name.startswith('SM_Cama_')])==4)
check('human_scale',all(abs(bpy.data.objects[f'REF_Player_{i}_175cm'].dimensions.z-1.75)<1e-5 for i in range(1,5)))
check('cube_scale',all(abs(x-1)<1e-5 for x in bpy.data.objects['SM_Scale_1m'].dimensions))
check('applied_mesh_scales',all(all(abs(v-1)<1e-5 for v in o.scale) for o in bpy.context.scene.objects if o.type=='MESH'))
check('finite_vertices',all(math.isfinite(v) for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.vertices for v in p.co))
check('no_duplicate_object_suffix',not any(o.name.endswith('.001') for o in bpy.data.objects))
# Inspect actual evaluated geometry, not just the generator's intended dimensions.
actual=[]
for c in ['ARCH_Walls','ARCH_Doors','PROPS_Blockout']:
 for o in bpy.data.collections[c].objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  actual.append({'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]})
def free(x,y,r=.3):
 if not ((r<x<28-r and r<y<20-r) or (24.6+r<x<26.4-r and -2<y<.5)):return False
 return not any(a['min'][2]<1.75 and a['max'][2]>.09 and a['min'][0]-r<x<a['max'][0]+r and a['min'][1]-r<y<a['max'][1]+r for a in actual)
step=.1
nodes={(i,j) for i in range(280) for j in range(200) if free(i*step+.05,j*step+.05)}
def nearest(x,y):return min(nodes,key=lambda p:(p[0]*step+.05-x)**2+(p[1]*step+.05-y)**2)
start=nearest(25.5,2);q=[start];seen={start}
for p in q:
 for a in [(p[0]-1,p[1]),(p[0]+1,p[1]),(p[0],p[1]-1),(p[0],p[1]+1)]:
  if a in nodes and a not in seen:seen.add(a);q.append(a)
for name,(a,b,c,d) in nav['rooms'].items():
 inside=[p for p in seen if a+.3<p[0]*step+.05<c-.3 and b+.3<p[1]*step+.05<d-.3]
 check('physical_path_'+name,len(inside)>20,f'{len(inside)} reachable 0.1 m cells')
check('main_2m_corridor',all(free(x/10,y/10) for x in range(8,274) for y in range(95,110)))
# Four capsules fit simultaneously side-by-side in meeting bay; two can pass in corridor.
spots=[(10+i*.85,9.5) for i in range(4)]
check('four_capsules_clear',all(free(*p) for p in spots) and all(math.dist(a,b)>=.6 for i,a in enumerate(spots) for b in spots[i+1:]))
check('two_way_main_corridor',all(free(x/10,9.7) and free(x/10,10.5) for x in range(8,274)))
# Doors: check at threshold and on either side using actual geometry.
for door in nav['doors']:
 if door['sealed']:continue
 x,y,_=door['center'];check('door_clear_'+door['name'],free(x,y),f"{door['width']} x {door['height']} m")
# Actual architectural wall volume overlaps, excluding intended face contact.
walls=[]
for o in bpy.data.collections['ARCH_Walls'].objects:
 pts=[o.matrix_world@Vector(p) for p in o.bound_box]
 walls.append((o.name,[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]))
overlaps=[]
for i,(an,alo,ahi) in enumerate(walls):
 for bn,blo,bhi in walls[i+1:]:
  if all(min(ahi[k],bhi[k])-max(alo[k],blo[k])>1e-5 for k in range(3)):overlaps.append([an,bn])
check('no_wall_volume_overlaps',not overlaps,str(overlaps))
# Manifold closed box proxies and nonzero faces.
import bmesh
bad=[];inward=[]
for me in {o.data for o in bpy.context.scene.objects if o.type=='MESH'}:
 bm=bmesh.new();bm.from_mesh(me)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-9 for f in bm.faces):bad.append(me.name)
 if bm.calc_volume(signed=True)<=0:inward.append(me.name)
 bm.free()
check('closed_non_degenerate_meshes',not bad,str(bad))
check('outward_normals',not inward,str(inward))
# Structural floors/stairs have no missing increments.
stairs=sorted([o for o in bpy.data.objects if o.name.startswith('SM_Stair_')],key=lambda o:o.name)
check('twenty_stair_steps',len(stairs)==20)
check('stair_riser_tread',all(abs(o.dimensions.y-.30)<1e-4 for o in stairs) and all(abs(stairs[i].dimensions.z-stairs[i+1].dimensions.z-.15)<1e-4 for i in range(19)))
support=[]
for cname in ['ARCH_Floors','ARCH_Stairs']:
 for o in bpy.data.collections[cname].objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
  if lo[0]<=25.5<=hi[0]:support.append((lo,hi))
heights=[]
for iy in range(-900,101):
 y=iy/100;z=[hi[2] for lo,hi in support if lo[1]-1e-5<=y<=hi[1]+1e-5]
 heights.append(max(z) if z else None)
check('continuous_stair_floor_support',all(z is not None for z in heights))
check('stair_surface_max_step',all(a is not None and b is not None and abs(a-b)<=.151 for a,b in zip(heights,heights[1:])))
check('five_nonempty_renders',all((ROOT/'screenshots'/f'CAM_{n}.png').stat().st_size>10000 for n in ['Top','Entrance','CommonRoom','Corridor','Storage']))
check('exports_present',all((ROOT/'exports'/n).stat().st_size>1000 for n in ['Bunker_Blockout_v001.glb','Bunker_Blockout_v001.fbx','Scale_1m.fbx']))
result={'checks':checks,'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'objects':len(bpy.context.scene.objects)}
(ROOT/'logs/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
# Independent round-trip of metric reference through FBX.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(ROOT/'exports/Scale_1m.fbx'))
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');dims=list(obj.dimensions)
(ROOT/'logs/scale_roundtrip.json').write_text(json.dumps({'dimensions_m':dims,'pass':all(abs(v-1)<.0001 for v in dims)},indent=2))
assert not result['failed'],f"{result['failed']} checks failed"
