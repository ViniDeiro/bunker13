"""Two rendered Editor game processes. No campaign saves; fail on missing evidence."""
from pathlib import Path
import os,subprocess,time,json,re,shutil,argparse
parser=argparse.ArgumentParser();parser.add_argument('--video',action='store_true');opt=parser.parse_args()
R=Path(__file__).resolve().parents[1];start=time.time();env=os.environ.copy()
env.setdefault('DEVELOPER_DIR','/Applications/Xcode.app/Contents/Developer');env.setdefault('TOOLCHAINS','com.apple.dt.toolchain.Metal.32023.883')
exe=Path(env.get('C13_UNREAL_ROOT','/Users/Shared/Epic Games/UE_5.8'))/'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor';project=R/'unreal/Condominio13/Condominio13.uproject'
procs=[];handles=[];logs={}
try:
 for role,url,res in [('host','/Game/Bunker/BedroomCabinet/Lvl_Bedroom_Study_Cabinet?listen',(960,540)),('client','127.0.0.1:7797',(800,450))]:
  if role=='client':
   deadline=time.time()+300
   while time.time()<deadline:
    if logs['host'].exists() and 'Load map complete /Game/Bunker/BedroomCabinet' in logs['host'].read_text(errors='replace'):break
    if procs[0].poll() is not None:raise RuntimeError('Host exited before map ready')
    time.sleep(1)
   else:raise RuntimeError('Host never reached map ready')
  path=R/f'logs/bedcab_{role}_native.log';path.unlink(missing_ok=True);out=(R/f'logs/bedcab_{role}_driver.log').open('w');handles.append(out);logs[role]=path
  args=[str(exe),str(project),url,'-port=7797','-game','-C13DoorVisual','-C13RoundTest','-C13BedroomCabinetTest','-windowed',f'-ResX={res[0]}',f'-ResY={res[1]}','-ForceRes','-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 70,r.ShadowQuality 0,r.AmbientOcclusionLevels 0','-abslog='+str(path),'-stdout','-FullStdOutLogOutput']
  if opt.video:args.append('-C13BedroomCabinetVideo')
  procs.append(subprocess.Popen(args,env=env,stdout=out,stderr=subprocess.STDOUT))
 for p in procs:p.wait(timeout=max(10,600-(time.time()-start)))
finally:
 for p in procs:
  if p.poll() is None:p.terminate();p.wait(timeout=10)
 for h in handles:h.close()
texts={k:p.read_text(errors='replace') if p.exists() else '' for k,p in logs.items()};host=texts.get('host','');client=texts.get('client','')
copied=[];dest=R/'screenshots/bedroom_reach_continuity';dest.mkdir(parents=True,exist_ok=True)
for folder in ('MacEditor','Mac'):
 for p in (R/'unreal/Condominio13/Saved/Screenshots'/folder).glob('bedcab_*.png'):
  if p.stat().st_mtime>=start:
   if p.name.startswith('bedcab_video_'):
    frames=R/'output/bedcab_frames';frames.mkdir(parents=True,exist_ok=True);shutil.copy2(p,frames/p.name)
   else:shutil.copy2(p,dest/p.name);copied.append(p.name)
checks={'clean_exit':len(procs)==2 and all(p.returncode==0 for p in procs),'two_players':'players=2' in host,'no_campaign_write':all('C13_SAVE_COMMIT' not in t for t in texts.values()),'all_server_audits':all(f'C13_BEDCAB_AUDIT step={s} pass=1' in host for s in range(10,16)),'no_modal':all('modal=0' in line for t in texts.values() for line in t.splitlines() if 'C13_BEDCAB_VIEW' in line),'stale_rejected':'C13_PHYSICAL_REJECT slot=6 revision=0' in host,'take_and_put':host.count('C13_PHYSICAL_MOVE take=1')==2 and host.count('C13_PHYSICAL_MOVE take=0')==2,'same_water_id':len(re.findall(r'C13_PHYSICAL_MOVE .*id=C13000130000B0020000000000000001',host))==4,'both_captures':all(any(n.startswith('bedcab_'+role+'_') for n in copied) for role in texts)}
for role,t in texts.items():
 views=[tuple(map(int,m)) for m in re.findall(r'C13_BEDCAB_VIEW role=\w+ stage=(\d+) revision=(-?\d+) entries=(\d+) drawn=(\d+) modal=(\d+)',t)]
 checks[role+'_visible_snapshots']=all((stage,rev,count,count,0) in views for stage,rev,count in [(2,0,2),(5,1,1),(8,2,2),(23,4,2)])
 checks[role+'_door_replication']=bool(re.search(r'C13_BEDCAB_VIEW .*stage=2 .*door=110.00',t))
fps={role:[{'samples':int(m[0]),'mean':float(m[1]),'p95_ms':float(m[2])} for m in re.findall(r'C13_BEDCAB_FPS role=\w+ samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',t)] for role,t in texts.items()}
checks['fps_both']=all(fps.values())
checks['take_contact']=bool(re.search(r'C13_REACH_SAMPLE place=0 phase=1 .*contact_cm=0.000 visible=1',host))
checks['store_contact']=bool(re.search(r'C13_REACH_SAMPLE place=1 phase=3 .*contact_cm=0.000 visible=1',host))
checks['item_waits_on_shelf']=bool(re.search(r'C13_REACH_SAMPLE place=0 phase=0 .*visible=1 item_shelf_cm=0.000',host))
checks['far_transfer_rejected']='C13_REACH_FAR_TEST pass=1' in host and 'C13_REACH_REJECT distance_cm=' in host
checks['approach_capture']='bedcab_contact_approach.png' in copied
remote_samples=[tuple(map(float,m)) for m in re.findall(r'C13_REMOTE_SHELF t=([\d.]+) item_shelf_cm=([\d.]+) hands_contact_cm=([\d.]+) visible=(\d+)',client)]
checks['remote_item_waits_on_shelf']=any(0<=t<.25 and item<.01 and hand>5 and visible==1 for t,item,hand,visible in remote_samples)

checks['local_shelf_orientation']=any(float(a)<.1 and float(d)<.1 for a,d in re.findall(r'C13_LOCAL_SHELF angle_deg=([\d.]+) item_shelf_cm=([\d.]+)',host))
checks['remote_shelf_orientation']=any(float(t)<.25 and float(a)<.1 for t,a in re.findall(r'C13_REMOTE_SHELF t=([\d.]+) .*angle_deg=([\d.]+)',client))
checks['hand_retracts_after_store']=bool(re.search(r'C13_REACH_SAMPLE place=1 phase=4 .*visible=0',host))
result={'passed':all(checks.values()),'checks':checks,'fps':fps,'captures':copied,'profiles':{'host_window':[960,540],'client_window':[800,450],'internal_percentage':70,'shadows':0,'ao':0,'cap':30},'video_capture':opt.video,'scope':'Two simultaneous rendered Unreal Editor game processes with scripted E/X input and server audits, local loopback; no human or packaged/Steam test.'}
(R/'logs/bedroom_cabinet_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
