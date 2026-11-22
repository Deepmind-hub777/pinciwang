"""v4 答案重建：IDS 全后代 + 几何复核 + 笔形(钩/折)硬校验 + 同笔画集合唯一 + 按字分段"""
import json, sys
from multiprocessing import Pool
import gen
from v4lib import solve_v4, resolve, types, assign, check, GEO_THR, typeok_strict
from pyau import py_of, au_of
from outline import outline_ok
VOC=set(c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip())|set('杲')  # v4.1：主园只认一级常用字；乂/廿/弋/彡/幺/兀/亓/亍 等部件不算（偏旁部件归后花园）
VOC={c for c in VOC if c in gen.G}-set('亠夂')  # 亠/夂 是偏旁，不算主园常用字
GEO=json.load(open('more_cache.json'))['res']; GEO.update(json.load(open('miss_cache.json')))
COMP=json.load(open('comp_names.json'))
SKIP={('贏','赢'),('餃','饺')}  # 繁体母字里的简体本字：几乎用尽全部笔画，不算“字中字”
def seg_main(M): return M, solve_v4(M,VOC,GEO.get(M))
def bonus_geo(M):
    N=len(gen.G[M]['medians']); found=[]
    for T in COMP:
        if len(gen.G[T]['medians'])>=N: continue
        ks=[k for _,k in gen.match(T,M,thr=0.2,maxnodes=20000)]
        if ks: found.append((0,T,ks))
    return found
def seg_bonus(M): return M, solve_v4(M,set(COMP),bonus_geo(M),core=False)
def build(levels,segsol,garden,old_by_char):
    out=[]; allconf=[]
    for L in levels:
        off=0; ans={}
        for ch in L['ch']:
            M=ch['c']; N=len(ch['st'])
            for T,lst in segsol[M].items():
                if garden=='main' and T not in VOC: continue  # 分段缓存可能来自旧词表
                if (M,T) in SKIP: continue
                for c,s,src in lst:
                    if src!='ids' and not (outline_ok(T,M,list(c)) and typeok_strict(T,M,list(c))): continue
                    ans.setdefault(T,[]).append(([i+off for i in c],s,src))
            if garden=='main':
                ans.setdefault(M,[]).append((list(range(off,off+N)),-1,'self'))
            off+=N
        res,conf=resolve(ans)
        allconf+= [(L['n'],L['t'])+c for c in conf]
        A=[]
        for T,lst in res.items():
            lst.sort(key=lambda x:x[1])
            sc=min(x[1] for x in lst)
            ks=[sorted(x[0]) for x in lst]
            if garden=='main':
                o=old_by_char.get(T); py=o['py'] if o else py_of(T); au=o['au'] if o else au_of(T,py)
                A.append({'c':T,'k':ks,'py':py,'au':au,'_s':sc,'_self':T in [c['c'] for c in L['ch']]})
            else:
                A.append({'c':T,'k':ks,'nm':COMP[T],'py':(gen.D.get(T,{}).get('pinyin') or [''])[0],'au':'bu/%04x'%ord(T),'_s':sc,'_self':False})
        A.sort(key=lambda a:(a['_self'],len(gen.G[a['c']]['strokes']),a['_s']))
        for a in A: a.pop('_s'); a.pop('_self')
        out.append({'n':L['n'],'t':L['t'],'ch':L['ch'],'a':A})
    return out,allconf
if __name__=='__main__':
    main=json.load(open('main_levels_v3.json')); bon=json.load(open('bonus_levels_v3.json'))  # v3 关卡表（关号/母字/笔画/读音）作为输入
    old_by_char={}
    for L in main:
        for a in L['a']: old_by_char.setdefault(a['c'],a)
    segs=sorted({ch['c'] for L in main for ch in L['ch']})
    bsegs=sorted({ch['c'] for L in bon for ch in L['ch']})
    import os, pickle
    if os.path.exists('segcache_v4.pkl') and '--fresh' not in sys.argv:
        sm,sb=pickle.load(open('segcache_v4.pkl','rb'))
    else:
        with Pool(8) as p:
            sb=dict(p.map(seg_bonus,bsegs,chunksize=2))
            sm={}
            for r in p.imap_unordered(seg_main,segs,chunksize=4):
                sm[r[0]]=r[1]
                if len(sm)%100==0: print('seg',len(sm),flush=True)
        pickle.dump((sm,sb),open('segcache_v4.pkl','wb'))
    M2,cm=build(main,sm,'main',old_by_char); B2,cb=build(bon,sb,'bonus',{})
    json.dump(M2,open('main_levels_v4.json','w'),ensure_ascii=False,separators=(',',':'))
    json.dump(B2,open('bonus_levels_v4.json','w'),ensure_ascii=False,separators=(',',':'))
    json.dump({'main':cm,'bonus':cb},open('conflicts_v4.json','w'),ensure_ascii=False)
    for nm,X in [('main',M2),('bonus',B2)]:
        tot=sum(len(L['a']) for L in X); print(nm,len(X),'levels',tot,'answers',round(tot/len(X),2),'min',min(len(L['a']) for L in X),'max',max(len(L['a']) for L in X))
    print('conflicts resolved',len(cm),len(cb))
    json.dump(M2,open('main_levels.json','w'),ensure_ascii=False,separators=(',',':'))
    json.dump(B2,open('bonus_levels.json','w'),ensure_ascii=False,separators=(',',':'))
