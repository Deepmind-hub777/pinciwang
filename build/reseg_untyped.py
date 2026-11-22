"""v4.1：只重算缺少笔形数据（多为繁体）的分段字，更新 segcache_v4.pkl"""
import pickle, json
from multiprocessing import Pool
import build_v4 as B, v4lib as V
if __name__=='__main__':
    sm,sb=pickle.load(open('segcache_v4.pkl','rb'))
    todo=[m for m in sm if not V.types(m)]
    btodo=[m for m in sb if not V.types(m)]
    print('reseg',len(todo),len(btodo),flush=True)
    with Pool(8) as p:
        for M,r in p.imap_unordered(B.seg_main,todo): sm[M]=r
        for M,r in p.imap_unordered(B.seg_bonus,btodo): sb[M]=r
    pickle.dump((sm,sb),open('segcache_v4.pkl','wb'))
