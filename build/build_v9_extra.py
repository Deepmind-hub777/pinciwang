"""v9：每个母字的「额外字」候选 → extra_v9.json {母字: {字: [[score,[笔画]],...]}}（可断点续跑）"""
import json,re,glob,os
from multiprocessing import Pool
import gen
from v9lib import extra_match
F=json.load(open('charfreq.json'))
VOC={c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip()}
XV=sorted(c for c in VOC if c in gen.G and F.get(c,0)>=3000 and c not in '亠夂')
def load(pat):
    L=[]
    for f in sorted(glob.glob(pat)): L+=json.loads(re.search(r',(\[.*\])\);',open(f).read(),re.S).group(1))
    return L
def seg(M):
    r={}
    for T in XV:
        if T!=M:
            m=extra_match(T,M)
            if m: r[T]=[list(x) for x in m[:4]]
    return M,r
if __name__=='__main__':
    main=load('/workspace/pinciwang/data/main-*.js'); qz=load('/workspace/hanzi-xueyuan/modules/pinci/data/qz-*.js')
    order=[]; 
    for L in [main[9],main[12],main[16]]+main+qz:
        for c in L['ch']:
            if c['c'] in gen.G and c['c'] not in order: order.append(c['c'])
    out=json.load(open('extra_v9.json')) if os.path.exists('extra_v9.json') else {}
    todo=[s for s in order if s not in out]
    print('segments',len(order),'todo',len(todo),'vocab',len(XV),flush=True)
    with Pool(8) as p:
        for k,(M,r) in enumerate(p.imap(seg,todo,chunksize=1)):
            out[M]=r
            if k%25==0:
                print(k,flush=True); json.dump(out,open('extra_v9.json.tmp','w'),ensure_ascii=False); os.replace('extra_v9.json.tmp','extra_v9.json')
    json.dump(out,open('extra_v9.json','w'),ensure_ascii=False); print('done',len(out),flush=True)
