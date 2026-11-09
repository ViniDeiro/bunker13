"""Rendered packaged-game evidence; two actual processes, no production save access."""
from pathlib import Path
import subprocess,time,json,re,shutil,argparse
R=Path(__file__).resolve().parents[1];P=argparse.ArgumentParser();P.add_argument('--mode',choices=['after','network','video'],default='after');opt=P.parse_args()
exe=R/'unreal/Condominio13/Saved/StagedBuilds/Mac/Condominio13.app/Contents/MacOS/Condominio13'
logs=[];procs=[];started=time.time()
def run(role,args,res):
 log=R/f'logs/reference_{opt.mode}_{role}.log';out=log.open('w');p=subprocess.Popen([str(exe),*args,'-windowed',f'-ResX={res[0]}',f'-ResY={res[1]}','-ForceRes','-C13Reference','-stdout','-FullStdOutLogOutput'],stdout=out,stderr=subprocess.STDOUT);logs.append((role,log,out));procs.append(p)
try:
 if opt.mode=='after':run('solo',['-ReferencePhase=after'],(1280,720))
 else:
  # The round fixture flag only suppresses real mouse input here; no round director exists on this map.
  args=['-C13PhysicalTest','-C13RoundTest']+(['-C13ReferenceVideo'] if opt.mode=='video' else [])
  run('host',['/Game/Bunker/Lvl_Bunker?listen','-port=7793',*args],(960,540));time.sleep(3)
  run('client',['127.0.0.1:7793',*args],(800,450))
 for p in procs:p.wait(timeout=max(5,110-(time.time()-started)))
finally:
 for p in procs:
  if p.poll() is None:p.terminate();p.wait(timeout=8)
 for _,_,o in logs:o.close()
source=Path('/Users/vini_deiro/Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/Screenshots/Mac')
output=R/('output/reference_video_frames' if opt.mode=='video' else 'screenshots');output.mkdir(parents=True,exist_ok=True)
for f in source.glob('refvideo_*.png' if opt.mode=='video' else 'reference_after_*.png'):
 if f.stat().st_mtime>=started:shutil.copy2(f,output/f.name)
markers={role:[line for line in log.read_text(errors='replace').splitlines() if any(k in line for k in ['C13_REFERENCE_','C13_PHYSICAL_','C13_TWO_PLAYER_','C13_CONSUME','C13_HAND_ACTION','C13_OBSERVED_ACTION','C13_REFERENCE_CIRCULATION','C13_REFERENCE_ROUTE_BLOCK'])] for role,log,_ in logs}
result={'mode':opt.mode,'rendered':True,'processes':len(procs),'exit_codes':[p.returncode for p in procs],'markers':markers,'scope':'Scripted actions in the packaged Unreal game; not a human playtest.'}
if opt.mode!='after':
 text='\n'.join(sum(markers.values(),[]));result['checks']={'two_players': 'players=2' in text,'unique_ownership':'ownership=1' in text,'no_stock_modal':all('modal=0' in l for l in text.splitlines() if 'C13_PHYSICAL_STAGE' in l and 'step=13 ' not in l and 'step=16 ' not in l),'take':bool(re.search('C13_PHYSICAL_MOVE take=1',text)),'put':bool(re.search('C13_PHYSICAL_MOVE take=0',text)),'closed_rejection':'C13_PHYSICAL_CLOSED_REJECT pass=1' in text,'drink_eat':'type=Water consume=1' in text and 'type=Food consume=1' in text}
 result['checks'].update({'put_preserves_id':bool(re.search('C13_PHYSICAL_MOVE take=0 slot=6 id=C1300022000000000000000000000001 revision=2',text)),'competing_request_rejected':'C13_PHYSICAL_REJECT slot=6 revision=0' in text,'remote_actions_visible':any('C13_OBSERVED_ACTION' in l for l in markers.get('client',[])),'circulation':'C13_REFERENCE_CIRCULATION clear=9 total=9' in text,'final_empty':'contents=0 revision=4' in text})
 expected={(2,0),(1,1),(2,2),(1,3),(0,4)}
 result['checks']['snapshots_agree']=all(expected.issubset({tuple(map(int,m)) for l in markers.get(role,[]) for m in re.findall(r'C13_PHYSICAL_SNAPSHOT count=(\d+) revision=(\d+)',l)}) for role in ('host','client'))
 result['passed']=all(result['checks'].values())
(R/f'logs/reference_{opt.mode}_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
