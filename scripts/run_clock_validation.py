"""Independent packaged processes: real collection closure, day rollover, offline resume."""
from pathlib import Path
import os,subprocess,time,re,json,shutil
R=Path(__file__).resolve().parents[1]
exe=os.environ.get('C13_TEST_EXE',str(R/'builds/Mac/Condominio13-MVP.app/Contents/MacOS/Condominio13'))
logs={};checks={};start=time.time()
for mode,args in [('seed',['-C13RoundReset','-C13ClockSave']),('load',['-C13ClockLoad'])]:
 p=R/f'logs/clock_{mode}.log'
 with p.open('w') as out:proc=subprocess.run([exe,'/Game/Bunker/Lvl_CollectionRound','-C13Round','-C13RoundTest','-C13ClockFast','-windowed','-ResX=960','-ResY=540','-stdout','-FullStdOutLogOutput',*args],stdout=out,stderr=subprocess.STDOUT,timeout=90)
 logs[mode]=p.read_text(errors='replace');checks[mode+'_exit']=proc.returncode==0
 if mode=='seed':time.sleep(3) # Offline duration must not be included on restoration.
seed=logs['seed'];load=logs['load'];saved=re.findall(r'C13_CLOCK_SAVED elapsed=([\d.]+) phase=3 day_seconds=8.0',seed);restored=re.search(r'C13_CLOCK_RESTORED elapsed=([\d.]+) day_seconds=8.0',load);final=re.search(r'C13_CLOCK_LOAD_CHECK elapsed=([\d.]+) day=(\d+) day_seconds=8.0 phase=3',load)
checks.update({'real_collection_and_closure':'C13_ROUND_STARTED duration=35' in seed and 'C13_ROUND_SHELTER' in seed,'day_advanced':bool(re.search(r'C13_CLOCK_SEED elapsed=[\d.]+ day=2',seed)),'same_saved_elapsed':bool(saved and restored and abs(float(saved[-1])-float(restored[1]))<.01),'resumed_and_ticking':bool(final and restored and 0<float(final[1])-float(restored[1])<5),'valid_checkpoint':'C13_SAVE_REJECT' not in seed+load})
snap=Path.home()/'Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/Screenshots/Mac/clock_resumed.png'
if snap.exists() and snap.stat().st_mtime>=start:shutil.copy2(snap,R/'screenshots/clock_resumed.png')
result={'passed':all(checks.values()),'checks':checks,'test_day_seconds':8,'normal_default_day_seconds':240,'limits':['Scripted local processes, not human playtest.','Collection closes normally; only day duration is accelerated.','No clock advance during offline time.']}
(R/'logs/clock_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
