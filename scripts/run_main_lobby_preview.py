"""Capture title screen, click its actual input-bound button, and verify match transition."""
import os, shutil, subprocess, time
from pathlib import Path

root=Path(__file__).resolve().parents[1]
ue=Path(os.environ.get('C13_UNREAL_ROOT','/Users/Shared/Epic Games/UE_5.8'))
exe=ue/'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
log=root/'logs/main_lobby_game.log'
start=time.time()
with log.open('w') as out:
    p=subprocess.run([str(exe),str(root/'unreal/Condominio13/Condominio13.uproject'),
        '/Game/Bunker/Lvl_CollectionRound','-game','-C13Round','-C13Expedition','-C13PlaytestNoSave',
        '-C13MainLobby','-C13RoundTest','-C13LobbyTest','-windowed','-ResX=960','-ResY=540','-ForceRes',
        '-stdout','-FullStdOutLogOutput',
        '-ExecCmds=t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 70,r.ShadowQuality 0,r.AmbientOcclusionLevels 0'],
        stdout=out,stderr=subprocess.STDOUT,timeout=180)
s=log.read_text(errors='replace')
shot=next(p for p in (root/'unreal/Condominio13/Saved/Screenshots').glob('*/main_lobby.png') if p.stat().st_mtime>=start)
shutil.copy2(shot,root/'screenshots/main_lobby.png')
assert p.returncode==0 and 'C13_LOBBY_BUTTON_AIM pass=1' in s and 'C13_LOBBY_ENTERED_MATCH pass=1' in s and 'C13_SAVE_COMMIT' not in s
print('C13_MAIN_LOBBY_VALIDATED')
