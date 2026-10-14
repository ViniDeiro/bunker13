"""Condominio 13 / Deiros Dev — B1. Run with Blender --background --python this_file.
All dimensions meters. Rebuilds the dedicated scene, never appends duplicates.
"""
import bpy, math, json, os, sys, heapq
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
RENDER='--no-render' not in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.name='Condominio13_B1'
s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
COLS=['ARCH_Walls','ARCH_Floors','ARCH_Ceilings','ARCH_Doors','ARCH_Stairs','PROPS_Blockout','LIGHTS_Preview','COLLISION','REFERENCE']
cs={n:bpy.data.collections.new(n) for n in COLS}
for c in cs.values(): s.collection.children.link(c)
def mat(n,col):
 m=bpy.data.materials.new('M_'+n); m.diffuse_color=(*col,1); m.use_nodes=True
 m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*col,1)
 m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78
 return m
mats={n:mat(n,c) for n,c in {'Concrete':(.30,.34,.33),'Floor':(.18,.22,.21),'Social':(.40,.30,.17),'Medical':(.28,.46,.44),'Technical':(.16,.25,.30),'Steel':(.10,.16,.16),'Door':(.46,.26,.09),'Reference':(.9,.55,.12),'Ink':(.018,.025,.028),'Text':(.82,.88,.80),'Furniture':(.30,.34,.25)}.items()}
obstacles=[]; doors=[]; furniture=[]
def move_col(o,c):
 for old in list(o.users_collection): old.objects.unlink(o)
 cs[c].objects.link(o)
def box(n,loc,dim,c='ARCH_Walls',ma='Concrete',solid=True,pivot='BASE'):
 origin=Vector(loc)-Vector((0,0,dim[2]/2))
 if pivot=='CORNER':origin=Vector(loc)-Vector(dim)/2
 delta=Vector(loc)-origin
 verts=[tuple(Vector((x*dim[0]/2,y*dim[1]/2,z*dim[2]/2))+delta) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 me=bpy.data.meshes.new('GEO_'+n);me.from_pydata(verts,[],[f[::-1] for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]]);me.update()
 uv=me.uv_layers.new(name='UVMap')
 for face in me.polygons:
  for i,li in enumerate(face.loop_indices):uv.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][i]
 o=bpy.data.objects.new('SM_'+n,me);cs[c].objects.link(o);o.location=origin;me.materials.append(mats[ma]);o['blockout']=True
 if solid and c not in ['ARCH_Floors','ARCH_Ceilings','ARCH_Stairs','REFERENCE']:
  obstacles.append({'name':o.name,'min':[loc[i]-dim[i]/2 for i in range(3)],'max':[loc[i]+dim[i]/2 for i in range(3)]})
 return o
# Clear internal bounds. Rooms are intentionally separated by shared circulation.
rooms={
 'Convivencia':(7,0.3,16,7.3), 'Cozinha':(17,.3,22,5.3),
 'Despensa':(22,12,28,17), 'Dormitorio':(.3,3.8,6.3,8.8),
 'Enfermaria':(.3,12,4.3,16), 'Radio_Comando':(5.5,12,9.5,16),
 'Oficina':(11,12,16,16), 'Gerador':(16.8,15.7,21.8,19.7),
 'Sanitario':(.3,.3,3.3,3.3), 'Antecamara':(23,0.3,28,6.3)}
# door wall, center along that wall, width
openings={'Convivencia':('N',11.5,1.8),'Cozinha':('N',19.5,1.1),'Despensa':('S',25,1.1),'Dormitorio':('N',4.8,1.1),'Enfermaria':('S',2.3,1.1),'Radio_Comando':('S',7.5,1.1),'Oficina':('N',13.5,1.1),'Gerador':('S',19.3,1.1),'Sanitario':('E',1.8,1.1),'Antecamara':('N',25.5,1.8)}
W=.20; H=3
# A regular floor/ceiling kit; transformed copies share mesh data after generation.
for ix in range(14):
 for iy in range(10):
  box(f'Floor_{ix:02}_{iy:02}',(1+2*ix,1+2*iy,-.125),(2,2,.25),'ARCH_Floors','Floor',False,'CORNER')
  box(f'Ceiling_{ix:02}_{iy:02}',(1+2*ix,1+2*iy,3.125),(2,2,.25),'ARCH_Ceilings','Concrete',False,'CORNER')
