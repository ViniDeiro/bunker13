"""Render the scripted board gesture using the same update path as manual input."""
import json, os, re, shutil, subprocess, time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ue = Path(os.environ.get('C13_UNREAL_ROOT', '/Users/Shared/Epic Games/UE_5.8'))
exe = ue / 'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
log = root/'logs/bedroom_drawing_game.log'
started = time.time()
with log.open('w') as output:
    run = subprocess.run([str(exe), str(root/'unreal/Condominio13/Condominio13.uproject'),
        '/Game/Bunker/BedroomVisual/Lvl_Bedroom_Study_Rest_Visual',
        '-game','-C13DoorVisual','-C13DrawingTest','-C13RoundTest','-windowed',
        '-ResX=960','-ResY=540','-ForceRes','-stdout','-FullStdOutLogOutput',
        '-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 85,r.ShadowQuality 2,r.Shadow.MaxResolution 512,r.AmbientOcclusionLevels 1'],
        stdout=output,stderr=subprocess.STDOUT,timeout=360)
data = log.read_text(errors='replace')
shot = next((p for p in (root/'unreal/Condominio13/Saved/Screenshots').glob('*/bedroom_board_game.png') if p.stat().st_mtime>=started),None)
dest=root/'screenshots/bedroom_visual'
dest.mkdir(exist_ok=True)
if shot:shutil.copy2(shot,dest/'drawing.png')
checks = dict(exit_clean=run.returncode==0,pickup='C13_DRAW_PICKUP pass=1' in data,
    trace_and_release='C13_DRAW_TRACE pass=1' in data,
    return_and_clear='C13_DRAW_RETURN pass=1 cleared=1' in data, screenshot=bool(shot),
    no_campaign_save='C13_SAVE_COMMIT' not in data)
fps=re.search(r'C13_DRAW_RETURN .*fps=([\d.]+) p95_ms=([\d.]+) samples=(\d+)',data)
result=dict(passed=all(checks.values()),checks=checks,
    fps=dict(mean=float(fps[1]),p95_ms=float(fps[2]),samples=int(fps[3])) if fps else None)
(root/'logs/bedroom_drawing_result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['passed'] else 1)
