"""Exercise actual I/U/E bindings and server transactions in the packaged game."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
exe=ROOT/'builds/Mac/Condominio13-VerticalSlice.app/Contents/MacOS/Condominio13'
log=ROOT/'logs/hands_visual.log'
with log.open('w') as out:
 child=subprocess.Popen([str(exe),'-windowed','-ResX=1280','-ResY=720','-ForceRes','-C13HandsVisual','-stdout','-FullStdOutLogOutput'],stdout=out,stderr=subprocess.STDOUT)
 try:child.wait(timeout=40)
 except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=8)
text=log.read_text(errors='replace');lines=[line for line in text.splitlines() if any(mark in line for mark in ('C13_HAND','C13_CONSUME','C13_PICKUP'))]
actions=[line for line in lines if 'C13_HAND_ACTION' in line]
frames=[line for line in lines if 'C13_HAND_FRAME' in line]
passed='C13_HANDS_AUDIT PASS' in text and len(actions)==4 and len(frames)==5 and all('playing=1' in x for x in frames) and all('hands=1 local=1' in x for x in actions)
passed=passed and all(any(f'type={kind} consume=1' in x for x in actions) for kind in ('Water','Food','Medkit')) and any('consume=0' in x for x in actions)
result={'passed':passed,'packaged_game':True,'actions':len(actions),'frames':len(frames),'checks':['Real I/U/E input bindings','Three consumptions plus one pickup','Repeated used GUID does not replay an action or change stats','Inventory closes and look is released','Two glove meshes loaded for each action'],'markers':lines,'limits':['Development-only fixture; not a human playtest or third-person animation validation.','Server applies the accepted consumable at action start; visual interruption does not refund it.']}
(ROOT/'logs/hands_playtest_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if passed else 1)
