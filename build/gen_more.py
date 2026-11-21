import json, gen, random
from multiprocessing import Pool
def work(c):
    try: return c, [(float(sc),T,ks) for sc,T,ks in gen.solve2(c,0.056,0.12)]
    except Exception as e: return c, None
if __name__=='__main__':
    order=json.load(open('more_order.json'))
    cur=json.load(open('levels_out.json'))
    used={c for l in cur for c in l['t']}|set(order)
    VOC1=[c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip()]
    filler=[c for c in VOC1 if c in gen.G and c not in used and 7<=len(gen.G[c]['medians'])<=16]
    random.seed(3); random.shuffle(filler); filler=filler[:700]
    todo=order+filler
    with Pool(8) as p:
        res=dict(p.map(work,todo,chunksize=4))
    json.dump({'order':order,'filler':filler,'res':res},open('more_cache.json','w'),ensure_ascii=False)
    print('done',len(res))
