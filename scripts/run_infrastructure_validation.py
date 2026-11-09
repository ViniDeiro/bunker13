"""Rendered native Unreal game instances; fixtures position players, production E performs operations."""
from pathlib import Path
import subprocess,time,json,re,os,shutil,argparse
R=Path(__file__).resolve().parents[1];P=argparse.ArgumentParser();P.add_argument('mode',choices=['generator','circuits','water','load','wear']);P.add_argument('--editor',action='store_true');P.add_argument('--players',type=int,choices=[2,4],default=2);P.add_argument('--lag',action='store_true');P.add_argument('--mixed',action='store_true');a=P.parse_args();exe=os.environ.get('C13_TEST_EXE',str(R/'builds/Mac/Condominio13-Infrastructure.app/Contents/MacOS/Condominio13'))
base=[exe]
if a.editor:base=['/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd',str(R/'unreal/Condominio13/Condominio13.uproject')]
processes=[];outputs=[];logs={};start=time.time()
os.environ['DEVELOPER_DIR']='/Applications/Xcode.app/Contents/Developer';os.environ['TOOLCHAINS']='com.apple.dt.toolchain.Metal.32023.883'
try:
 roles=['host'] if a.mode=='load' else (['host','client'] if a.players==2 else ['host','client','client2','client3'])
 for index,role in enumerate(roles):
  f=(R/f'logs/infra_{a.mode}_{role}.log').open('w');outputs.append(f)
  url='/Game/Bunker/Lvl_CollectionRound?listen' if role=='host' else '127.0.0.1:7795'
  cmd=base+[url,'-game','-C13Round','-C13RoundTest','-C13InfraTest','-windowed','-ResX=960','-ResY=540','-ForceRes','-port=7795','-stdout','-FullStdOutLogOutput','-LogCmds="LogTemp Verbose"']
  if a.mode=='load':cmd+=['-C13InfraLoad']
  else:cmd+=['-C13RoundReset']
  if a.mode in ('circuits','water','wear'):cmd+=['-C13Infra'+a.mode.title()]
  if role!='host':cmd+=[f'-C13RoundProfile={index}']
  cmd+=[f'-C13InfraPlayers={a.players}',f'-C13InfraRole={index}']
  if a.lag:cmd+=['-PktLag=80','-PktLoss=2']
  if a.mixed and index>=2:cmd+=['-nullrhi','-nosound','-unattended']
  p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);processes.append(p)
  if role=='host' and a.mode!='load':time.sleep(3)
 for p in processes:p.wait(timeout=300 if a.players==4 else 180 if a.editor else 100)
finally:
 for p in processes:
  if p.poll() is None:
   p.terminate()
   try:p.wait(timeout=8)
   except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
 for f in outputs:f.close()
for role in roles:logs[role]=(R/f'logs/infra_{a.mode}_{role}.log').read_text(errors='replace')
text='\n'.join(logs.values());checks={'processes_exited':all(p.returncode==0 for p in processes),'checkpoint_valid':'C13_SAVE_REJECT' not in text}
if a.mode=='generator':
 for k in ('stop','refuel','repair','running','ownership'):checks[k]=f'C13_INFRA_CHECK {k}=1' in logs['host']
 checks['single_fuel_and_parts_consumption']=len(re.findall('C13_INFRA_CONSUMED action=[12]',logs['host']))==2
 checks['interrupted_work_cancelled']=logs['host'].count('C13_INFRA_CANCEL')>=3
 finals=[re.search(r'C13_INFRA_FINAL role=\w+ fuel=([\d.]+) condition=([\d.]+) running=(\d)',logs[x]) for x in roles]
 checks['state_agrees']=bool(all(finals) and all(abs(float(finals[0][1])-float(x[1]))<.03 and abs(float(finals[0][2])-float(x[2]))<.03 and x[3]=='0' for x in finals))
elif a.mode=='wear':checks['wear_stop']='C13_INFRA_CHECK wear_stop=1' in text
elif a.mode=='load':checks['restored']='C13_INFRA_RESTORED legacy=0' in text and 'C13_INFRA_LOAD' in text
else:
 for k in ({'circuits':['lights_off','services_off','emergency','restored_power','fuel_saving'],'water':['filtering','power_stops_filtering','drink_consumed','filter_replaced','finite_water']}[a.mode]):checks[k]=bool(re.search(r'C13_INFRA_CHECK[^\n]*\b'+k+r'=1\b',text))
if a.players==4:checks['remote_controls_used']=all(f'C13_INFRA_REMOTE role={i} interacted=1' in logs[f'client{i}'] for i in (2,3)) and 'C13_INFRA_DRINK' in logs['host'] and 'C13_INFRA_CIRCUIT action=3' in logs['host']
if a.lag:checks['packet_emulation']=all('PktLag set to 80' in x and 'PktLoss set to 2' in x for x in logs.values())
snap=Path.home()/('Library/Application Support/Epic/Condominio13/Saved/Screenshots/MacEditor' if a.editor else 'Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/Screenshots/Mac')
if a.editor:snap=R/'unreal/Condominio13/Saved/Screenshots/MacEditor'
for f in snap.glob('infra_*.png'):
 if f.stat().st_mtime>=start:shutil.copy2(f,R/'screenshots'/f.name)
result={'mode':a.mode,'connections':len(processes),'rendered_instances':min(2,len(processes)) if a.mixed else len(processes),'packet_emulation':a.lag,'exit_codes':[p.returncode for p in processes],'passed':all(checks.values()),'checks':checks,'runtime':'UnrealEditor -game' if a.editor else 'packaged game','limits':['Scripted local processes, not two humans or internet.','Fixture positions and damaged/low-fuel state are test-only.','Actual E input and authoritative inventory transactions used.']};(R/f'logs/infra_{a.mode}_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
