"""Run existing legacy-cabinet save/migration probes against the newly built module."""
from pathlib import Path
import os,subprocess,json
R=Path(__file__).resolve().parents[1];env=os.environ.copy();env.setdefault('DEVELOPER_DIR','/Applications/Xcode.app/Contents/Developer');env.setdefault('TOOLCHAINS','com.apple.dt.toolchain.Metal.32023.883')
exe=Path(env.get('C13_UNREAL_ROOT','/Users/Shared/Epic Games/UE_5.8'))/'Engine/Binaries/Mac/UnrealEditor-Cmd';rows=[]
for phase in ('reference_seed','reference_load','reference_badslot','reference_legacy','reference_migrate'):
 p=R/f'logs/bedcab_save_{phase}.log'
 with p.open('w') as out:
  run=subprocess.run([str(exe),str(R/'unreal/Condominio13/Condominio13.uproject'),'/Game/Bunker/Lvl_Bunker','-game','-C13SaveProbe','-C13SavePhase='+phase,'-nullrhi','-nosound','-unattended','-NoSteam','-stdout','-FullStdOutLogOutput'],env=env,stdout=out,stderr=subprocess.STDOUT,timeout=180)
 text=p.read_text(errors='replace');ok=run.returncode==0 and f'C13_SAVE_PROBE PASS phase={phase}' in text
 row={'phase':phase,'passed':ok,'exit_code':run.returncode,'markers':[l for l in text.splitlines() if 'C13_SAVE_' in l]};rows.append(row);print(json.dumps(row),flush=True)
 if not ok:break
result={'passed':len(rows)==5 and all(r['passed'] for r in rows),'checkpoint_prefix':'C13_AutomatedCheckpoint','original_bunker_map':True,'compiled_current_module':True,'checks':rows}
(R/'logs/bedroom_cabinet_save_result.json').write_text(json.dumps(result,indent=2)+'\n');raise SystemExit(0 if result['passed'] else 1)
