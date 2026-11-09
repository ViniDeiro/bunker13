from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1];E=R/'unreal/Condominio13/Saved/StagedBuilds/Mac/Condominio13.app/Contents/MacOS/Condominio13';rows=[]
for phase in ['reference_seed','reference_load','reference_badslot','reference_legacy','reference_migrate']:
 p=R/f'logs/{phase}.log'
 with p.open('w') as out:r=subprocess.run([str(E),'-C13SaveProbe',f'-C13SavePhase={phase}','-game','-nullrhi','-RenderOffScreen','-nosound','-unattended','-NoSteam','-stdout','-FullStdOutLogOutput'],stdout=out,stderr=subprocess.STDOUT,timeout=40)
 text=p.read_text(errors='replace');ok=r.returncode==0 and f'C13_SAVE_PROBE PASS phase={phase}' in text;row={'phase':phase,'passed':ok,'exit_code':r.returncode,'markers':[l for l in text.splitlines() if 'C13_SAVE_' in l]};rows.append(row);print(json.dumps(row),flush=True)
 if not ok:break
result={'passed':len(rows)==5 and all(r['passed'] for r in rows),'isolated_test_checkpoint':True,'processes':len(rows),'checks':rows};(R/'logs/reference_save_result.json').write_text(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