# Perimeter clear of room walls, adjusted footprint allowed by GDD.
# 28.6 x 20.6 exterior; south opening aligned to airlock and stair.
def segment(n,orient,fixed,a,b,z=1.5,h=3):
 if b-a<.001:return
 # modular 1 m pieces plus deterministic closure
 i=0
 while a < b-.001:
  e=min(a+1,b); dim=(e-a,W,h) if orient=='H' else (W,e-a,h)
  loc=((a+e)/2,fixed,z) if orient=='H' else (fixed,(a+e)/2,z)
  box(n+f'_{i:02}',loc,dim,pivot='CORNER'); a=e;i+=1
for name,orient,fixed,a,b in [('OuterW','V',-.3,-.4,20.2),('OuterE','V',28.3,-.4,20.2),('OuterN','H',20.2,-.2,28.2),('OuterS_L','H',-.3,-.2,24.6),('OuterS_R','H',-.3,26.4,28.2)]:segment(name,orient,fixed,a,b)
# Vestibule between outer shell and airlock; no gap in walking support.
box('EntryThreshold',(25.5,-.25,-.125),(1.8,.5,.25),'ARCH_Floors','Floor',False)

def door(n,orient,fixed,center,width,height=2.2,sealed=False):
 loc=(center,fixed,0) if orient=='H' else (fixed,center,0)
 # Door placed open in dedicated hinge empty; geometry is real but kept outside passage.
 hinge=bpy.data.objects.new('HINGE_'+n,None);cs['ARCH_Doors'].objects.link(hinge)
 hinge.location=(center-width/2,fixed,0) if orient=='H' else (fixed,center-width/2,0)
 leaf=box('Door_'+n,(0,0,height/2),(width,.08,height),'ARCH_Doors','Door',False)
 # local mesh origin lower-left hinge
 for v in leaf.data.vertices:v.co.x+=width/2
 leaf.parent=hinge;leaf.location=(0,0,0)
 hinge.rotation_euler.z=(0 if orient=='H' else math.pi/2)+(0 if sealed else (math.pi/2 if n.endswith('S') else -math.pi/2))
 leaf['opening_width_m']=width;leaf['opening_height_m']=height;leaf['state']='SEALED' if sealed else 'OPEN_B1'
 for off in [-width/2-.045,width/2+.045]:
  p=(center+off,fixed,height/2) if orient=='H' else (fixed,center+off,height/2)
  box('Frame_'+n+str(off),p,(.09,.24,height) if orient=='H' else (.24,.09,height),'ARCH_Doors','Steel',False)
 p=(center,fixed,height+.05) if orient=='H' else (fixed,center,height+.05)
 box('FrameTop_'+n,p,(width+.18,.24,.10) if orient=='H' else (.24,width+.18,.10),'ARCH_Doors','Steel',False)
 doors.append({'name':n,'center':list(loc),'width':width,'height':height,'sealed':sealed})
 return hinge
for n,(x0,y0,x1,y1) in rooms.items():
 side,center,width=openings[n]
 for sd,ori,fixed,a,b in [('S','H',y0-W/2,x0-W,x1+W),('N','H',y1+W/2,x0-W,x1+W),('W','V',x0-W/2,y0,y1),('E','V',x1+W/2,y0,y1)]:
  if n=='Gerador' and sd=='E':a=17.2
  if n=='Gerador' and sd=='S':b=21.8
  if sd==side or (n=='Antecamara' and sd=='S') or (n=='Convivencia' and sd=='W') or (n=='Oficina' and sd=='S'):
   cc=1.8 if n=='Convivencia' and sd=='W' else (25.5 if n=='Antecamara' and sd=='S' else center)
   ww=1.1 if n=='Convivencia' and sd=='W' else (1.8 if n=='Antecamara' else width); hh=2.4 if n=='Antecamara' else 2.2
   segment(n+sd+'L',ori,fixed,a,cc-ww/2);segment(n+sd+'R',ori,fixed,cc+ww/2,b)
   segment(n+sd+'Lintel',ori,fixed,cc-ww/2,cc+ww/2,(hh+H)/2,H-hh)
   door(n+sd,ori,fixed,cc,ww,hh)
  else:segment(n+sd,ori,fixed,a,b)
 # Functional color on inset floor only, no coincident faces.
 ma='Social' if n in ['Convivencia','Cozinha','Dormitorio'] else 'Medical' if n in ['Enfermaria','Sanitario'] else 'Technical'
 box('Zone_'+n,((x0+x1)/2,(y0+y1)/2,.008),(x1-x0,y1-y0,.016),'ARCH_Floors',ma,False)
