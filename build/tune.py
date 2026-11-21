import json,numpy as np,gen
L=json.load(open('/workspace/ref/levels.json'))
gen.VOC_SET=set(gen.VOC)
def dist2(PT,PM):
    a,ea=gen.norm(PT); b,eb=gen.norm(PM)
    ps=np.sqrt(((a-b)**2).sum(-1)).mean(-1)
    return ps.mean(), ps.max(), (ea[0]/ea[1])/(eb[0]/eb[1])
import random; random.seed(1)
sample=random.sample(L,50)
rows=[]
for lv in sample:
    M=lv['m']
    if M not in gen.G: continue
    ans={a['c'] for a in lv['a']}
    for T in gen.VOC:
        if T==M or len(gen.G[T]['medians'])>=len(gen.G[M]['medians']): continue
        r=gen.match(T,M,thr=0.16)
        if not r: continue
        PT=gen.prep(T)[0]; PM=gen.prep(M)[0]
        best=min((dist2(PT,PM[c]) for _,c in r), key=lambda x:x[0]+0.5*x[1])
        rows.append((T in ans, best[0], best[1], M, T))
for lv in sample:
    pass
refans=sum(len([a for a in lv['a'] if a['c'] in gen.VOC_SET]) for lv in sample)
print('ref answers in vocab',refans)
for t1 in [0.08,0.1,0.12,0.14]:
  for t2 in [0.15,0.2,0.25,0.3]:
    sel=[r for r in rows if r[1]<t1 and r[2]<t2]
    tp=sum(r[0] for r in sel); print(t1,t2,'tp',tp,'extra',len(sel)-tp)
json.dump(rows,open('rows.json','w'),ensure_ascii=False)
