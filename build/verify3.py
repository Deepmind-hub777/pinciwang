import sys; sys.argv=['x']
exec(open('verify2.py').read().split("if __name__=='__main__':")[0])
import json, asyncio
OV=json.load(open('tts_override.json'))
L=json.load(open('levels_out.json'))
pairs=sorted({(a['c'],a['py'],a['au']) for l in L for a in l['a']})
items=[(c,py,'../audio/zi/'+au+'.mp3') for c,py,au in pairs if len(het(c))>1 and c not in OV]
items=[('行','xíng','/tmp/ref/sample_行.mp3'),('长','cháng','/tmp/ref/sample_长.mp3'),('着','zhe','/tmp/ref/sample_着.mp3')]+items
def refs_for(c):
    R={}
    for r in het(c):
        cand=[v for v in VOC if v!=c and d(v)==r and len(het(v))==1] or [v for v in VOC if v!=c and d(v)==r]
        cand=[v for v in cand if v not in OV]  # avoid chars we know are ambiguous
        if cand: R[r]=cand[0]
    return R
async def run():
    out=[]
    for c,py,p in items:
        R=refs_for(c)
        if len(R)<2 or py not in R: print('NOREF',c,py,R); out.append((c,py,None,R)); continue
        for v in R.values(): await syn(v,'/tmp/ref/%s.mp3'%v)
        fc=feat(p); sc={r:dist(fc,feat('/tmp/ref/%s.mp3'%v)) for r,v in R.items()}
        best=min(sc,key=sc.get); srt=sorted(sc.values()); margin=srt[1]-srt[0]
        print('OK ' if best==py else 'BAD',c,py,'best',best,{r:(R[r],round(s,2)) for r,s in sc.items()},'margin %.2f'%margin,flush=True)
        out.append((c,py,best,{r:(R[r],round(s,2)) for r,s in sc.items()}))
    json.dump(out,open('verify3.json','w'),ensure_ascii=False)
asyncio.run(run())
