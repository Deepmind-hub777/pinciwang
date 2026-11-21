import json, asyncio, subprocess, os, numpy as np, librosa, edge_tts
from pypinyin import pinyin, Style
from tts import pinyin_to_num  # noqa
VOC=[c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip()]
d=lambda c: pinyin(c,style=Style.TONE)[0][0]
het=lambda c: pinyin(c,style=Style.TONE,heteronym=True)[0]
os.makedirs('/tmp/ref',exist_ok=True)
async def syn(text,path):
    for k in range(6):
        if os.path.exists(path) and os.path.getsize(path)>500: return
        try: await edge_tts.Communicate(text,"zh-CN-XiaoxiaoNeural",rate="-10%").save(path)
        except Exception: await asyncio.sleep(3)
def feat(path):
    y,sr=librosa.load(path,sr=16000)
    y,_=librosa.effects.trim(y,top_db=35)
    m=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=13,hop_length=160)[1:]
    f0,vf,_=librosa.pyin(y,fmin=80,fmax=500,sr=sr,hop_length=160)
    f0=np.where(np.isnan(f0),np.nanmedian(f0) if np.any(~np.isnan(f0)) else 200,f0)
    st=12*np.log2(f0/180.0)
    n=min(m.shape[1],len(st)); m=m[:,:n]; st=st[:n]
    m=(m-m.mean(1,keepdims=True))/ (m.std(1,keepdims=True)+1e-6)
    return np.vstack([m, np.tile(st*0.6,(4,1))])
def dist(a,b):
    D,wp=librosa.sequence.dtw(X=a,Y=b,metric='euclidean'); return D[-1,-1]/len(wp)
async def main(items):
    out=[]
    for c,py,path in items:
        refs={}
        for r in het(c):
            cand=[v for v in VOC if v!=c and d(v)==r and len(het(v))==1] or [v for v in VOC if v!=c and d(v)==r]
            if not cand: continue
            rp='/tmp/ref/%s.mp3'%cand[0]; await syn(cand[0],rp); refs[r]=(cand[0],rp)
        if py not in refs or len(refs)<2: out.append((c,py,'no-ref',refs and list(refs))); continue
        fc=feat(path)
        sc={r:dist(fc,feat(p)) for r,(v,p) in refs.items()}
        best=min(sc,key=sc.get)
        out.append((c,py,best,{r:(refs[r][0],round(s,2)) for r,s in sc.items()}))
        print(('OK ' if best==py else 'BAD'),c,py,'best=',best,out[-1][3],flush=True)
    return out
if __name__=='__main__':
    import sys
    L=json.load(open('levels_out.json'))
    pairs=sorted({(a['c'],a['py'],a['au']) for l in L for a in l['a']})
    items=[(c,py,'../audio/zi/'+au+'.mp3') for c,py,au in pairs if len(het(c))>1]
    # extra samples requested: 行 长 着 (not in game) + 乐
    async def extra():
        x=[]
        for c,py in [('行','xíng'),('长','cháng'),('着','zhe'),('乐','lè')]:
            p='/tmp/ref/sample_%s.mp3'%c; await syn(c,p); x.append((c,py,p))
        return x
    items=asyncio.run(extra())+items
    res=asyncio.run(main(items))
    json.dump(res,open('verify2.json','w'),ensure_ascii=False,indent=0)
    bad=[r for r in res if r[2]!=r[1]]
    print('total',len(res),'mismatch/no-ref',len(bad)); print(bad)
