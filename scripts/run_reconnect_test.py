"""Four packaged instances, durable private test profiles, disconnect/restart and rejection tests."""
from pathlib import Path
import subprocess,time,json
ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'builds/Mac/Condominio13-VerticalSlice.app/Contents/MacOS/Condominio13'
processes={};handles=[];checks={};events=[]
def read(tag):
 return (ROOT/f'logs/reconnect_{tag}.log').read_text(errors='replace')
def start(tag,index=0,*,host=False,reset=False,check=False,invalid=False,restore=False,shutdown=False,damage=False):
 out=(ROOT/f'logs/reconnect_{tag}.log').open('w');handles.append(out)
 args=[str(EXE),'/Game/Bunker/Lvl_Bunker?listen' if host else '127.0.0.1:7791','-port=7791','-C13ReconnectTest',f'-C13ReconnectProfile={index}','-PktLag=80','-PktLoss=2','-game','-nullrhi','-RenderOffScreen','-nosound','-unattended','-NoSteam','-stdout','-FullStdOutLogOutput']
 if host:args.append('-C13ReconnectStage=restore' if restore else '-C13ReconnectStage=seed')
 if reset:args.append('-C13ReconnectReset')
 if check:args.append('-C13ReconnectCheck')
 if invalid:args.append('-C13ReconnectInvalid')
 if shutdown:args.append('-C13ReconnectShutdown')
 if damage:args.append('-C13ReconnectDamageProfile')
 p=subprocess.Popen(args,stdout=out,stderr=subprocess.STDOUT);processes[tag]=p
 return p
def wait(tag,marker,timeout=30,after=0):
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  if marker in read(tag)[after:]:return True
  if processes[tag].poll() is not None:return False
  time.sleep(.2)
 return False
def require(name,value):
 checks[name]=bool(value);print(json.dumps({'check':name,'passed':checks[name]}),flush=True)
 if not value:raise RuntimeError(name)
def stop(tag):
 p=processes[tag]
 if p.poll() is None:p.terminate()
 try:p.wait(timeout=10)
 except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
 return p.returncode
try:
 start('host',host=True,reset=True)
 require('host_prepared',wait('host','C13_RECONNECT_HOST prepared=1'))
 for i in range(1,4):start(f'initial_{i}',i,reset=True);time.sleep(.4)
 for i in range(1,4):require(f'initial_owner_{i}',wait(f'initial_{i}',f'C13_RECONNECT_CLIENT PASS role={i}'))
 require('four_unique_players',wait('host','C13_RECONNECT_AUDIT PASS ready=3 beds=1 unique=6'))
 offset=len(read('host'));stop('initial_1')
 require('disconnect_releases_bed',wait('host','C13_RECONNECT_AUDIT PASS ready=2 beds=0 unique=6',after=offset))
 start('resumed_1',1,check=True,damage=True)
 require('same_profile_restored',wait('resumed_1','C13_RECONNECT_CLIENT PASS role=1'))
 require('credential_backup_recovers', 'C13_RECONNECT_PROFILE_BACKUP remaining=1' in read('resumed_1'))
 require('no_duplicate_after_resume',wait('host','C13_RECONNECT_AUDIT PASS ready=3 beds=0 unique=6'))
 offset=len(read('host'));stop('initial_3')
 require('third_player_reserved',wait('host','C13_RECONNECT_AUDIT PASS ready=2 beds=0 unique=6',after=offset))
 offset=len(read('host'));start('duplicate',1,check=True)
 require('active_character_rejected',wait('host','C13_RECONNECT_REJECT active',after=offset));stop('duplicate')
 offset=len(read('host'));start('invalid',4,invalid=True)
 require('unknown_credential_rejected',wait('host','C13_RECONNECT_REJECT invalid',after=offset));stop('invalid')
 offset=len(read('host'));start('stranger',4)
 require('reserved_roster_rejects_stranger',wait('host','C13_RECONNECT_REJECT roster',after=offset));stop('stranger')
 start('resumed_3',3,check=True,shutdown=True)
 require('reserved_third_restored',wait('resumed_3','C13_RECONNECT_CLIENT PASS role=3'))
 try:hostcode=processes['host'].wait(timeout=12)
 except subprocess.TimeoutExpired:hostcode='timeout'
 hostlog=read('host');after=hostlog.split('C13_RECONNECT_QUIT requested=1')[-1]
 require('host_graceful_checkpoint',hostcode==0 and 'C13_RECONNECT_QUIT requested=1' in hostlog and 'C13_SAVE_COMMIT' in after)
 require('cross_player_duplicate_save_rejected','C13_RECONNECT_DUPLICATE_SAVE rejected=1' in hostlog)
 # The engine closes the network session when the listen host exits.
 time.sleep(2)
 lost={tag:any(s in read(tag) for s in ('NetworkFailure','ConnectionLost','Host closed the connection','Connection closed')) for tag in ('resumed_1','initial_2','resumed_3')}
 events.append({'host_exit_network_observed':lost})
 for tag in ('resumed_1','initial_2','resumed_3'):stop(tag)
 start('restored_host',host=True,restore=True)
 require('host_restart_restores_offline_roster',wait('restored_host','C13_RECONNECT_AUDIT PASS ready=0 beds=0 unique=6'))
 for i in range(1,4):start(f'restored_{i}',i,check=True);time.sleep(.4)
 for i in range(1,4):require(f'disk_profile_restores_player_{i}',wait(f'restored_{i}',f'C13_RECONNECT_CLIENT PASS role={i}'))
 require('full_restart_has_no_duplicates',wait('restored_host','C13_RECONNECT_AUDIT PASS ready=3 beds=0 unique=6'))
 require('packet_emulation_enabled',all('PktLag set to 80' in read(tag) and 'PktLoss set to 2' in read(tag) for tag in ('host','restored_host','restored_1','restored_2','restored_3')))
 require('clients_do_not_write_campaign',all('C13_SAVE_' not in read(tag) for tag in processes if tag not in ('host','restored_host')))
except Exception as error:
 events.append({'error':str(error)})
finally:
 for tag in list(processes):stop(tag)
 for out in handles:out.close()
markers={tag:[line for line in read(tag).splitlines() if any(m in line for m in ('C13_RECONNECT','C13_SAVE_','PktLag set','PktLoss set'))] for tag in processes}
report={'passed':bool(checks) and all(checks.values()) and not any('error' in event for event in events),'packaged_game':True,'max_simultaneous_connections':4,'processes_started':len(processes),'packet_simulation':{'outgoing_lag_ms':80,'outgoing_loss_percent':2},'isolated_slots':'C13_TestCoopCheckpoint and C13_TestReconnectProfile_0..8','checks':checks,'events':events,'markers':markers,'limits':['Development fixtures prepare six real item meshes and one occupied bed; production persistence/credential/RPC code handles disconnect and restoration.','Private local campaign tickets, not Steam account authentication; no internet-security or human endurance claim.']}
(ROOT/'logs/reconnect_result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':checks,'events':events},indent=2));raise SystemExit(0 if report['passed'] else 1)
