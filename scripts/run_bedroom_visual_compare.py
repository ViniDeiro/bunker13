"""Capture the reference and isolated grade with the same rendered functional probe."""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ue = Path(os.environ.get('C13_UNREAL_ROOT', '/Users/Shared/Epic Games/UE_5.8'))
exe = ue / 'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
dest = root / 'screenshots/bedroom_visual'
dest.mkdir(exist_ok=True)
results_path = root/'logs/bedroom_visual_comparison.json'
results = json.loads(results_path.read_text()) if len(sys.argv)>1 and results_path.exists() else {}
for name, level in [('before','BedroomRest/Lvl_Bedroom_Study_Rest'),
                    ('after','BedroomVisual/Lvl_Bedroom_Study_Rest_Visual'),
                    ('bed02','BedroomVisual/Lvl_Bedroom_Study_Rest_Visual')]:
    if len(sys.argv)>1 and name not in sys.argv[1:]:continue
    log_path = root / f'logs/bedroom_visual_{name}.log'
    start = time.time()
    with log_path.open('w') as out:
        run = subprocess.run([str(exe), str(root/'unreal/Condominio13/Condominio13.uproject'),
            '/Game/Bunker/'+level, '-game','-C13DoorVisual','-C13RoomStudyTest','-C13RoundTest',
            '-windowed','-ResX=960','-ResY=540','-ForceRes','-stdout','-FullStdOutLogOutput',
            '-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 85,r.ShadowQuality 2,r.Shadow.MaxResolution 512,r.AmbientOcclusionLevels 1']
            + (['-C13RoomStudyBed02'] if name=='bed02' else []),
            stdout=out, stderr=subprocess.STDOUT, timeout=420)
    log = log_path.read_text(errors='replace')
    fps = re.search(r'C13_BEDROOM_FPS samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)',log)
    checks = {k:k+' pass=1' in log for k in ('C13_BEDROOM_REST','C13_BEDROOM_RELEASE','C13_BEDROOM_WALK','C13_BEDROOM_REST_CAMERA','C13_BEDROOM_CAMERA_BLEND')}
    for shot in ('overview','rest'):
        images = [p for p in (root/'unreal/Condominio13/Saved/Screenshots').glob(f'*/bedroom_unreal_{shot}.png') if p.stat().st_mtime>=start]
        if images:shutil.copy2(images[0],dest/f'{name}_{shot}.png')
        checks[shot]=bool(images)
    checks.update(clean_exit=run.returncode==0,no_campaign_save='C13_SAVE_COMMIT' not in log,fps=bool(fps))
    results[name]={'passed':all(checks.values()),'checks':checks,'fps':dict(samples=int(fps[1]),mean=float(fps[2]),p95_ms=float(fps[3])) if fps else None}
print(json.dumps(results,indent=2))
(root/'logs/bedroom_visual_comparison.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(row['passed'] for row in results.values()) else 1)
