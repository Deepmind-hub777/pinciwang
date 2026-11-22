import json, gen
from multiprocessing import Pool
def work(c):
    try: return c, [(float(sc),T,ks) for sc,T,ks in gen.solve2(c,0.056,0.12)]
    except Exception as e: return c, None
if __name__=='__main__':
    mc=json.load(open('more_cache.json'))['res']
    main=json.load(open('main_levels.json'))
    segs=sorted({ch['c'] for l in main for ch in l['ch']})
    todo=[c for c in segs if c not in mc or mc[c] is None]
    with Pool(8) as p: res=dict(p.map(work,todo,chunksize=2))
    json.dump(res,open('miss_cache.json','w'),ensure_ascii=False); print('done',len(res),sum(v is None for v in res.values()))
