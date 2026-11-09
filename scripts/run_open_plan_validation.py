"""Independent comparison map. Never opens a production campaign checkpoint."""
from pathlib import Path
import subprocess,json,shutil,time,argparse,re
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--network',action='store_true');opt=p.parse_args()
exe=R/'builds/Mac/Condominio13-OpenPlan.app/Contents/MacOS/Condominio13';start=time.time();processes=[];files=[];mode='network' if opt.network else 'solo'
try:
 for i in range(2 if opt.network else 1):
  role='client' if i else 'host';out=(R/f'logs/open_plan_{mode}_{role}.log').open('w');files.append(out)
  level='127.0.0.1:7793' if i else '/Game/Bunker/Lvl_Bunker_OpenPlan'+('?listen' if opt.network else '')
  args=[str(exe),level,'-windowed','-ResX=960' if opt.network else '-ResX=1280','-ResY=540' if opt.network else '-ResY=720','-ForceRes','-C13Reference','-C13OpenPlan','-ReferencePhase=openplan','-stdout','-FullStdOutLogOutput']
  if opt.network:args+=['-port=7793','-C13PhysicalTest']
  processes.append(subprocess.Popen(args,stdout=out,stderr=subprocess.STDOUT))
  if opt.network and not i:time.sleep(3)
 for proc in processes:proc.wait(timeout=100)
finally:
 for proc in processes:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=8)
 for f in files:f.close()
logs=[(R/f'logs/open_plan_{mode}_{role}.log').read_text(errors='replace') for role in (['host','client'] if opt.network else ['host'])]
if opt.network:
 text='\n'.join(logs);checks={'two_players':'players=2' in text,'unique_ownership':'ownership=1' in text,'take':'C13_PHYSICAL_MOVE take=1' in text,'put_same_id':'C13_PHYSICAL_MOVE take=0 slot=6 id=C1300022000000000000000000000001 revision=2' in text,'closed_rejected':'C13_PHYSICAL_CLOSED_REJECT pass=1' in text,'race_rejected':'C13_PHYSICAL_REJECT slot=6 revision=0' in text,'remote_gesture': 'C13_OBSERVED_ACTION' in logs[1],'final_empty':'contents=0 revision=4' in text}
 checks['no_stock_modal']=all('modal=0' in l for l in text.splitlines() if 'C13_PHYSICAL_STAGE' in l and 'step=13 ' not in l and 'step=16 ' not in l)
 checks['consume_water_and_food']='type=Water consume=1' in text and 'type=Food consume=1' in text
 checks['reference_routes_clear']='C13_REFERENCE_CIRCULATION clear=9 total=9' in text
 expected={(2,0),(1,1),(2,2),(1,3),(0,4)};checks['snapshots_match']=all(expected.issubset({tuple(map(int,m)) for m in re.findall(r'C13_PHYSICAL_SNAPSHOT count=(\d+) revision=(\d+)',log)}) for log in logs)
else:
 checks={'six_zones_reachable':'C13_OPEN_PLAN_AUDIT zones=6 total=6' in logs[0],'four_capsules_clear':'four_capsules=4' in logs[0],'fps_measured':'C13_REFERENCE_FPS phase=openplan' in logs[0]}
 src=Path.home()/'Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/Screenshots/Mac'
 shots=list(src.glob('reference_openplan_*.png'));checks['three_captures']=sum(f.stat().st_mtime>=start for f in shots)==3
 for f in shots:
  if f.stat().st_mtime>=start:shutil.copy2(f,R/'screenshots'/f.name)
result={'passed':all(checks.values()) and all(proc.returncode==0 for proc in processes),'checks':checks,'rendered_processes':len(processes),'map':'/Game/Bunker/Lvl_Bunker_OpenPlan','campaign_io_disabled':True,'markers':[[l for l in log.splitlines() if any(x in l for x in ('C13_OPEN_PLAN_','C13_REFERENCE_FPS','C13_PHYSICAL_','C13_TWO_PLAYER_FPS'))] for log in logs]}
(R/f'logs/open_plan_{mode}_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
