import json, numpy as np, gen
REAL=json.load(open('real_levels.json'))
def solve(M):
    return gen.solve2(M,0.056,0.12)
levels=[]
plan=[(1,'大'),(2,'王')]+[(n,c) for n,c in REAL if 3<=n<=130]
cache={}
for n,t in plan:
    chars=[c for c in t]
    if not all(c in gen.G for c in chars): print('skip',n,t); continue
    off=0; amap={}; ch=[]
    for c in chars:
        g=gen.G[c]
        if c not in cache: cache[c]=solve(c)
        for sc,T,ks in cache[c]:
            ks=[[i+off for i in k] for k in ks]
            if T in amap: amap[T]['k']+=ks; amap[T]['sc']=min(amap[T]['sc'],sc)
            else: amap[T]={'c':T,'k':ks,'sc':sc}
        N=len(g['strokes'])
        whole=list(range(off,off+N))
        if c in amap: amap[c]['k'].insert(0,whole); amap[c]['sc']=0
        else: amap[c]={'c':c,'k':[whole],'sc':0}
        ch.append({'c':c,'st':g['strokes']}); off+=N
    A=list(amap.values())
    mains=[a for a in A if a['sc']==0]; rest=sorted([a for a in A if a['sc']>0],key=lambda a:a['sc'])
    cap=max(4,min(20,6+n//6))
    rest=rest[:cap-len(mains)]
    A=rest+mains
    sc_of=lambda a: len(gen.G[a['c']]['medians'])
    A.sort(key=lambda a:(a['sc']==0, sc_of(a)))
    for a in A:
        a['py']=(gen.D.get(a['c'],{}).get('pinyin') or [''])[0]
        a['k']=a['k'][:8]; a.pop('sc')
    levels.append({'n':len(levels)+1,'t':t,'ch':ch,'a':A})
    print(len(levels),t,' '.join(a['c'] for a in A))
json.dump(levels,open('levels_out.json','w'),ensure_ascii=False,separators=(',',':'))
