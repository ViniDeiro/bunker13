"""Verify the finite cache, cooperative trip, host restart and additive legacy migration."""
from pathlib import Path
import subprocess, os, json, re, shutil, hashlib, struct, argparse, time
R=Path(__file__).resolve().parents[1];app=R/'builds/Mac/Condominio13-Expedition.app';exe=app/'Contents/MacOS/Condominio13'
p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');a=p.parse_args()
digest=hashlib.sha256(exe.read_bytes()).hexdigest();path=R/'logs/supply_delivery_manifest.json'
old=json.loads(path.read_text()) if path.exists() else {};rows=old.get('steps',{}) if a.resume and old.get('executable_sha256')==digest else {}
archive=R/'logs/supply_prior';archive.mkdir(exist_ok=True)
for pattern in ('round_seed_*','round_load_*','reconnect_*.log','reconnect_result.json','airlock_package_*'):
 for source in (R/'logs').glob(pattern):
  dest=archive/source.name
  if source.is_file() and not dest.exists():shutil.copy2(source,dest)
env=dict(os.environ,C13_TEST_EXE=str(exe));env.pop('C13_TEST_EXTRA',None)
def commit():
 path.write_text(json.dumps(dict(version='0.4.2',date='2026-11-05',scope='Finite supply expedition; no radiation/enemies/combat/death/voice',executable_sha256=digest,steps=rows,passed=False),indent=2))
def run(name,args,result,environment=env):
 if rows.get(name,{}).get('passed'):print(name,'cached for identical executable',flush=True);return
 for attempt in range(3):
  with (R/f'logs/supply_delivery_{name}.log').open('w') as out:proc=subprocess.run(['python3',*args],cwd=R,env=environment,stdout=out,stderr=subprocess.STDOUT)
  report=R/'logs'/result;data=json.loads(report.read_text()) if report.exists() else {}
  if proc.returncode==0:break
  # Preserve and retry only the already-known pre-log native Mac crash.
  if args[0]!='scripts/run_supply_validation.py':break
  mode=args[1];roles=['host']+[f'client{i}' for i in range(1,data.get('connections',1))]
  blank=any(code==-11 and (R/f'logs/supply_package_{mode}_{role}.log').exists() and (R/f'logs/supply_package_{mode}_{role}.log').stat().st_size==0 for role,code in zip(roles,data.get('exit_codes',[])))
  if not blank:break
  for f in (R/'logs').glob(f'supply_package_{mode}_*'):
   if f.is_file():shutil.copy2(f,R/'logs'/f'supply_{name}_startup_failure_{attempt}_{f.name}')
  print(name,'pre-log startup retry',attempt,flush=True);time.sleep(2)
 rows[name]=dict(passed=proc.returncode==0 and data.get('passed',False),exit_code=proc.returncode,result=f'logs/supply_verified_{name}.json')
 if report.exists():shutil.copy2(report,R/f'logs/supply_verified_{name}.json')
 commit();print(name,rows[name],flush=True)
 if not rows[name]['passed']:raise SystemExit(1)

