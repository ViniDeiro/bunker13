"""Native expedition tests. Only the initial fixture positions players; the trip uses CharacterMovement."""
from pathlib import Path
import subprocess, time, json, re, os, shutil, argparse
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('mode',choices=['full','seed','continue','load','race']);p.add_argument('--editor',action='store_true');p.add_argument('--headless',action='store_true');p.add_argument('--players',type=int,choices=[1,2,4],default=4);p.add_argument('--resolution',default='960x540');a=p.parse_args();resx,resy=a.resolution.split('x')
exe=os.environ.get('C13_TEST_EXE',str(R/'builds/Mac/Condominio13-Expedition.app/Contents/MacOS/Condominio13'))
base=[exe] if not a.editor else ['/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd',str(R/'unreal/Condominio13/Condominio13.uproject')]
os.environ['DEVELOPER_DIR']='/Applications/Xcode.app/Contents/Developer';os.environ['TOOLCHAINS']='com.apple.dt.toolchain.Metal.32023.883'
kind=('editor_' if a.editor else 'package_')+a.mode
count=1 if a.mode=='load' else a.players
roles=['host']+[f'client{i}' for i in range(1,count)]
processes=[];files=[];start=time.time()
try:
 for i,role in enumerate(roles):
  out=(R/f'logs/supply_{kind}_{role}.log').open('w');files.append(out)
  url='/Game/Bunker/Lvl_CollectionRound?listen' if i==0 else '127.0.0.1:7797'
  cmd=base+[url,'-game','-C13Round','-C13Expedition','-C13RoundTest','-C13SupplyTest',f'-C13SupplyPlayers={count}',f'-C13SupplyRole={i}','-port=7797','-PktLag=80','-PktLoss=2','-windowed',f'-ResX={resx}',f'-ResY={resy}','-ForceRes','-stdout','-FullStdOutLogOutput']
  if a.mode in ('full','seed','race'):cmd+=['-C13RoundReset']
  if a.mode!='full':cmd += [{'seed':'-C13SupplySeedOutside','continue':'-C13SupplyContinue','load':'-C13SupplyLoad','race':'-C13SupplyRace'}[a.mode]]
  if i:cmd += [f'-C13RoundProfile={i}']
  if a.headless or i>=2:cmd += ['-nullrhi','-nosound','-unattended']
  processes.append(subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT))
  if i==0 and count>1:time.sleep(3)
 deadline=time.time()+420
 while processes[0].poll() is None and time.time()<deadline:
  if any(x.poll() not in (None,0) for x in processes):break
  time.sleep(.5)
 if processes[0].poll()==0:time.sleep(2)
finally:
 for proc in processes:
  if proc.poll() is None:
   proc.terminate()
   try:proc.wait(timeout=8)
   except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
 for out in files:out.close()
logs={role:(R/f'logs/supply_{kind}_{role}.log').read_text(errors='replace') for role in roles};host=logs['host']
checks={'host_exit_clean':processes[0].returncode==0,'no_runtime_timeout':'C13_SUPPLY_TIMEOUT' not in host and 'C13_SUPPLY_FALL' not in host,'valid_checkpoint':'C13_SAVE_REJECT' not in host,'all_processes_started':all(len(text)>1000 for text in logs.values()),'packet_emulation':all('PktLag set to 80' in text and 'PktLoss set to 2' in text for text in logs.values())}
if a.mode=='race':
 checks['one_owner']='C13_SUPPLY_RACE pass=1 owners=1 active=0' in host
 checks['remote_pickup']='remote_owner=1' in host
 checks['slots_preserve_item']='C13_SUPPLY_CAPACITY slots=1' in host
 checks['weight_preserves_item']='C13_SUPPLY_CAPACITY weight=1' in host
 checks['strict_schema']='C13_SUPPLY_SCHEMA missing=1 mixed=1 migration=1 duplicate=1' in host
elif a.mode=='seed':
 checks['outside_collected']='C13_SUPPLY_COLLECTED' in host and 'C13_SUPPLY_SEED_OUTSIDE' in host
 checks['physical_departure']=len(set(re.findall(r'C13_SUPPLY_WALK stage=7 point=(\d+)',host)))==11
 checks['initial_collection_and_closure']='C13_ROUND_STARTED duration=35' in host and 'C13_ROUND_SHELTER' in host
else:
 if a.mode=='load':checks['same_cache_not_respawned']='C13_SUPPLY_LOAD pass=1 count=6 inactive=2' in host
 else:
  checks['restored_generator']='C13_SUPPLY_RESTORED pass=1' in host
  checks['physical_return']=len(set(re.findall(r'C13_SUPPLY_WALK stage=11 point=(\d+)',host)))==11
  checks['consumed_exactly_two']=len(re.findall('C13_INFRA_CONSUMED action=[12]',host))==2
  checks['all_clients_see_power']=all(logs[role].rfind('C13_INFRA_POWER light=1 services=1')>logs[role].find('C13_INFRA_POWER light=0 services=0')>=0 for role in roles[1:])
  if a.mode=='continue':checks['outside_checkpoint_resumed']='C13_SUPPLY_RESUME_OUTSIDE pass=1' in host
 checks['strict_schema']='C13_SUPPLY_SCHEMA missing=1 mixed=1 migration=1 duplicate=1' in host
ids={m[1]:dict(id=m[2],active=int(m[3])) for m in re.finditer(r'C13_SUPPLY_ID key=(\w+) id=([A-Fa-f0-9]{32}) active=(\d)',host)}
if not ids:ids={m[1]:dict(id=m[2],active=1) for m in re.finditer(r'C13_SUPPLY_SPAWN key=(\w+) id=([A-Fa-f0-9]{32})',host)}
collected=re.search(r'C13_SUPPLY_COLLECTED fuel=([A-Fa-f0-9]{32}) parts=([A-Fa-f0-9]{32})',host)
race=re.search(r'C13_SUPPLY_RACE pass=1 owners=1 active=0 remote_owner=\d id=([A-Fa-f0-9]{32})',host)
for entry in ids.values():
 if (collected and entry['id'] in collected.groups()) or (race and entry['id']==race[1]):entry['active']=0
fps=[]
if not a.headless:
 for role in roles[:2]:
  for m in re.finditer(r'C13_SUPPLY_FPS role=\w+ samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',logs[role]):fps.append(dict(role=role,samples=int(m[1]),fps=float(m[2]),p95_ms=float(m[3])))
snap=R/'unreal/Condominio13/Saved/Screenshots/MacEditor' if a.editor else Path.home()/'Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/Screenshots/Mac'
for f in snap.glob('supply_*.png'):
 if f.stat().st_mtime>=start:shutil.copy2(f,R/'screenshots'/f.name)
result=dict(passed=all(checks.values()),mode=a.mode,checks=checks,ids=ids,fps=fps,connections=count,resolution=a.resolution,rendered_instances=0 if a.headless else min(2,count),exit_codes=[x.returncode for x in processes],limits=['Automated local processes, not human playtest or Internet.','Initial fixture creates a reproducible crisis; no teleports between departure, cache and return.','Host restart is intentional in seed/continue; remote processes are closed after host exits.','Radiation, enemies, combat and death remain separate milestones.'])
(R/f'logs/supply_{kind}_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
