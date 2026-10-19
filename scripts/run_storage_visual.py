from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1];exe=ROOT/'builds/Mac/Condominio13-VerticalSlice.app/Contents/MacOS/Condominio13'
with (ROOT/'logs/storage_visual.log').open('w') as out:
 p=subprocess.Popen([str(exe),'-C13StorageVisual','-windowed','-ResX=1280','-ResY=720','-ForceRes','-stdout','-FullStdOutLogOutput'],stdout=out,stderr=subprocess.STDOUT)
 try:p.wait(timeout=35)
 except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=8)
log=(ROOT/'logs/storage_visual.log').read_text(errors='replace');moves=[l for l in log.splitlines() if 'C13_STORAGE_MOVE' in l]
result={'passed':'C13_STORAGE_VISUAL_AUDIT PASS' in log and len(moves)==2,'packaged_game':True,'moves':moves,'markers':[l for l in log.splitlines() if 'C13_STORAGE' in l]}
(ROOT/'logs/storage_visual_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