# Solid service shafts close narrow incidental slots between rooms.
for n,x,w in [('MedicalRadio',4.9,.8),('RadioWorkshop',10.25,1.1)]:box('ServiceShaft_'+n,(x,14,1.5),(w,4.4,3))
# Entry stair drops 3 m from symbolic stock landing; 20 x .15 m rises, .30 tread.
for i in range(20):
 z=3-.15*i
 box(f'Stair_{i:02}',(25.5,-7.85+i*.30,z/2),(1.8,.30,z),'ARCH_Stairs','Concrete',False)
box('StockLanding',(25.5,-9,2.875),(3,2,.25),'ARCH_Stairs','Concrete',False)
box('StairBottom',(25.5,-1.25,-.125),(1.8,1.5,.25),'ARCH_Floors','Floor',False)
for x in [24.5,26.5]:
 box('StairSide'+str(x),(x,-4.35,1.5),(.2,7.9,3),'ARCH_Walls','Concrete')
 # rail follows stairs, handrail height ~1m above nosing.
 a=Vector((x,-8,4));b=Vector((x,-2,1)); mid=(a+b)/2
 rail=box('Handrail'+str(x),mid,(.06,.06,(b-a).length),'ARCH_Stairs','Steel',False)
 rail.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 for y,z in [(-8,3),(-6.5,2.25),(-5,1.5),(-3.5,.75),(-2,0)]:box('RailPost'+str(x)+str(y),(x,y,z+.5),(.06,.06,1),'ARCH_Stairs','Steel',False)
# Closed narrative fronts on north perimeter, backed by the actual shell.
for n,x in [('Ala_Medica_Lacrada',2.5),('Vigilancia_Lacrada',7),('Tunel_Emergencia',12)]:door(n,'H',20.08,x,1.1,2.2,True)
# Simple massing: all furniture remains B1 proxy geometry, no production detail.
def prop(n,x,y,dx,dy,dz,z=0,ma='Furniture'):
 o=box(n,(x,y,z+dz/2),(dx,dy,dz),'PROPS_Blockout',ma)
 furniture.append(o.name);return o
prop('Mesa_Social',11.4,3.7,2.6,1.2,.78)
for i,(x,y) in enumerate([(10.4,2.7),(11.4,2.7),(12.4,2.7),(10.4,4.7),(11.4,4.7),(12.4,4.7)]):prop('Cadeira_'+str(i),x,y,.45,.45,.46)
prop('Sofa',8,4.2,.85,2.6,.8);prop('TV_Antiga',8,.9,.8,.5,1.2)
prop('Mesa_Cartas',14.5,1.8,1.2,1.2,.75);prop('Radio_Social',8,5.2,.55,.4,.4,.8)
prop('Estante_Social',15.6,5,.5,2,1.9);prop('Quadro_Avisos',14.3,.38,1.8,.08,1.1,1)
prop('Cozinha_Bancada',17.45,2.6,.7,3,.9);prop('Pia',17.5,1.2,.75,.75,.15,.9)
prop('Fogao',18.9,.85,.8,.8,.9);prop('Geladeira',21.4,.85,.8,.8,1.9)
prop('Mesa_Cozinha',20.2,2.5,1.3,1,.75)
for i,x in enumerate([22.45,27.55]):prop('Despensa_Estante_'+str(i),x,14.8,.6,3.7,2)
prop('Despensa_Estante_Fundo',25,16.6,2.5,.6,2)
prop('Esconderijo_Visual',23.6,15.8,.8,.6,.7)
for i in range(3):prop('Galao_'+str(i),24+i*.55,16,.35,.35,.6)
for i,(x,y) in enumerate([(1,5),(3,5),(1,7.5),(3,7.5)]):
 prop('Cama_'+str(i+1),x,y,1,2,.5)
 prop('Armario_Pessoal_'+str(i+1),5.9,4.35+i*1.05,.6,.65,1.8)
