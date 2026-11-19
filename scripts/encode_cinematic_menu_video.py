"""Encode actual timestamped Unreal frames, without synthetic background or interpolated motion."""
from pathlib import Path
import json,re,subprocess
r=Path(__file__).resolve().parents[1]
s=(r/'logs/cinematic_1280x720_video.log').read_text(errors='replace')
frames=[(float(t),r/'output/cinematic_frames'/n) for t,n in re.findall(r'C13_MENU_FRAME time=([\d.]+) file=(cinematic_video_\d+\.png)',s)]
assert len(frames)>20 and all(p.exists() for t,p in frames)
rows=['ffconcat version 1.0']
for i,(t,p) in enumerate(frames):
 rows+=["file '"+str(p)+"'",'duration '+str(frames[i+1][0]-t if i+1<len(frames) else .125)]
rows+=["file '"+str(frames[-1][1])+"'"]
manifest=r/'output/cinematic_menu.ffconcat';manifest.write_text(chr(10).join(rows)+chr(10))
dest=r/'output/Condominio13_Menu_Cinematico.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-safe','0','-f','concat','-i',str(manifest),
 '-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-fps_mode','vfr','-movflags','+faststart',str(dest)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(dest)]))
result=dict(file=str(dest),real_frames=len(frames),duration=float(probe['format']['duration']),audio=False,
 scope='Timestamped native screenshots requested at 8 fps. Silent demonstration; recording overhead is separate from game FPS.')
(r/'logs/cinematic_video.json').write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps(result,indent=2))
