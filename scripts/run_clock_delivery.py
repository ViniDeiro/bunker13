"""Final package checks, preserving the October evidence and executable."""
from pathlib import Path
import os,subprocess,json,shutil,re,hashlib
R=Path(__file__).resolve().parents[1];archive=R/'logs/clock_prior_evidence';archive.mkdir(exist_ok=True)
for pattern in ('round_*_result.json','round_regressions.json','round_reference_regression.json'):
 for f in (R/'logs').glob(pattern):
  if not (archive/f.name).exists():shutil.copy2(f,archive/f.name)
app=R/'builds/Mac/Condominio13-MVP-0.3.1.app';exe=app/'Contents/MacOS/Condominio13'
env=dict(os.environ,C13_TEST_EXE=str(exe),C13_TEST_APP='builds/Mac/Condominio13-MVP-0.3.1.app')
def run(name,args,environ=env):
 with (R/'logs'/f'clock_delivery_{name}.log').open('w') as out:p=subprocess.run(['python3',*args],cwd=R,env=environ,stdout=out,stderr=subprocess.STDOUT)
 print(name,p.returncode,flush=True)
 if p.returncode:raise SystemExit(p.returncode)
# The old binary writes an old-format checkpoint, then the new binary loads it.
oldenv=dict(env,C13_TEST_EXE=str(R/'builds/Mac/Condominio13-MVP.app/Contents/MacOS/Condominio13'))
run('legacy_seed',['scripts/run_round_validation.py','seed'],oldenv)
shutil.copy2(R/'logs/round_seed_solo.log',R/'logs/clock_legacy_seed.log')
run('legacy_load',['scripts/run_round_validation.py','load'])
text=(R/'logs/round_load_solo.log').read_text(errors='replace');legacy={'passed':'C13_CLOCK_RESTORED elapsed=0.000 day_seconds=240.0' in text and json.loads((R/'logs/round_load_result.json').read_text())['passed'],'old_version':'0.3.0','new_version':'0.3.1','default_elapsed':0,'default_day_seconds':240}
(R/'logs/clock_legacy_result.json').write_text(json.dumps(legacy,indent=2));assert legacy['passed']
for mode in ('walk','seed','load','network'):
 run('round_'+mode,['scripts/run_round_validation.py',mode]);shutil.copy2(R/f'logs/round_{mode}_result.json',R/f'logs/clock_round_{mode}_result.json')
run('clock',['scripts/run_clock_validation.py'])
# Exercise normal 240-second configuration through the real shelter transition.
with (R/'logs/clock_normal.log').open('w') as out:p=subprocess.run([str(exe),'/Game/Bunker/Lvl_CollectionRound','-C13Round','-C13RoundTest','-C13RoundReset','-C13ClockSave','-windowed','-ResX=960','-ResY=540','-stdout','-FullStdOutLogOutput'],stdout=out,stderr=subprocess.STDOUT,timeout=85)
text=(R/'logs/clock_normal.log').read_text(errors='replace');normal={'passed':p.returncode==0 and 'day_seconds=240.0' in text and bool(re.search(r'C13_CLOCK_SEED elapsed=[\d.]+ day=1',text)),'day_seconds':240}
(R/'logs/clock_normal_result.json').write_text(json.dumps(normal,indent=2));assert normal['passed']
run('regressions',['scripts/run_mvp_regressions.py']);shutil.copy2(R/'logs/round_regressions.json',R/'logs/clock_regressions.json')
manifest={'date':'2026-11-03','version':'0.3.1','executable':str(exe.relative_to(R)),'sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'previous_executable_preserved':hashlib.sha256((R/'builds/Mac/Condominio13-MVP.app/Contents/MacOS/Condominio13').read_bytes()).hexdigest()==json.loads((R/'logs/round_delivery_manifest.json').read_text())['executable_sha256'],'clock':json.loads((R/'logs/clock_result.json').read_text()),'normal_duration':normal,'legacy_compatibility':legacy,'round_checks':{m:json.loads((R/f'logs/clock_round_{m}_result.json').read_text())['checks'] for m in ('walk','seed','load','network')},'regressions':json.loads((R/'logs/clock_regressions.json').read_text()),'limits':['No human multiplayer, internet or Windows certification.','No new art or generator/event gameplay in this revision.']}
manifest['short_fps']=[]
for role in ('host','client'):
 m=re.search(r'C13_ROUND_FPS role=\w+ samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',(R/f'logs/round_network_{role}.log').read_text(errors='replace'));manifest['short_fps'].append({'role':role,'samples':int(m[1]),'fps':float(m[2]),'p95_ms':float(m[3])})
(R/'logs/clock_delivery_manifest.json').write_text(json.dumps(manifest,indent=2));print('DELIVERY_PASS',flush=True)
