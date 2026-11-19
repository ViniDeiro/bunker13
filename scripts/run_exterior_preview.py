"""Render the exterior and exercise R and the no-save playtest contract."""
import os, shutil, subprocess, time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ue = Path(os.environ.get('C13_UNREAL_ROOT', '/Users/Shared/Epic Games/UE_5.8'))
exe = ue/'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
log = root/'logs/exterior_preview_game.log'
start = time.time()
with log.open('w') as out:
    run = subprocess.run([str(exe),str(root/'unreal/Condominio13/Condominio13.uproject'),
        '/Game/Bunker/Lvl_CollectionRound','-game','-C13Round','-C13Expedition',
        '-C13PlaytestNoSave','-C13RoundTest','-C13ExteriorPreviewTest',
        '-windowed','-ResX=960','-ResY=540','-ForceRes','-stdout','-FullStdOutLogOutput',
        '-ExecCmds=t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 70,r.ShadowQuality 0,r.AmbientOcclusionLevels 0'],
        stdout=out,stderr=subprocess.STDOUT,timeout=180)
s=log.read_text(errors='replace')
assert run.returncode==0 and 'C13_EXTERIOR_PREVIEW_START pass=1' in s and 'C13_SUPPLY_ROUTE_DRESSED bays=3' in s
assert 'C13_SAVE_COMMIT' not in s
assert 'C13_EXTERIOR_MARKET_DRESSED portal=1 stalls=4 divider=1' in s
shot=next(p for p in (root/'unreal/Condominio13/Saved/Screenshots').glob('*/exterior_polish_overview.png') if p.stat().st_mtime>=start)
dest=root/'screenshots/exterior_polish'
dest.mkdir(exist_ok=True)
shutil.copy2(shot,dest/'parking.png')
market=next(p for p in (root/'unreal/Condominio13/Saved/Screenshots').glob('*/exterior_polish_market.png') if p.stat().st_mtime>=start)
shutil.copy2(market,dest/'market.png')
print('C13_EXTERIOR_PREVIEW_VALIDATED')
