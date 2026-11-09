"""Encode native game screenshots at their recorded timestamps; do not infer game FPS from capture FPS."""
from pathlib import Path
import re,subprocess,json,shutil,wave,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'output/video';D.mkdir(parents=True,exist_ok=True);frames=R/'output/reference_video_frames';reports={};videos=[]
for role in ('host','client'):
 text=(R/f'logs/reference_video_{role}.log').read_text(errors='replace');entries=[(float(t),n) for t,n in re.findall(r'C13_VIDEO_FRAME time=([\d.]+) file=(refvideo_\w+_\d+\.png)',text)]
 assert len(entries)>100,(role,len(entries));timeline=frames/f'{role}_timeline.txt'
 rows=['ffconcat version 1.0']
 for i,(t,name) in enumerate(entries):
  f=frames/name;assert f.is_file(),f;rows.append(f"file '{f}'")
  if i<len(entries)-1:rows.append('duration %.6f'%(entries[i+1][0]-t))
 rows.append(f"file '{frames/entries[-1][1]}'");timeline.write_text('\n'.join(rows)+'\n')
 out=D/f'Condominio13_Armario_{role}.mp4'
 cmd=['/opt/homebrew/bin/ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(timeline)]
 audio=None
 if role=='host':
  src=Path('/Users/vini_deiro/Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/C13ReferenceAudio/refvideo_host.wav')
  if src.exists():
   audio=D/'Condominio13_Audio_Jogo.wav';shutil.copy2(src,audio)
   with wave.open(str(audio),'rb') as w:
    raw=w.readframes(w.getnframes());sw=w.getsampwidth();a=np.frombuffer(raw,dtype='<i2' if sw==2 else '<i4').astype(float)/(32768 if sw==2 else 2147483648);audio_report={'channels':w.getnchannels(),'rate':w.getframerate(),'duration_s':w.getnframes()/w.getframerate(),'rms':float(np.sqrt(np.mean(a*a))),'peak':float(np.max(np.abs(a)))}
   assert audio_report['peak']>.001,'Game audio recording is silent';reports['audio']=audio_report
   reports['audio']['limitation']='Partial audio-device recording; not synchronized to wall-clock video. Supplied separately, not muxed.';audio=None
 cmd+=['-vsync','vfr','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart']
 if audio:cmd+=['-c:a','aac','-b:a','160k']
 cmd+=[str(out)];subprocess.run(cmd,check=True);videos.append(out)
 reports[role]={'captured_frames':len(entries),'source_interval_s':entries[-1][0]-entries[0][0],'average_capture_fps':(len(entries)-1)/(entries[-1][0]-entries[0][0]),'video':str(out),'source':'Native Unreal FScreenshotRequest frames; variable intervals preserved'}
# Main deliverable keeps the operator's first-person view; companion file shows the remote observer.
shutil.copy2(videos[0],D/'Condominio13_Armario_Fisico.mp4')
for out in videos:
 r=subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(out)],check=True,capture_output=True,text=True);reports[out.name]=json.loads(r.stdout)
(R/'logs/reference_video_encoding.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
