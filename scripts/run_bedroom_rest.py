"""Two rendered players: replicated skeletal rest, recovery and interrupted exit."""
from pathlib import Path
import os,subprocess,time,json,re,shutil,argparse
parser=argparse.ArgumentParser();parser.add_argument("--headless-client",action="store_true");opt=parser.parse_args()
R=Path(__file__).resolve().parents[1];start=time.time();env=os.environ.copy();env.setdefault('DEVELOPER_DIR','/Applications/Xcode.app/Contents/Developer');env.setdefault('TOOLCHAINS','com.apple.dt.toolchain.Metal.32023.883')
exe=Path(env.get('C13_UNREAL_ROOT','/Users/Shared/Epic Games/UE_5.8'))/'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
procs=[];handles=[];logs={};driver_error=None
try:
 for role,url,res in [('host','/Game/Bunker/BedroomRest/Lvl_Bedroom_Study_Rest?listen',(960,540)),('client','127.0.0.1:7798',(800,450))]:
  if role=='client':
   deadline=time.time()+300
   while time.time()<deadline:
    ready=logs['host'].exists() and 'Load map complete /Game/Bunker/BedroomRest' in logs['host'].read_text(errors='replace')
    if ready:break
    if procs[0].poll() is not None:raise RuntimeError('Host exited before map ready')
    time.sleep(1)
   else:raise RuntimeError('Host never reached map ready')
  path=R/f'logs/restpose_{role}_native.log';logs[role]=path;path.unlink(missing_ok=True);out=(R/f'logs/restpose_{role}_driver.log').open('w');handles.append(out)
  args=[str(exe),str(R/'unreal/Condominio13/Condominio13.uproject'),url,'-port=7798','-game','-C13DoorVisual','-C13RoundTest','-C13BedroomRestTest','-windowed',f'-ResX={res[0]}',f'-ResY={res[1]}','-ForceRes','-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 70,r.ShadowQuality 0,r.AmbientOcclusionLevels 0','-abslog='+str(path),'-stdout','-FullStdOutLogOutput']
  if role=='client' and opt.headless_client:args+=['-nullrhi','-nosound']
  procs.append(subprocess.Popen(args,env=env,stdout=out,stderr=subprocess.STDOUT))
 for p in procs:p.wait(timeout=max(10,750-(time.time()-start)))
except (subprocess.TimeoutExpired,RuntimeError) as error:
 driver_error=str(error)
finally:
 for p in procs:
  if p.poll() is None:
   p.terminate()
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:p.kill();p.wait(timeout=10)
 for h in handles:h.close()
texts={k:p.read_text(errors='replace') if p.exists() else '' for k,p in logs.items()};checks={'driver_completed':driver_error is None,'clean_exit':len(procs)==2 and all(p.returncode==0 for p in procs),'client_joined':'Welcomed by server' in texts.get('client',''),'no_campaign_write':all('C13_SAVE_COMMIT' not in t for t in texts.values()),'occupied_rejected':'Esta cama está ocupada' in texts.get('client','')}
for role,t in texts.items():
 checks[role+'_actual_bones_lying']=all(f'C13_REST_BODY role={role} stage={s} pass=1' in t for s in (4,9))
 checks[role+'_restores_after_each_exit']=all(f'C13_REST_RESTORE role={role} stage={s} pass=1' in t for s in (6,11,14))
 checks[role+'_inventory_unchanged']=all('inventory=0' in l for l in t.splitlines() if 'C13_REST_STATE' in l)
 acting_stage=4 if role=='host' else 9
 match=re.search(rf'C13_REST_STATE role={role} stage={acting_stage} acting=1 resting=1 energy=([\d.]+)',t)
 checks[role+'_energy_increases']=bool(match and float(match[1])>35)
checks['mid_transition_enter']='C13_REST_MID leaving=0 pass=1' in texts.get('client','')
checks['mid_transition_leave']='C13_REST_MID leaving=1 pass=1' in texts.get('client','')
checks['no_orphan_pose_actors']='C13_REST_SERVER_RELEASE pass=0' not in texts.get('host','') and texts.get('host','').count('C13_REST_SERVER_RELEASE pass=1')==3
copied=[]
for folder in ('MacEditor','Mac'):
 for p in (R/'unreal/Condominio13/Saved/Screenshots'/folder).glob('restpose_*.png'):
  if p.stat().st_mtime>=start:shutil.copy2(p,R/'screenshots'/p.name);copied.append(p.name)
checks['remote_captures']='restpose_host_09.png' in copied and (opt.headless_client or 'restpose_client_04.png' in copied)
fps={role:[{'samples':int(n),'mean':float(f),'p95_ms':float(p)} for n,f,p in re.findall(r'C13_REST_FPS role=\w+ samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',t)] for role,t in texts.items()};checks['fps_recorded']=all(fps.values())
result={'driver_error':driver_error,'passed':all(checks.values()),'checks':checks,'fps':fps,'captures':copied,'profile':{'host_window':[960,540],'client_window':[800,450],'internal_percentage':70,'cap':30,'shadows':0,'ao':0},'headless_client':opt.headless_client,'scope':'Two simultaneous local Editor game instances (client optionally headless) with scripted inputs, real skeletal bones and screenshots; not a human, internet or packaged test.'}
(R/'logs/bedroom_rest_pose_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
