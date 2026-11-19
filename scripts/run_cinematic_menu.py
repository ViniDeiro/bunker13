"""Rendered menu capture, UMG delegate test and actual map transition."""
import argparse,os,subprocess,time,re,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--resolution',default='1280x720');p.add_argument('--video',action='store_true');p.add_argument('--quit',action='store_true');a=p.parse_args()
R=Path(__file__).resolve().parents[1];W,H=a.resolution.split('x');tag=a.resolution+('_video' if a.video else '')+('_quit' if a.quit else '')
env=dict(os.environ,DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer',TOOLCHAINS='com.apple.dt.toolchain.Metal.32023.883')
exe=Path('/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor')
log=R/f'logs/cinematic_{tag}.log';start=time.time()
args=[str(exe),str(R/'unreal/Condominio13/Condominio13.uproject'),'/Game/Bunker/MainMenu/L_MainMenu',
 '-game','-C13Round','-C13Expedition','-C13PlaytestNoSave','-C13RoundTest','-C13CinematicTest','-windowed',f'-ResX={W}',f'-ResY={H}','-ForceRes',
 '-stdout','-FullStdOutLogOutput','-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 85,r.ShadowQuality 2,r.Shadow.MaxResolution 512,r.AmbientOcclusionLevels 1']
if a.video:args+=['-C13CinematicVideo']
if a.quit:args+=['-C13CinematicQuitTest']
with log.open('w') as out:
 run=subprocess.run(args,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=360)
s=log.read_text(errors='replace');dest=R/'screenshots/cinematic_menu';dest.mkdir(exist_ok=True)
shot=next((p for p in (R/'unreal/Condominio13/Saved/Screenshots').glob('*/cinematic_menu.png') if p.stat().st_mtime>=start),None)
if shot:shutil.copy2(shot,dest/(tag+'.png'))
checks=dict(clean_exit=run.returncode==0,screenshot=bool(shot),accessibility='C13_MENU_ACCESSIBILITY pass=1' in s,
 entrance='C13_MENU_ENTRANCE_BEGIN' in s,travel='C13_MENU_TRAVEL' in s,match='C13_MENU_MATCH_LOADED pass=1' in s,no_campaign_save='C13_SAVE_COMMIT' not in s)
if a.quit:
 checks={k:checks[k] for k in ('clean_exit','screenshot','no_campaign_save')}
 checks['quit_action']='C13_MENU_QUIT_REQUEST pass=1' in s
else:
 checks['parallax']='C13_MENU_PARALLAX pass=1' in s
 checks['disabled_actions']='C13_MENU_DISABLED pass=1' in s
fps=re.search(r'C13_MENU_FPS mean=([\d.]+) p95_ms=([\d.]+) samples=(\d+)',s)
result=dict(passed=all(checks.values()),checks=checks,resolution=a.resolution,video=a.video,
 fps=dict(mean=float(fps[1]),p95_ms=float(fps[2]),samples=int(fps[3])) if fps else None)
(R/f'logs/cinematic_{tag}.json').write_text(json.dumps(result,indent=2)+'\n')
if a.video:
 frames=R/'output/cinematic_frames';frames.mkdir(exist_ok=True)
 for f in (R/'unreal/Condominio13/Saved/Screenshots').glob('*/cinematic_video_*.png'):
  if f.stat().st_mtime>=start:shutil.copy2(f,frames/f.name)
print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
