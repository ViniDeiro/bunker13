"""Encode actual Unreal screenshots at their captured timestamps, with game audio only if its duration matches the capture."""
from pathlib import Path
import re,subprocess,json,wave,array
R=Path(__file__).resolve().parents[1];O=R/'output';O.mkdir(exist_ok=True)
log=(R/'logs/bedcab_recording_failure/bedcab_host_native.log').read_text(errors='replace');frames=[]
for t,n in re.findall(r'C13_BEDCAB_FRAME time=([\d.]+) file=(bedcab_video_\d+\.png)',log):
 p=O/'bedcab_frames'/n
 if p.exists():frames.append((float(t),p))
assert len(frames)>100,'Missing actual gameplay frames'
concat=O/'bedcab_capture.ffconcat';rows=['ffconcat version 1.0']
for i,(t,p) in enumerate(frames):
 rows.append("file '"+str(p)+"'");rows.append('duration '+str(frames[i+1][0]-t if i+1<len(frames) else .125))
rows.append("file '"+str(frames[-1][1])+"'");concat.write_text('\n'.join(rows)+'\n')
audio=R/'unreal/Condominio13/Saved/BedroomCabinetVideo/bedcab_audio.wav';assert audio.exists(),'Missing recorded game audio'
with wave.open(str(audio)) as w:
 duration=w.getnframes()/w.getframerate();width=w.getsampwidth();data=w.readframes(w.getnframes())
 peak=max(map(abs,array.array('h',data))) if width==2 else None
timeline_duration=frames[-1][0]-frames[0][0]+.125
audio_valid=abs(duration-timeline_duration)<1.0
video=O/'Condominio13_Armario_Interacoes.mp4'
args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-safe','0','-f','concat','-i',str(concat)]
if audio_valid:args+=['-i',str(audio)]
args+=['-c:v','libx264','-threads','2','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-fps_mode','vfr']
if audio_valid:args+=['-c:a','aac','-shortest']
args+=['-movflags','+faststart',str(video)]
subprocess.run(args,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
assert any(s['codec_type']=='video' for s in probe['streams'])
result={'file':str(video),'frames':len(frames),'duration_s':float(probe['format']['duration']),'audio_included':audio_valid,'audio_duration_s':duration,'audio_issue':None if audio_valid else 'Recorded audio is shorter than real capture timeline; omitted to avoid false synchronization.','pcm16_peak':peak,'bytes':video.stat().st_size,'connected_players':1,'scope':'Host-only demonstration from recording run where client failed before joining; not multiplayer proof.','capture':'Real gameplay sequence, requested 8 fps, variable captured timing; not a smooth 30/60 fps recording.'}
(R/'logs/bedroom_cabinet_video.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
