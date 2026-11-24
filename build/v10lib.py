"""v10 更宽松：「只要看得出来就行」——允许出头（相接↔穿过，最多 2 处）、比例略有出入。只用于≤7 画的常用字（部件型），大字靠 IDS 部件直接认。"""
import numpy as np
import gen, v9lib
from v9lib import strict_type, isx, outline_bad, junc_bad, feasible
from v4lib import fit, types, lenprof
LTHR=(0.105,0.28,0.62); AR=(0.25,4.0)
def topo_prot(T,M,c):
    n=len(c); prot=0
    for i in range(n):
        for j in range(i+1,n):
            a=isx(T,i,j); b=isx(M,c[i],c[j])
            if a==b: continue
            if b and not a: prot+=1   # 母字里穿过、目标里只是相接：出头
            else: return None
    return prot
def loose_ok(T,M,c):
    n=len(c); f=fit(T,M,c,*AR)
    if not f or not (f[0]<LTHR[0] and f[1]<LTHR[1] and f[2]>LTHR[2]): return None
    p=topo_prot(T,M,c)
    if p is None or p>2: return None
    if outline_bad(T,M,c)>(0 if n==2 else 1)+p: return None
    if lenprof(T,M,c)>=0.5: return None
    if junc_bad(T,M,c)>(1 if n<4 else 2)+p: return None
    if gap_bad(T,M,c): return None
    return f
from v9lib import pdist
from outline import bbox_ext
def gap_bad(T,M,c):
    n=len(c); eT=bbox_ext(T,range(n)); eM=bbox_ext(M,c)
    for i in range(n):
        dT=min(pdist(T,i,j) for j in range(n) if j!=i)/eT
        dM=min(pdist(M,c[i],c[j]) for j in range(n) if j!=i)/eM
        if dM>dT+0.10: return True
    return False
def loose_match(T,M,maxnodes=6000):
    tT=types(T); tM=types(M)
    if not tT or not tM: return []
    n=len(tT); N=len(tM)
    if n>=N or n==1 or not feasible(tT,tM): return []
    _,_,ST=gen.prep(T); _,_,SM=gen.prep(M)
    SH=np.sqrt(((ST[:,None]-SM[None])**2).sum(-1)).mean(-1)<0.42
    C=[[strict_type(tT[i],tM[j]) and SH[i,j] for j in range(N)] for i in range(n)]
    if not all(any(r) for r in C): return []
    out=[]; nodes=[0]; seen=set(); PT=gen.prep(T)[0]; PM=gen.prep(M)[0]
    def dfs(k,ch):
        nodes[0]+=1
        if nodes[0]>maxnodes: return
        if k==n:
            key=tuple(sorted(ch))
            if key in seen: return
            seen.add(key); f=loose_ok(T,M,ch)
            if f: out.append((round(f[0],4),list(ch)))
            return
        for j in range(N):
            if C[k][j] and j not in ch:
                nc=ch+[j]
                if k>=1 and gen.dist(PT[:k+1],PM[nc])[0]>(0.5 if k==1 else 0.45): continue
                dfs(k+1,nc)
    dfs(0,[]); out.sort(); return out
