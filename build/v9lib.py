"""v9 宽松找字：把“看得出来”的常用字也认出来（形变部件、田里的日、国里的口、寸里的十……），作为「额外字」。
条件：笔形兼容（竖/竖钩互认）+ 不要求笔顺 + 交叉关系一致（出头一点点算相接）+ 相接/分离、接点位置最多 1–2 处不同 + 放宽的仿射几何。"""
import numpy as np, json
from collections import Counter
import gen
from v4lib import fit, types, tcompat, _dense, _segx, _ext, lenprof
from outline import orel, bbox_ext
LOOSE=(0.15,0.26,0.72); AR=(0.3,3.3); XTHR=(0.12,0.20,0.80)
LOOSE_T={('f','g'),('g','f')}
def strict_type(a,b): return (tcompat(a,b) and not (a=='s' and b=='f')) or (a,b) in LOOSE_T
def rel2(ch,i,j,ext):
    (A,ta),(B,tb)=_dense(ch)[i],_dense(ch)[j]
    for a in range(len(A)-1):
        for b in range(len(B)-1):
            x=_segx(A[a],A[a+1],B[b],B[b+1])
            if x:
                fa=ta[a]+(ta[a+1]-ta[a])*x[0]; fb=tb[b]+(tb[b+1]-tb[b])*x[1]
                return 'X' if (0.18<fa<0.82 and 0.18<fb<0.82) else 'T'
    d=np.sqrt(((A[:,None]-B[None])**2).sum(-1)).min()/ext
    return 'T' if d<0.035 else ('A' if d>0.085 else '?')
_XC={}
def isx(ch,i,j):
    if i>j: i,j=j,i
    k=(ch,i,j)
    if k not in _XC: _XC[k]=rel2(ch,i,j,1e9)=='X'
    return _XC[k]
def topo_ok(T,M,c):
    n=len(c)
    for i in range(n):
        for j in range(i+1,n):
            if isx(T,i,j)!=isx(M,c[i],c[j]): return False
    return True
from outline import poly
_PD={}
def pdist(ch,i,j):
    if i>j: i,j=j,i
    k=(ch,i,j)
    if k not in _PD: _PD[k]=poly(ch,i).distance(poly(ch,j))
    return _PD[k]
def _orel(ch,i,j,ext):
    d=pdist(ch,i,j)/ext
    return 'T' if d<=0.004 else ('A' if d>0.03 else '?')
def outline_bad(T,M,c):
    n=len(c); eT=bbox_ext(T,range(n)); eM=bbox_ext(M,c); bad=0
    for i in range(n):
        for j in range(i+1,n):
            if {_orel(T,i,j,eT),_orel(M,c[i],c[j],eM)}=={'T','A'}: bad+=1
    return bad
_JC={}
def _jraw(ch,i,j):
    k=(ch,i,j)
    if k not in _JC:
        (A,ta),(B,tb)=_dense(ch)[i],_dense(ch)[j]
        D=np.sqrt(((A[:,None]-B[None])**2).sum(-1)); q=np.unravel_index(D.argmin(),D.shape)
        _JC[k]=(D[q],ta[q[0]],tb[q[1]])
    return _JC[k]
def _jpos(ch,i,j,ext):
    d,a,b=_jraw(ch,i,j)
    if d/ext>0.06: return None
    q=lambda t:'s' if t<0.22 else ('e' if t>0.78 else 'm')
    return q(a)+q(b)
def junc_bad(T,M,c):
    n=len(c); eT=_ext(T,range(n)); eM=_ext(M,c); bad=0
    for i in range(n):
        for j in range(i+1,n):
            a=_jpos(T,i,j,eT); b=_jpos(M,c[i],c[j],eM)
            if a is None and b is None: continue
            if a is None or b is None or a!=b: bad+=1
    return bad
def feasible(tT,tM):
    cM=Counter(tM)
    for t,k in Counter(tT).items():
        if sum(v for u,v in cM.items() if strict_type(t,u))<k: return False
    return True
def extra_ok(T,M,c):
    n=len(c); f=fit(T,M,c,*AR)
    if not f or not (f[0]<XTHR[0] and f[1]<XTHR[1] and f[2]>XTHR[2]): return None
    if not topo_ok(T,M,c): return None
    if outline_bad(T,M,c)>(0 if n==2 else 1): return None
    if lenprof(T,M,c)>=0.4: return None
    if junc_bad(T,M,c)>(1 if n<4 else 2): return None
    return f
def extra_match(T,M,maxnodes=5000):
    tT=types(T); tM=types(M)
    if not tT or not tM: return []
    n=len(tT); N=len(tM)
    if n>=N or n==1 or not feasible(tT,tM): return []
    _,_,ST=gen.prep(T); _,_,SM=gen.prep(M)
    SH=np.sqrt(((ST[:,None]-SM[None])**2).sum(-1)).mean(-1)<0.35
    C=[[strict_type(tT[i],tM[j]) and SH[i,j] for j in range(N)] for i in range(n)]
    if not all(any(r) for r in C): return []
    out=[]; nodes=[0]; seen=set(); PT=gen.prep(T)[0]; PM=gen.prep(M)[0]
    def dfs(k,ch):
        nodes[0]+=1
        if nodes[0]>maxnodes: return
        if k==n:
            key=tuple(sorted(ch))
            if key in seen: return
            seen.add(key); f=extra_ok(T,M,ch)
            if f: out.append((round(f[0],4),list(ch)))
            return
        for j in range(N):
            if C[k][j] and j not in ch:
                nc=ch+[j]
                if k>=1 and gen.dist(PT[:k+1],PM[nc])[0]>(0.45 if k==1 else 0.40): continue
                dfs(k+1,nc)
    dfs(0,[]); out.sort(); return out