prop('Maca',1.2,13.5,.8,2,.8);prop('Medicamentos',3.8,12.6,.6,1,1.8);prop('Bancada_Medica',3.8,14.7,.6,1.4,.9)
prop('Radio_Console',6,14,.7,2.6,.95);prop('Transmissor',6,14,.5,.7,.45,.95);prop('Arquivo_Expedicoes',9,13.8,.5,1,1.6)
prop('Bancada_Oficina',11.5,14,.7,3,.9);prop('Sucata',15.5,14,.6,1,.6)
prop('Gerador',19.2,17.8,2.3,1.3,1.6);prop('Combustivel',17.4,18.8,.65,.65,1)
prop('Painel_Eletrico',21.7,18,.15,1,1.2,1);prop('Filtro',20.8,19.2,1,.6,1.5)
prop('Tanque_Agua',17.5,16.6,.7,.7,1.4)
prop('Vaso',.9,1,.65,.8,.7);prop('Pia_Sanitaria',2.6,.65,.8,.5,.85);prop('Ducha',.9,2.5,.9,.9,.08)
prop('EPI',23.5,2,.7,1.6,1.9);prop('Inspecao',27.45,3.3,.7,1.7,.9)
prop('Ducha_Descontaminacao',27.3,1.1,1,1,.06);prop('Status',27.9,5,.12,.8,.5,1.2)
# Ventilation placeholders at ceiling height, finite and intentionally readable.
for x in [6.8,21.3]:box('Duto_'+str(x),(x,10.3,2.75),(.35,17,.3),'PROPS_Blockout','Steel')
# Four human-height capsule references off the main walking lane.
for i in range(4):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=(10+i*.85,9.5,.875))
 o=bpy.context.object;o.name='REF_Player_'+str(i+1)+'_175cm';o.scale=(.30,.30,.875);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);move_col(o,'REFERENCE');o.data.materials.append(mats['Reference']);o['height_m']=1.75;o['capsule_radius_m']=.30
box('Scale_1m',(18,9.5,.5),(1,1,1),'REFERENCE','Reference',False)
def label(n,txt,loc,size=.4,rot=(0,0,0)):
 cu=bpy.data.curves.new(n,'FONT');cu.body=txt;cu.size=size;cu.align_x='CENTER';cu.extrude=.001
 o=bpy.data.objects.new(n,cu);cs['REFERENCE'].objects.link(o);o.location=loc;o.rotation_euler=rot;cu.materials.append(mats['Ink'] if n.startswith('LABEL_') else mats['Text']);return o
for n,(a,b,c,d) in rooms.items():label('LABEL_'+n,n.upper().replace('_',' ')+'\n'+f'{c-a:g} x {d-b:g} m',((a+c)/2,(b+d)/2,.05),.42)
label('TITLE','CONDOMINIO 13  /  DEIROS DEV\nB1 - DEFESA CIVIL / SANTA AURORA',(14,22,.02),.7)
label('DIM_X','28 m (piso) / envelope externo 28,8 m',(14,-.95,.02),.45)
label('DIM_Y','20 m | pe-direito 3 m',(-1,10,.02),.4,(0,0,math.pi/2))
label('CORRIDOR','EIXO PRINCIPAL / 2 m LIVRES',(14,10.5,.03),.38)
label('STOCK','PATAMAR DO ESTOQUE\n+3,00 m',(25.5,-9,3.01),.25)
# Dimension lines kept in reference collection.
for y in [-.75]:
 box('Dimension_X',(14,y,.025),(28,.025,.025),'REFERENCE','Text',False)
 for x in [0,28]:box('DimensionTick'+str(x),(x,y,.025),(.025,.3,.025),'REFERENCE','Text',False)
# Preview light zones; no textures, visual detailing or final asset work.
def area(n,loc,power,col,size=4):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=col;d.shape='DISK';d.size=size
 o=bpy.data.objects.new(n,d);cs['LIGHTS_Preview'].objects.link(o);o.location=loc