run('race',['scripts/run_supply_validation.py','race','--players','4'],'supply_package_race_result.json')
run('seed',['scripts/run_supply_validation.py','seed','--players','4'],'supply_package_seed_result.json')
run('continue',['scripts/run_supply_validation.py','continue','--players','4'],'supply_package_continue_result.json')
run('load',['scripts/run_supply_validation.py','load'],'supply_package_load_result.json')
run('solo',['scripts/run_supply_validation.py','full','--players','1','--resolution','1280x720'],'supply_package_full_result.json')
# Separate old/new executable processes; do not use a synthetic legacy save.
slots=Path.home()/'Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/SaveGames'
if not rows.get('migration',{}).get('passed'):
 oldenv=dict(env,C13_TEST_EXE=str(R/'builds/Mac/Condominio13-Airlock.app/Contents/MacOS/Condominio13'))
 run('legacy_seed',['scripts/run_round_validation.py','seed'],'round_seed_result.json',oldenv)
 prior_bytes=[f.read_bytes() for f in slots.glob('C13_TestRound_[AB].sav')]
 newenv=dict(env,C13_TEST_EXTRA='-C13Expedition')
 run('legacy_load',['scripts/run_round_validation.py','load'],'round_load_result.json',newenv)
 first=(R/'logs/round_load_solo.log').read_text(errors='replace');shutil.copy2(R/'logs/round_load_solo.log',R/'logs/supply_migration_first.log')
 introduced={m[1]:m[2] for m in re.finditer(r'C13_SUPPLY_SPAWN key=(\w+) id=([A-Fa-f0-9]{32})',first)}
 run('legacy_reload',['scripts/run_round_validation.py','load'],'round_load_result.json',newenv)
 second=(R/'logs/round_load_solo.log').read_text(errors='replace');shutil.copy2(R/'logs/round_load_solo.log',R/'logs/supply_migration_second.log')
 latest=max(slots.glob('C13_TestRound_[AB].sav'),key=lambda f:f.stat().st_mtime).read_bytes()
 backups=[f.read_bytes() for f in slots.glob('C13_TestRound_PreSupplyV1_*.sav')]
 checks=dict(old_ids_preserved=all(json.loads((R/f'logs/supply_verified_{name}.json').read_text())['checks']['same_item_guid'] for name in ('legacy_load','legacy_reload')),raw_backups_verified=len(prior_bytes)==2 and all(data in backups for data in prior_bytes),introduced_once='C13_SUPPLY_LEGACY_BACKUP' in first and 'C13_SUPPLY_RESTORED introduced=0' in first and 'C13_SUPPLY_LEGACY_BACKUP' not in second and 'C13_SUPPLY_RESTORED introduced=1' in second,checksum_valid=hashlib.sha1(latest[:-20]).digest()==latest[-20:],six_new_ids_survive_reload=len(introduced)==6 and all(struct.pack('<IIII',*(int(guid[i:i+8],16) for i in (0,8,16,24))) in latest for guid in introduced.values()))
 migration=dict(passed=all(checks.values()),checks=checks,old_version='0.4.1',new_version='0.4.2',note='FGuid uses four serialized uint32 words; verify original cache IDs in a checksum-validated checkpoint after a second process reload.')
 (R/'logs/supply_migration_result.json').write_text(json.dumps(migration,indent=2));rows['migration']=dict(passed=migration['passed'],result='logs/supply_migration_result.json');commit();print('migration',migration,flush=True)
 if not migration['passed']:raise SystemExit(1)

seed=json.loads((R/'logs/supply_verified_seed.json').read_text());returned=json.loads((R/'logs/supply_verified_continue.json').read_text());loaded=json.loads((R/'logs/supply_verified_load.json').read_text())
same=len(seed['ids'])==6 and all(seed['ids'][key]['id']==returned['ids'][key]['id']==loaded['ids'][key]['id'] for key in seed['ids'])
checks=dict(same_six_guids_across_host_restart=same,exactly_two_cache_tombstones=sum(row['active']==0 for row in loaded['ids'].values())==2,three_participants_reconnected=(R/'logs/supply_package_continue_host.log').read_text(errors='replace').count('C13_RECONNECT_BOUND')>=3)
(R/'logs/supply_identity_result.json').write_text(json.dumps(dict(passed=all(checks.values()),checks=checks),indent=2));rows['identity']=dict(passed=all(checks.values()),result='logs/supply_identity_result.json');commit()
manifest=json.loads(path.read_text());manifest['passed']=all(row['passed'] for row in rows.values());path.write_text(json.dumps(manifest,indent=2));print('SUPPLY_DELIVERY',manifest['passed'],flush=True);raise SystemExit(0 if manifest['passed'] else 1)
