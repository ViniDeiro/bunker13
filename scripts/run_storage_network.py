"""Four real processes: concurrent withdrawal, deposit, stale/access/capacity rejection."""
from pathlib import Path
import subprocess,time,json
ROOT=Path(__file__).resolve().parents[1];exe=ROOT/'builds/Mac/Condominio13-VerticalSlice.app/Contents/MacOS/Condominio13'
processes=[];files=[]
try:
 for i in range(4):
  out=(ROOT/f'logs/storage_network_{i}.log').open('w');files.append(out)
  args=[str(exe),'/Game/Bunker/Lvl_Bunker?listen' if i==0 else '127.0.0.1:7789','-port=7789','-C13StorageTest','-game','-nullrhi','-RenderOffScreen','-nosound','-unattended','-NoSteam','-stdout','-FullStdOutLogOutput','-LogCmds=LogTemp Verbose']
  processes.append(subprocess.Popen(args,stdout=out,stderr=subprocess.STDOUT));time.sleep(2 if i==0 else .5)
 deadline=time.monotonic()+75
 while time.monotonic()<deadline:
  host=(ROOT/'logs/storage_network_0.log').read_text(errors='replace')
  if 'C13_STORAGE_AUDIT final' in host or all(p.poll() is not None for p in processes):break
  time.sleep(1)
finally:
 for p in processes:
  if p.poll() is None:p.terminate()
 for p in processes:
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 for out in files:out.close()
logs=[(ROOT/f'logs/storage_network_{i}.log').read_text(errors='replace') for i in range(4)]
checks={name:f'C13_STORAGE_AUDIT {name} PASS' in logs[0] for name in ('race','deposit','remote_reject','capacity','weight','final')}
checks['all_opened']=all('C13_STORAGE_SNAPSHOT count=1 revision=0' in log for log in logs)
checks['two_moves']=logs[0].count('C13_STORAGE_MOVE')==2
checks['stale_rejected']='C13_STORAGE_REJECT stale' in logs[0]
checks['unauthorized_rejected']='C13_STORAGE_REJECT access' in logs[0]
checks['slots_enforced']='slots=1 weight=0' in logs[0]
checks['weight_enforced']='slots=0 weight=1' in logs[0]
checks['private_views']=all('C13_STORAGE_PRIVATE value=1 closed=1' in log for log in logs)
checks['controls_released']=all('C13_STORAGE_CLIENT_DONE closed=1' in log for log in logs)
result={'passed':all(checks.values()),'processes':4,'packaged_game':True,'checks':checks,'markers':[[l for l in log.splitlines() if 'C13_STORAGE' in l] for log in logs],'limits':['Development-only preparation places players and supplies capacity fixtures; E/TAB/X/I use the actual input bindings.','No save/load, reconnection or human latency/endurance claim.']}
(ROOT/'logs/storage_network_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