for n,(a,b,c,d) in rooms.items():area('L_'+n,((a+c)/2,(b+d)/2,2.9),450,(1,.70,.40) if n in ['Convivencia','Dormitorio','Cozinha'] else (.56,.75,1),3)
for x in [3,9,15,22,26]:area('L_Circulation'+str(x),(x,10.5,2.9),350,(.70,.84,1),3)
for x in [3,8,13]:area('L_North'+str(x),(x,18,2.9),300,(.55,.72,1),3)
area('L_Stair',(25.5,-5,6),700,(.7,.8,1),5)
def camera(n,pos,target,lens=22,ortho=None):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.05;d.clip_end=200
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
cams=[camera('CAM_Top',(14,6,45),(14,6,0),ortho=48),camera('CAM_Entrance',(25.5,5.7,1.65),(25.5,-3,1.4)),camera('CAM_CommonRoom',(14.8,6.6,1.65),(9.5,2,1.1)),camera('CAM_Corridor',(25.5,10.5,1.65),(5,10.4,1.65)),camera('CAM_Storage',(25,12.5,1.65),(25,16,1.2))]
# A navigable route generated from actual solid bounds (capsule horizontal clearance).
R=.30;STEP=.20
def free(x,y):
 if not(.05<x<27.95 and .05<y<19.95):return False
 for a in obstacles:
  if a['min'][2]>=1.75 or a['max'][2]<=.08:continue
  if a['min'][0]-R<x<a['max'][0]+R and a['min'][1]-R<y<a['max'][1]+R:return False
 return True
nodes={(i,j) for i in range(140) for j in range(100) if free(i*STEP+.1,j*STEP+.1)}
def nearest(p):return min(nodes,key=lambda q:(q[0]*STEP+.1-p[0])**2+(q[1]*STEP+.1-p[1])**2)
start=nearest((25.5,2)); q=[start]; prev={start:None}
for p in q:
 for n in [(p[0]+1,p[1]),(p[0]-1,p[1]),(p[0],p[1]+1),(p[0],p[1]-1)]:
  if n in nodes and n not in prev:prev[n]=p;q.append(n)
results={};paths={}
for n,(a,b,c,d) in rooms.items():
 target=nearest(((a+c)/2,(b+d)/2));ok=target in prev
 results[n]={'clear_dimensions_m':[c-a,d-b,3],'reachable_capsule_r030':ok}
 if ok:
  path=[];p=target
  while p is not None:path.append([p[0]*STEP+.1,p[1]*STEP+.1,1.65]);p=prev[p]
  paths[n]=path[::-1]
