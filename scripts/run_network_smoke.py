"""Four real game processes; test view setup is Development-only, transactions use owner RPCs."""
from pathlib import Path
import subprocess,time,json,argparse
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--editor',action='store_true');p.add_argument('--remote-only',action='store_true');p.add_argument('--tag',default='network');args=p.parse_args()
exe=Path('/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor') if args.editor else ROOT/'builds/Mac/Condominio13-VerticalSlice.app/Contents/MacOS/Condominio13'
base=[str(exe)]
if args.editor: base += [str(ROOT/'unreal/Condominio13/Condominio13.uproject')]
common=['-game','-nullrhi','-nosound','-unattended','-nosplash','-C13NetTest','-stdout','-FullStdOutLogOutput','-NoSteam','-LogCmds=LogTemp Verbose']
processes=[];files=[]
try:
    for i in range(4):
        dest='/Game/Bunker/Lvl_Bunker?listen' if i==0 else '127.0.0.1:7787'
        f=(ROOT/f'logs/{args.tag}_{i}.log').open('w');files.append(f)
        processes.append(subprocess.Popen(base+[dest,'-port=7787']+common+(['-C13RemoteOnly'] if i==0 and args.remote_only else []),stdout=f,stderr=subprocess.STDOUT))
        time.sleep(3 if i==0 else 1)
    deadline=time.monotonic()+65
    while time.monotonic()<deadline:
        host=(ROOT/f'logs/{args.tag}_0.log').read_text(errors='replace')
        if 'C13_NET_AUDIT' in host: break
        if all(x.poll() is not None for x in processes):break
        time.sleep(1)
finally:
    for child in processes:
        if child.poll() is None:child.terminate()
    for child in processes:
        try:child.wait(timeout=8)
        except subprocess.TimeoutExpired:child.kill();child.wait()
    for f in files:f.close()
logs=[(ROOT/f'logs/{args.tag}_{i}.log').read_text(errors='replace') for i in range(4)]
markers=[[line for line in log.splitlines() if any(s in line for s in ['C13_NET_AUDIT','C13_CLIENT_STATE','C13_PICKUP','C13_PROBE_SENT'])] for log in logs]
passed='C13_NET_AUDIT PASS' in logs[0] and all('C13_CLIENT_STATE pickupHidden=1 pickupCollision=0 bedOccupied=1' in log for log in logs)
if args.remote_only: passed = passed and any('C13_CLIENT_STATE pickupHidden=1 pickupCollision=0 bedOccupied=1 inventory=1' in log for log in logs[1:])
result={'passed':passed,'real_processes':len(processes),'players':4,'remote_only':args.remote_only,'editor':args.editor,'markers':markers,'limits':['Automated isolated transactions; not four-human playtest or a network endurance test.','Test-only RPC arranges views/positions; normal ServerInteract RPC performs transactions.']}
(ROOT/f'logs/{args.tag}_result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
raise SystemExit(0 if passed else 1)
