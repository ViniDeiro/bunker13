"""Rendered collection session and independent save processes, always isolated from user campaigns."""
from pathlib import Path
import subprocess,json,time,re,shutil,argparse,os,shlex
R=Path(__file__).resolve().parents[1];exe=Path(os.environ.get('C13_TEST_EXE',str(R/'builds/Mac/Condominio13-MVP.app/Contents/MacOS/Condominio13')))
P=argparse.ArgumentParser();P.add_argument('mode',choices=['seed','load','walk','network','visual']);opt=P.parse_args();mode=opt.mode
started=time.time();processes=[];outputs=[];roles=[]
def launch(role,url,args):
 out=(R/f'logs/round_{mode}_{role}.log').open('w');outputs.append(out);roles.append(role)
 cmd=[str(exe),url,'-C13Round','-C13RoundTest','-C13ClockFast','-windowed','-ResX=960','-ResY=540','-ForceRes','-stdout','-FullStdOutLogOutput',*args,*shlex.split(os.environ.get('C13_TEST_EXTRA',''))]
 proc=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT);processes.append(proc);return proc
try:
 if mode=='network':
  launch('host','/Game/Bunker/Lvl_CollectionRound?listen',['-port=7794','-C13RoundReset']);time.sleep(3)
  launch('client','127.0.0.1:7794',['-C13RoundReset','-C13RoundProfile=1'])
  while time.time()-started<90:
   if "C13_ROUND_SHELTER" in (R/"logs/round_network_host.log").read_text(errors="replace"):break
   if any(p.poll() is not None for p in processes):break
   time.sleep(.5)
  # A stranger with no campaign ticket must be rejected after closure.
  launch('late','127.0.0.1:7794',['-C13RoundReset','-C13RoundProfile=2','-nullrhi','-nosound'])
  for proc in processes[:2]:proc.wait(timeout=90)
 else:
  args={'seed':['-C13RoundReset','-C13RoundSaveEarly'],'load':['-C13RoundLoadCheck'],'walk':['-C13RoundReset','-C13RoundWalkTest'],'visual':['-C13RoundReset','-C13RoundVisualOnly']}[mode]
  launch('solo','/Game/Bunker/Lvl_CollectionRound',args).wait(timeout=80)
finally:
 for proc in processes:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=8)
 for f in outputs:f.close()
logs={role:(R/f'logs/round_{mode}_{role}.log').read_text(errors='replace') for role in roles};text='\n'.join(logs.values());checks={}
if mode=='visual':checks={'started':'C13_ROUND_STARTED' in text,'camera_logged':'C13_ROUND_CAMERA' in text,'one_item_owned':'C13_ROUND_PICKUP_AUDIT count=1 unique=1' in text}
elif mode=='seed':checks={'started':'C13_ROUND_STARTED duration=35' in text,'one_item_owned':'C13_ROUND_PICKUP_AUDIT count=1 unique=1' in text,'checkpoint_written':'C13_SAVE_COMMIT' in text,'save_accepted':'C13_SAVE_REJECT' not in text}
elif mode=='load':
 m=re.search(r'C13_ROUND_LOAD_CHECK phase=(\d+) remaining=([\d.]+) inventory=(\d+)',text)
 checks={'phase_and_timer_resumed':bool(m and m[1]=='1' and 10<float(m[2])<30),'inventory_resumed':bool(m and m[3]=='1'),'restoration_valid':'C13_ROUND_RESTORED phase=1' in text}
 old=(R/'logs/round_seed_solo.log').read_text(errors='replace');before=re.search(r'C13_ROUND_PICKUP_AUDIT count=1 unique=1 id=([A-Fa-f0-9]{32})',old);after=re.search(r'C13_ROUND_LOAD_CHECK .* id=([A-Fa-f0-9]{32})',text);checks['same_item_guid']=bool(before and after and before[1]==after[1])
elif mode=='walk':checks={'floor_hole_exists':'C13_ROUND_FLOOR_HOLE pass=1' in text,'all_route_points':len(set(re.findall(r'C13_ROUND_WALK_STEP step=(\d+)',text)))==13,'walked_to_bunker':'C13_ROUND_WALK_PASS' in text,'no_timeout':'C13_ROUND_WALK_TIMEOUT' not in text}
else:
 checks={'host_started':'C13_ROUND_STARTED duration=35' in logs['host'],'remote_start_rejected':'C13_ROUND_START_REJECT' in logs['host'],'one_item_not_duplicated':'C13_ROUND_PICKUP_AUDIT count=1 unique=1' in logs['host'],'alerts_30_15_5':all(f'C13_ROUND_ALERT seconds={i}' in logs['client'] for i in (30,15,5)),'physically_closed':'C13_ROUND_SHELTER' in logs['host'],'outside_not_killed':bool(re.search(r'C13_ROUND_OUTSIDE_ALIVE phase=3 angle=-?0\.0 health=100\.0 outside=1',logs['host'])),'release_cancelled':'C13_ROUND_CRANK_CANCEL' in logs['host'],'manual_recovery_opened':'C13_ROUND_RECOVERY_OPEN' in logs['host'],'exhaustion_not_a_softlock':'C13_ROUND_RECOVERY_OPEN energy=0.0' in logs['host'],'returned_by_movement':'C13_ROUND_RETURN pass=1' in logs['host'],'late_stranger_rejected':'C13_RECONNECT_REJECT collection_closed' in logs['host'],'both_see_shelter':all('C13_ROUND_CLIENT_FINAL role='+role+' phase=3 open=1' in logs[role] for role in ('host','client')),'checkpoints_valid':'C13_SAVE_REJECT' not in logs['host']}
if mode=='network':
 clocks={}
 for role in ('host','client'):
  m=re.search(r'C13_CLOCK_FINAL role=\w+ elapsed=([\d.]+) day=(\d+) day_seconds=([\d.]+)',logs[role]);clocks[role]=tuple(map(float,m.groups())) if m else None
 checks['shared_day_clock']=bool(all(clocks.values()) and abs(clocks['host'][0]-clocks['client'][0])<.3 and clocks['host'][1]==clocks['client'][1] and clocks['host'][1]>=6 and clocks['host'][2]==8)
snap=Path.home()/'Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/Screenshots/Mac'
for f in snap.glob('round_*.png'):
 if f.stat().st_mtime>=started:shutil.copy2(f,R/'screenshots'/f.name)
result={'mode':mode,'passed':all(checks.values()) and all(p.returncode==0 for p in processes[:2 if mode=='network' else 1]),'checks':checks,'rendered_instances':2 if mode=='network' else 1,'markers':{role:[l for l in s.splitlines() if any(k in l for k in ('C13_ROUND_','C13_SAVE_','C13_RECONNECT_REJECT'))] for role,s in logs.items()},'limits':['Scripted local processes, not human playtest or Internet.','Test duration 35 seconds; normal duration 90 seconds.','Fixtures position players for competing pickup and closure; the separate walk test validates locomotion on the real stair route.']}
(R/f'logs/round_{mode}_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
