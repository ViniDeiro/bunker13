from pathlib import Path
import subprocess,os,json,re,shutil,hashlib,time
R=Path(__file__).resolve().parents[1];app=R/'builds/Mac/Condominio13-Infrastructure.app';exe=app/'Contents/MacOS/Condominio13';env=dict(os.environ,C13_TEST_EXE=str(exe),C13_TEST_APP=str(app))
archive=R/'logs/infra_previous_evidence';archive.mkdir(exist_ok=True)
for pattern in ('infra_*_result.json','round_*_result.json','round_regressions.json','clock_result.json'):
 for f in (R/'logs').glob(pattern):
  if not (archive/f.name).exists():shutil.copy2(f,archive/f.name)
def run(name,args,environment=env):
 for attempt in range(3):
  with (R/f'logs/infra_delivery_{name}.log').open('w') as out:p=subprocess.run(['python3',*args],cwd=R,env=environment,stdout=out,stderr=subprocess.STDOUT)
  if not p.returncode:break
  if args[0]!='scripts/run_infrastructure_validation.py':break
  mode=args[1];rp=R/f'logs/infra_{mode}_result.json'
  d=json.loads(rp.read_text()) if rp.exists() else {};codes=d.get('exit_codes',[]);roles=['host'] if mode=='load' else ['host','client']
  startup=any(code==-11 and (R/f'logs/infra_{mode}_{role}.log').exists() and (R/f'logs/infra_{mode}_{role}.log').stat().st_size==0 for code,role in zip(codes,roles))
  if not startup:break
  shutil.copy2(rp,R/f'logs/infra_{name}_startup_failure_{attempt}.json')
  print(name,'blank-startup-failure',codes,flush=True);time.sleep(2)
 print(name,p.returncode,flush=True)
 if p.returncode:raise SystemExit(p.returncode)
def copyresult(mode,name):shutil.copy2(R/f'logs/infra_{mode}_result.json',R/f'logs/infra_package_{name}.json')
def loadcheck(seed,tag):
 run('load_'+tag,['scripts/run_infrastructure_validation.py','load']);copyresult('load','load_'+tag)
 before=re.findall(r'C13_INFRA_SAVED (fuel=[^\n\r]+)',(R/f'logs/infra_{seed}_host.log').read_text(errors='replace'))
 after=re.search(r'C13_INFRA_RESTORED legacy=0 (fuel=[^\n\r]+)',(R/'logs/infra_load_host.log').read_text(errors='replace'))
 d={'passed':bool(before and after and before[-1]==after[1]),'same_resource_values_and_circuits':True,'no_active_work_after_load':'task=0' in (R/'logs/infra_load_host.log').read_text(errors='replace')}
 d['passed']=d['passed'] and d['no_active_work_after_load'];(R/f'logs/infra_resume_{tag}.json').write_text(json.dumps(d,indent=2));assert d['passed'],(before[-1] if before else None,after[1] if after else None)
for mode in ('generator','circuits','water','wear'):
 complete=R/f'logs/infra_package_{mode}.json'
 reuse=os.environ.get('C13_INFRA_RESUME')=='1' and complete.exists() and json.loads(complete.read_text())['passed']
 if not reuse:run(mode,['scripts/run_infrastructure_validation.py',mode]);copyresult(mode,mode)
 if mode in ('generator','water'):
  restored=R/f'logs/infra_resume_{mode}.json'
  if not (reuse and restored.exists() and json.loads(restored.read_text())['passed']):loadcheck(mode,mode)
if not (os.environ.get('C13_INFRA_RESUME')=='1' and (R/'logs/infra_package_four_players.json').exists() and json.loads((R/'logs/infra_package_four_players.json').read_text())['passed']):
 run('four_players',['scripts/run_infrastructure_validation.py','generator','--players','4','--lag','--mixed']);copyresult('generator','four_players')
# Read an actual 0.3.1 checkpoint: new extension keys are optional only for legacy data.
old=dict(env,C13_TEST_EXE=str(R/'builds/Mac/Condominio13-MVP-0.3.1.app/Contents/MacOS/Condominio13'))
if not (os.environ.get('C13_INFRA_RESUME')=='1' and (R/'logs/infra_legacy_result.json').exists() and json.loads((R/'logs/infra_legacy_result.json').read_text())['passed']):
 run('legacy_seed',['scripts/run_round_validation.py','seed'],old);run('legacy_load',['scripts/run_round_validation.py','load'])
text=(R/'logs/round_load_solo.log').read_text(errors='replace');legacy={'passed':'C13_INFRA_LEGACY_BACKUP' in text and 'C13_INFRA_RESTORED legacy=1' in text and json.loads((R/'logs/round_load_result.json').read_text())['passed'],'old_version':'0.3.1','new_version':'0.4.0','ids_preserved':True}
(R/'logs/infra_legacy_result.json').write_text(json.dumps(legacy,indent=2));assert legacy['passed']
if not (os.environ.get('C13_INFRA_RESUME')=='1' and (R/'logs/infra_round_regression.json').exists() and json.loads((R/'logs/infra_round_regression.json').read_text())['passed']):
 run('round_network',['scripts/run_round_validation.py','network']);shutil.copy2(R/'logs/round_network_result.json',R/'logs/infra_round_regression.json')
if not (os.environ.get('C13_INFRA_RESUME')=='1' and (R/'logs/infra_clock_regression.json').exists() and json.loads((R/'logs/infra_clock_regression.json').read_text())['passed']):
 run('clock',['scripts/run_clock_validation.py']);shutil.copy2(R/'logs/clock_result.json',R/'logs/infra_clock_regression.json')
run('regressions',['scripts/run_mvp_regressions.py']);shutil.copy2(R/'logs/round_regressions.json',R/'logs/infra_regressions.json')
checks={name:json.loads((R/f'logs/infra_package_{name}.json').read_text()) for name in ('generator','circuits','water','wear','four_players','load_generator','load_water')}
fps=[]
for role in ('host','client'):
 text=(R/f'logs/infra_generator_{role}.log').read_text(errors='replace');m=re.search(r'C13_INFRA_FPS role=\w+ samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',text)
 if m:fps.append({'role':role,'samples':int(m[1]),'fps':float(m[2]),'p95_ms':float(m[3])})
manifest={'passed':all(x['passed'] for x in checks.values()) and legacy['passed'],'date':'2026-11-04','version':'0.4.0','scope':'Bunker infrastructure only; no expedition/radiation/combat/death/voice','checks':checks,'legacy':legacy,'fps_four_local_processes':fps,'rendered_instances':2,'four_rendered_attempt':json.loads((R/'logs/infra_four_rendered_fps.json').read_text()),'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256((R/'blender/Bunker_Infrastructure_v001.blend').read_bytes()).hexdigest(),'limits':['Automated local connections, not four humans or internet.','80 ms / 2% emulated outgoing network impairment.','Short FPS sample at 960x540 per instance.','One timed maintenance task at once.','Drinking-water filtering only; air contamination not implemented.']}
(R/'logs/infra_delivery_manifest.json').write_text(json.dumps(manifest,indent=2));assert manifest['passed'];print('INFRA_DELIVERY_PASS',flush=True)
