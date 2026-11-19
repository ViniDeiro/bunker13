"""Rendered Unreal study validation in an isolated map, no campaign saves."""
from pathlib import Path
import json,os,re,subprocess,time,shutil
R=Path(__file__).resolve().parents[1];(R/'logs').mkdir(exist_ok=True)
exe=Path(os.environ.get('C13_UNREAL_ROOT','/Users/Shared/Epic Games/UE_5.8'))/'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
start=time.time()
env=os.environ.copy()
env.setdefault('DEVELOPER_DIR','/Applications/Xcode.app/Contents/Developer')
env.setdefault('TOOLCHAINS','com.apple.dt.toolchain.Metal.32023.883')
with (R/'logs/bedroom_game.log').open('w') as out:
 p=subprocess.Popen([str(exe),str(R/'unreal/Condominio13/Condominio13.uproject'),'/Game/Bunker/BedroomStudy/Lvl_Bedroom_Study','-game','-C13DoorVisual','-C13RoomStudyTest','-windowed','-ResX=1280','-ResY=720','-ForceRes','-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 45,r.ScreenPercentage 100,r.ShadowQuality 2,r.Shadow.MaxResolution 512,r.AmbientOcclusionLevels 1','-abslog='+str(R/'logs/bedroom_game_native.log'),'-stdout','-FullStdOutLogOutput'],stdout=out,stderr=subprocess.STDOUT,env=env)
 try:code=p.wait(timeout=420)
 except subprocess.TimeoutExpired:
  p.terminate();p.wait(timeout=10);code=-1
log=(R/'logs/bedroom_game_native.log').read_text(errors='replace') if (R/'logs/bedroom_game_native.log').is_file() else (R/'logs/bedroom_game.log').read_text(errors='replace')
source=R/'unreal/Condominio13/Saved/Screenshots/MacEditor'
copied=[]
for folder in (source,R/'unreal/Condominio13/Saved/Screenshots/Mac'):
 for image in folder.glob('bedroom_unreal_*.png'):
  if image.stat().st_mtime>=start:shutil.copy2(image,R/'screenshots'/image.name);copied.append(image.name)
checks={'exit_clean':code==0,'rest_raises_energy':'C13_BEDROOM_REST pass=1' in log,'leave_releases_bed':'C13_BEDROOM_RELEASE pass=1' in log,'walk':'C13_BEDROOM_WALK pass=1' in log,'no_campaign_commit':'C13_SAVE_COMMIT' not in log,'overview_image':'bedroom_unreal_overview.png' in copied}
fps=re.search(r'C13_BEDROOM_FPS samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',log)
checks['rest_camera_position']='C13_BEDROOM_REST_CAMERA pass=1' in log
checks['camera_blends_instead_of_snapping']='C13_BEDROOM_CAMERA_BLEND pass=1' in log
checks['fps_recorded']=fps is not None
result={'passed':all(checks.values()),'checks':checks,'fps':{'samples':int(fps[1]),'mean':float(fps[2]),'p95_ms':float(fps[3])} if fps else None,'resolution':'1280x720','study_quality':{'screen_percentage':100,'shadow_quality':2,'shadow_resolution':512,'ao_levels':1,'fps_cap':45},'scope':'One rendered Unreal Editor game process, automated fixture, 20s window including captures; not packaged multiplayer or human playtest.'}
(R/'logs/bedroom_game_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
