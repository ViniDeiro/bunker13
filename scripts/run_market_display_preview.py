"""Validate the original water GUID through real E input and capture the new HUD."""
import os, shutil, subprocess, time
from pathlib import Path

r=Path(__file__).resolve().parents[1]
ue=Path(os.environ.get('C13_UNREAL_ROOT','/Users/Shared/Epic Games/UE_5.8'))
exe=ue/'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
log=r/'logs/market_display_preview.log'
start=time.time()
with log.open('w') as out:
    p=subprocess.run([str(exe),str(r/'unreal/Condominio13/Condominio13.uproject'),
        '/Game/Bunker/Lvl_CollectionRound','-game','-C13Round','-C13Expedition','-C13PlaytestNoSave',
        '-C13RoundTest','-C13MarketDisplayTest','-windowed','-ResX=960','-ResY=540','-ForceRes',
        '-stdout','-FullStdOutLogOutput',
        '-ExecCmds=t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 70,r.ShadowQuality 0,r.AmbientOcclusionLevels 0'],
        stdout=out,stderr=subprocess.STDOUT,timeout=180)
s=log.read_text(errors='replace')
shot=next(p for p in (r/'unreal/Condominio13/Saved/Screenshots').glob('*/market_display_hud.png') if p.stat().st_mtime>=start)
shutil.copy2(shot,r/'screenshots/market_display_hud.png')
assert p.returncode==0 and 'C13_MARKET_STOCK pass=1 count=12' in s and 'C13_MARKET_PICKUP pass=1' in s and 'C13_SAVE_COMMIT' not in s
print('C13_MARKET_HUD_VALIDATED')
