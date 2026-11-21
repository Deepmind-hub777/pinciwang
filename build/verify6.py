import sys; sys.argv=['x']
exec(open('verify2.py').read().split("if __name__=='__main__':")[0])
import json, asyncio, hashlib
OV=json.load(open('tts_override.json'))
L=json.load(open('main_levels.json'))
OLD=json.load(open('verify4.json'))
pairs=sorted({(a['c'],a['py']) for l in L for a in l['a'] if a['c'] not in OLD})
ALL=[c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip()]+[c.strip() for c in open('level-2.txt',encoding='utf8') if c.strip()]
def rp(t): return '/tmp/ref/%s.mp3'%t
def homs(py,excl):
    a=[v for v in ALL if v not in excl and d(v)==py]
    return sorted(a,key=lambda v:(len(het(v))>1, ALL.index(v)))
FC={}
def F(t):
    if t not in FC: FC[t]=feat(rp(t))
    return FC[t]
async def synall(texts):
    sem=asyncio.Semaphore(8)
    async def one(t):
        async with sem: await syn(t,rp(t))
    await asyncio.gather(*[one(t) for t in set(texts)])
TH=0.6
async def run():
    plan={}
    for c,py in pairs:
        T=OV.get(c,c); refs=homs(py,{c,T})[:3]
        plan[(c,py)]=(T,refs)
    await synall([t for T,refs in plan.values() for t in [T]+refs])
    res={}; newOV={}; unsure=[]
    for (c,py),(T,refs) in plan.items():
        ds=[dist(F(T),F(r)) for r in refs]
        if ds and min(ds)<TH: res[c]=('ok',T,refs[ds.index(min(ds))],round(min(ds),2)); 
        else:
            # try other homophone texts
            cands=[c]+homs(py,{c})[:8]
            await synall(cands+homs(py,set())[:10])
            found=None
            for S in cands:
                others=[r for r in homs(py,{S})[:10]]
                dd=[dist(F(S),F(r)) for r in others]
                if dd and min(dd)<TH: found=(S,others[dd.index(min(dd))],min(dd)); break
            if found:
                res[c]=('fixed',found[0],found[1],round(found[2],2))
            else:
                res[c]=('unsure',T,refs,[round(x,2) for x in ds]); unsure.append((c,py))
        if res[c][0]!='ok': print(c,py,res[c],flush=True)
        if res[c][0] in('ok','fixed') and res[c][1]!=c: newOV[c]=res[c][1]
    print('ok',sum(1 for v in res.values() if v[0]=='ok'),'fixed',sum(1 for v in res.values() if v[0]=='fixed'),'unsure',unsure)
    json.dump(newOV,open('tts_override_new2.json','w'),ensure_ascii=False)
    json.dump({k:list(map(str,v)) for k,v in res.items()},open('verify6.json','w'),ensure_ascii=False,indent=0)
asyncio.run(run())
