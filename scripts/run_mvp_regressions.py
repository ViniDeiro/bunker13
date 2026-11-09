"""Run established suites against the NEW package, preserving previous evidence."""
from pathlib import Path
import subprocess,shutil,json,os,time
R=Path(__file__).resolve().parents[1];archive=R/'logs/round_prior_regressions';archive.mkdir(exist_ok=True)
target=os.environ.get('C13_TEST_APP','builds/Mac/Condominio13-MVP.app')
prior_path=R/'logs/round_regressions.json'
prior=json.loads(prior_path.read_text()).get('suites',[]) if prior_path.exists() else []
rows=[]
for script,result in [('run_persistence_test','persistence_result'),('run_storage_network','storage_network_result'),('run_reconnect_test','reconnect_result')]:
 old=next((x for x in prior if x.get('suite')==script and x.get('passed') and x.get('executable')==target),None)
 if os.environ.get('C13_REGRESSION_RESUME')=='1' and old:rows.append(old);print({**old,'reused':True},flush=True);continue
 previous=R/'logs'/f'{result}.json'
 if previous.exists() and not (archive/previous.name).exists():shutil.copy2(previous,archive/previous.name)
 source=R/'scripts'/f'{script}.py'
 wrapper="from pathlib import Path\np=Path("+repr(str(source))+")\nexec(compile(p.read_text().replace('builds/Mac/Condominio13-VerticalSlice.app',"+repr(target)+"),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})\n"
 for attempt in range(3):
  with (R/'logs'/f'round_regression_{script}.log').open('w') as out:p=subprocess.run(['python3','-c',wrapper],stdout=out,stderr=subprocess.STDOUT)
  if p.returncode==0 or script!='run_storage_network':break
  blank=any((R/f'logs/storage_network_{i}.log').exists() and (R/f'logs/storage_network_{i}.log').stat().st_size==0 for i in range(4))
  if not blank:break
  shutil.copy2(previous,R/f'logs/infra_storage_startup_failure_{attempt}.json');print({'suite':script,'blank_startup_retry':attempt},flush=True);time.sleep(2)

 report=json.loads(previous.read_text()) if previous.exists() else {};rows.append({'suite':script,'passed':p.returncode==0 and report.get('passed',False),'executable':target,'result':result});print(rows[-1],flush=True)
 if not rows[-1]['passed']:break
passed=len(rows)==3 and all(row['passed'] for row in rows)
if passed:
 with (R/'logs/round_regression_reference.log').open('w') as out:p=subprocess.run(['python3',str(R/'scripts/run_reference_validation.py'),'--mode','network'],stdout=out,stderr=subprocess.STDOUT)
 ref=json.loads((R/'logs/reference_network_result.json').read_text());shutil.copy2(R/'logs/reference_network_result.json',R/'logs/round_reference_regression.json');rows.append({'suite':'reference_physical_cabinet','passed':p.returncode==0 and ref['passed']});passed=all(x['passed'] for x in rows)
(R/'logs/round_regressions.json').write_text(json.dumps({'passed':passed,'suites':rows},indent=2));raise SystemExit(0 if passed else 1)
