"""Separate packaged processes, isolated slots; never touches a user's solo campaign."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'builds/Mac/Condominio13-VerticalSlice.app/Contents/MacOS/Condominio13'
steps=['seed','load','roundtrip','shutdown','shutdownload','seed','corrupt','backup','version','backup','layout','backup','duplicate','backup','position','safe_spawn','blocked']
results=[]
for index,phase in enumerate(steps):
 path=ROOT/f'logs/persistence_{index:02}_{phase}.log'
 with path.open('w') as out:
  try:
   p=subprocess.run([str(EXE),'-C13SaveProbe',*(['-C13SaveExit'] if phase=='shutdown' else []),f'-C13SavePhase={phase}','-game','-nullrhi','-RenderOffScreen','-nosound','-unattended','-NoSteam','-stdout','-FullStdOutLogOutput'],stdout=out,stderr=subprocess.STDOUT,timeout=35)
   code=p.returncode
  except subprocess.TimeoutExpired:code='timeout'
 log=path.read_text(errors='replace')
 passed=code==0 and f'C13_SAVE_PROBE PASS phase={phase}' in log
 result={'phase':phase,'passed':passed,'exit_code':code,'markers':[l for l in log.splitlines() if 'C13_SAVE' in l]}
 results.append(result);print(json.dumps(result),flush=True)
 if not passed:break
report={'passed':len(results)==len(steps) and all(r['passed'] for r in results),'packaged_game':True,'separate_processes':len(results),'isolated_slots':'C13_AutomatedCheckpoint_A/B','steps':results,'limits':['Authoritative fixture prepares bags/storage and invokes actual drop; production checkpoint code performs all serialization/validation/restoration.','Solo only: no cooperative reconnect claim; normal engine shutdown tested, not forced termination or power loss.']}
(ROOT/'logs/persistence_result.json').write_text(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
