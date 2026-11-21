import json, os, sys, subprocess, numpy as np
def dec(f):
    b=subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    return np.frombuffer(b,np.float32)
from faster_whisper import WhisperModel
from pypinyin import pinyin, Style
L=json.load(open('levels_out.json'))
pairs=sorted({(a['c'],a['py'],a['au']) for l in L for a in l['a']})
m=WhisperModel(sys.argv[1] if len(sys.argv)>1 else "small",device="cpu",compute_type="int8")
res=[]
for c,py,au in pairs:
    segs,_=m.transcribe(dec('../audio/zi/'+au+'.mp3'),language="zh",beam_size=5,initial_prompt="单字朗读：")
    t=''.join(s.text for s in segs).strip()
    hz=[ch for ch in t if '\u4e00'<=ch<='\u9fff']
    reads=set()
    for ch in hz[:1]:
        reads|=set(pinyin(ch,style=Style.TONE,heteronym=True)[0])
    ok = py in reads
    toneless_ok = any(pinyin(ch,style=Style.NORMAL)[0][0]==pinyin(c,style=Style.NORMAL)[0][0] for ch in hz[:1])
    res.append((c,py,t,ok))
    if not ok: print('CHECK',c,py,'->',repr(t),flush=True)
print('ok',sum(r[3] for r in res),'/',len(res))
json.dump(res,open('verify.json','w'),ensure_ascii=False)