assert all(r['reachable_capsule_r030'] for r in results.values()),results
walk=camera('CAM_Walkthrough',(25.5,-9,4.65),(25.5,-8,4.65));s.render.fps=30
route=[[25.5,-9,4.65],[25.5,-8,4.65],[25.5,-2,1.65],[25.5,2,1.65]]+paths['Convivencia'][1:]
# Keyframes at distance-based times, constant travel speed 1.4m/s.
frame=1;last=route[0]
for i,p in enumerate(route):
 frame+=max(1,round((Vector(p)-Vector(last)).length/1.4*30)) if i else 0
 walk.location=p
 target=route[min(i+1,len(route)-1)]
 if Vector(target)!=Vector(p):walk.rotation_euler=(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_euler()
 walk.keyframe_insert('location',frame=frame);walk.keyframe_insert('rotation_euler',frame=frame);last=p
s.frame_end=frame;s.frame_set(1)
# Share equivalent box geometry for modular editing/instancing.
cache={}
for o in list(bpy.data.objects):
 if o.type!='MESH' or not o.name.startswith('SM_'):continue
 key=(tuple(round(v,5) for v in o.dimensions),o.data.materials[0].name if o.data.materials else '',tuple(tuple(round(c,5) for c in v.co) for v in o.data.vertices))
 if key in cache:o.data=cache[key]
 else:cache[key]=o.data
# Store complete solid navigation metadata; the viewer uses world AABBs.
# Open leaves can protrude into rooms, so include evaluated door bounds after parenting.
bpy.context.view_layer.update()
for o in cs['ARCH_Doors'].objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  obstacles.append({'name':o.name,'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]})
nav={'rooms':rooms,'obstacles':obstacles,'doors':doors,'paths':paths,'radius':R,'height':1.75,'eye_height':1.65,'stair':{'x':[24.6,26.4],'y':[-8,-2],'rise':3,'tread':.3,'riser':.15},'spawn':[25.5,2,1.65]}
(ROOT/'exports/navigation.json').write_text(json.dumps(nav,indent=2))
# Collision meshes, convex box per static obstacle, matching UE UCX owner naming.
for a in obstacles:
 owner=bpy.data.objects.get(a['name'])
 if not owner or owner.type!='MESH':continue
 lo=a['min'];hi=a['max'];o=box('CollisionTemp',tuple((lo[i]+hi[i])/2 for i in range(3)),tuple(hi[i]-lo[i] for i in range(3)),'COLLISION','Concrete',False)
 o.name='UCX_'+owner.name+'_00';o.hide_render=True;o.hide_set(True)
cs['COLLISION'].hide_render=True
# Include floor, ceiling and step collision boxes in FBX, not in horizontal navigation.
for cname in ['ARCH_Floors','ARCH_Ceilings','ARCH_Stairs']:
 for owner in cs[cname].objects:
  if owner.type!='MESH':continue
  pts=[owner.matrix_world@Vector(p) for p in owner.bound_box]
  lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
  o=box('CollisionTemp',tuple((lo[i]+hi[i])/2 for i in range(3)),tuple(hi[i]-lo[i] for i in range(3)),'COLLISION','Concrete',False)
  o.name='UCX_'+owner.name+'_00';o.hide_render=True;o.hide_set(True)
# Remove stale unused geometry left by shared module reassignment.
for me in list(bpy.data.meshes):
 if me.users==0:bpy.data.meshes.remove(me)
for me in bpy.data.meshes:
 for poly in me.polygons:poly.material_index=0
# Complete reference cube sample for scale test.
ref=bpy.data.objects.get('SM_Scale_1m')
bpy.ops.object.select_all(action='DESELECT');ref.select_set(True);bpy.context.view_layer.objects.active=ref
bpy.ops.export_scene.fbx(filepath=str(ROOT/'exports/Scale_1m.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
# Export architecture and proxy props only; camera/lighting/reference excluded.
bpy.ops.object.select_all(action='DESELECT')
for c in ['ARCH_Walls','ARCH_Floors','ARCH_Ceilings','ARCH_Doors','ARCH_Stairs','PROPS_Blockout']:
 for o in cs[c].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/Bunker_Blockout_v001.glb'),export_format='GLB',use_selection=True)
# FBX with collision geometry, one convex UCX box per wall segment/prop.
for o in cs['COLLISION'].objects:o.hide_set(False);o.select_set(True)
# FBX exporter in this Blender build warns on linked mesh material slots.
# Temporary single-user copies preserve materials; master remains instanced.
original_data={o:o.data for o in bpy.context.selected_objects if o.type=='MESH'}
for o,me in original_data.items():o.data=me.copy()
bpy.ops.export_scene.fbx(filepath=str(ROOT/'exports/Bunker_Blockout_v001.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
for o,me in original_data.items():
 temp=o.data;o.data=me;bpy.data.meshes.remove(temp)

for o in cs['COLLISION'].objects:o.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('World_Preview');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.23,.28,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
s.view_settings.view_transform='AgX'
s.camera=cams[2]
for o in cs['REFERENCE'].objects:
 if o.type=='FONT':o.hide_render=True;o.location.z=3.5
# Visible, editable text navigation helper, no automatic script execution on file open.
for filename in ['walk_bunker.py']:
 p=ROOT/'scripts'/filename
 if p.exists():bpy.data.texts.load(str(p))
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   ar.spaces.active.overlay.grid_scale=.5;ar.spaces.active.clip_end=200;ar.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Bunker_Blockout_v001.blend'))
if RENDER:
 for cam in cams:
  s.camera=cam
  top=cam.name=='CAM_Top';cs['ARCH_Ceilings'].hide_render=top
  for o in cs['REFERENCE'].objects:
   if o.type=='FONT':o.hide_render=not top;o.location.z=3.5 if top else .05
  if top:area('L_Top',(14,8,24),15000,(1,1,1),24)
  s.render.filepath=str(ROOT/'screenshots'/f'{cam.name}.png');bpy.ops.render.render(write_still=True)
  if top:
   o=bpy.data.objects.get('L_Top');bpy.data.objects.remove(o,do_unlink=True)
 cs['ARCH_Ceilings'].hide_render=False;s.camera=cams[2]
 for o in cs['REFERENCE'].objects:
  if o.type=='FONT':o.hide_render=True;o.location.z=3.5
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Bunker_Blockout_v001.blend'))
report={'blender':bpy.app.version_string,'objects':len(s.objects),'mesh_data_blocks':len(bpy.data.meshes),'rooms':results,'doors':doors,'main_corridor_clear_width_m':2,'route_entry_common_m':round((len(paths['Convivencia'])-1)*STEP,2),'walking_speed_assumed_m_s':1.4,'walk_frames':frame,'collection_counts':{n:len(c.objects) for n,c in cs.items()},'furniture':furniture}
(ROOT/'logs/generation.json').write_text(json.dumps(report,indent=2))
print('B1_GENERATION_OK',json.dumps(report))
