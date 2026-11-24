"""v10：在 v9 额外字上，并入 (1) 宽松匹配（≤7 画常用字，允许出头/比例略有出入）(2) IDS 部件（雷里的雨、需里的雨……）(3) 雨字头里的「丁」。去掉黑名单（单→手）。→ extra_v10.json"""
import json,os
from multiprocessing import Pool
import gen
from ids import desc
from v10lib import loose_match
from build_v9_extra import XV, load
SM=[c for c in XV if len(gen.G[c]['strokes'])<=7]
XS=set(XV)
BL={('单','手')}
def seg(M):
    r={}
    for T in SM:
        if T!=M:
            m=loose_match(T,M)
            if m: r[T]=[[x[0],x[1]] for x in m[:3]]
    return M,r
if __name__=='__main__':
    main=load('/workspace/pinciwang/data/main-*.js'); qz=load('/workspace/hanzi-xueyuan/modules/pinci/data/qz-*.js')
    order=[]
    for L in main+qz:
        for c in L['ch']:
            if c['c'] in gen.G and c['c'] not in order: order.append(c['c'])
    EX=json.load(open('extra_v9.json'))
    LO=json.load(open('loose_v10.json')) if os.path.exists('loose_v10.json') else {}
    todo=[s for s in order if s not in LO]; print('todo',len(todo),flush=True)
    with Pool(8) as p:
        for k,(M,r) in enumerate(p.imap(seg,todo,chunksize=2)):
            LO[M]=r
            if k%100==0: print(k,flush=True); json.dump(LO,open('loose_v10.json','w'),ensure_ascii=False)
    json.dump(LO,open('loose_v10.json','w'),ensure_ascii=False)
    out={}; st={'v9':0,'loose':0,'ids':0,'ding':0}
    for M in order:
        R={T:[list(x) for x in v] for T,v in (EX.get(M) or {}).items()}; st['v9']+=len(R)
        def add(T,sc,k,tag):
            if (M,T) in BL or T==M: return
            if T not in R: st[tag]+=1
            L=R.setdefault(T,[])
            if not any(sorted(k)==sorted(x[1]) for x in L): L.append([sc,k])
        mt=(gen.D.get(M) or {}).get('matches') or []
        grp=lambda i: (mt[i][0] if i<len(mt) and mt[i] else None)
        for T,v in (LO.get(M) or {}).items():
            for sc,k in v:
                if len({grp(i) for i in k})>1: continue   # 宽松匹配不得跨部件（避免「件」在「解」里这种拼凑）
                if len(k)>=5 and sc>=0.09: continue
                if T in '手卡': continue
                add(T,sc,k,'loose')
        for T,S in desc(M):
            if T in XS and len(S)>=2: add(T,0.01,list(S),'ids')
            if T=='雨': add('丁',0.02,[S[0],S[3]],'ding'); add('丁',0.03,[S[0],S[2]],'ding')
        if M=='雨': add('丁',0.02,[0,3],'ding'); add('丁',0.03,[0,2],'ding')
        for T in list(R):
            if (M,T) in BL: R.pop(T)
            else: R[T].sort()
        out[M]=R
    json.dump(out,open('extra_v10.json','w'),ensure_ascii=False); print('done',len(out),st)
