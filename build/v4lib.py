import json, numpy as np
import gen
from feat import feats, compat as fcompat
from ids import desc, D
from stypes import types, tcompat
def typeok(T,M,c):
    tT=types(T); tM=types(M)
    if tT and tM:
        return all(tcompat(tT[i],tM[j]) for i,j in enumerate(c))
    fT=feats(T); fM=feats(M)
    return all(fcompat(fT[i],fM[j]) for i,j in enumerate(c))
def fit(T,M,c,arlo=0.25,arhi=4.0):
    PT=gen.prep(T)[0]; PM=gen.prep(M)[0][list(c)]
    A=PT.reshape(-1,2); B=PM.reshape(-1,2)
    ext=max(np.ptp(B,0).max(),1)
    out=np.zeros_like(B); s=[]
    for ax in range(2):
        a=A[:,ax]; b=B[:,ax]; va=a.var()
        sc=((a-a.mean())*(b-b.mean())).mean()/va if va>1e-3 else None
        s.append(sc)
    if s[0] is None and s[1] is None: return None
    if s[0] is None: s[0]=s[1]
    if s[1] is None: s[1]=s[0]
    if min(s)<=0.05: return None
    ar=s[0]/s[1]
    if not (arlo<ar<arhi): return None
    for ax in range(2):
        a=A[:,ax]; b=B[:,ax]; out[:,ax]=s[ax]*(a-a.mean())+b.mean()
    O=out.reshape(PT.shape)
    d=np.sqrt(((O-PM)**2).sum(-1)).mean(-1)/ext
    vo=O[:,-1]-O[:,0]; vm=PM[:,-1]-PM[:,0]
    lo=np.linalg.norm(vo,axis=1); lm=np.linalg.norm(vm,axis=1)
    cos=(vo*vm).sum(1)/(lo*lm+1e-9)
    big=lo>0.12*ext
    mc=cos[big].min() if big.any() else 1.0
    return float(d.mean()), float(d.max()), float(mc), float(ar)

from scipy.optimize import linear_sum_assignment
FREQ=json.load(open('charfreq.json'))
def _norm_all(P):
    pts=P.reshape(-1,2); mn=pts.min(0); mx=pts.max(0); ext=np.maximum(mx-mn,1); m=ext.max(); ext=np.maximum(ext,0.3*m)
    return (P-(mn+mx)/2)/ext
def assign(T,M,S):
    """order M strokes S to correspond to T's stroke order (types + geometry)"""
    S=list(S); n=len(S)
    if n==1: return S
    PT=_norm_all(gen.prep(T)[0]); PM=_norm_all(gen.prep(M)[0][S])
    tT=types(T); tM=types(M)
    C=np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            d=np.sqrt(((PT[i]-PM[j])**2).sum(-1)).mean()
            if tT and tM and not tcompat(tT[i],tM[S[j]]): d+=10
            C[i,j]=d
    r,c=linear_sum_assignment(C)
    return [S[j] for j in c]
def lenprof(T,M,c):
    LT=gen.prep(T)[1]; LM=gen.prep(M)[1][list(c)]
    a=np.log(LT/LT.mean()+1e-6); b=np.log(LM/LM.mean()+1e-6)
    return float(np.abs(a-b).mean())
def check(T,M,c,mean_thr,max_thr,cos_thr,ar=(0.25,4.0)):
    if len(c)!=len(gen.G[T]['medians']): return None
    if not typeok(T,M,c): return None
    if len(c)==1:
        tT=types(T); tM=types(M)
        if tT and tM: return (0.0,0.0,1.0,1.0) if tT[0]==tM[c[0]] else None
    f=fit(T,M,c,*ar)
    if not f: return None
    if f[0]<mean_thr and f[1]<max_thr and f[2]>cos_thr: return f
    return None
IDS_THR=(0.17,0.30,0.7)
GEO_THR=(0.056,0.12,0.8)
def score(T,M,c,f,src):
    return f[0]+0.1*lenprof(T,M,c)+0.05*abs(np.log(f[3]))-(0.015 if src=='ids' else 0)
CORE=list('十口木人土日大火米几车立月目田山王工力又小女子心石禾白言门马牛羊文方寸干刀儿八丁')
CORE_THR=(0.08,0.16,0.75)
def solve_v4(M, vocab, geo_cache, core=True):
    """returns {T: [(stroke list in T order, score, src), ...]} for one segment char"""
    N=len(gen.G[M]['strokes'])
    cand={}
    def add(T,c,src,thr):
        if T==M or T not in vocab or len(c)>=N: return
        f=check(T,M,c,*thr)
        if not f: return
        key=tuple(sorted(c))
        lst=cand.setdefault(T,{})
        s=score(T,M,c,f,src)
        if key not in lst or lst[key][1]>s: lst[key]=(list(c),s,src)
    for T,S in desc(M):
        if T in vocab and T in gen.G:
            add(T,assign(T,M,S),'ids',IDS_THR)
    for sc,T,ks in (geo_cache or []):
        for k in ks: add(T,list(k),'geo',GEO_THR)
    if core:
        for T in CORE:
            if T in vocab and T!=M and len(gen.G[T]['medians'])<N:
                for _,k in gen.match(T,M,thr=0.2,maxnodes=20000): add(T,list(k),'geo2',CORE_THR)
    # single-stroke chars: every stroke of exactly that type
    tM=types(M)
    if tM:
        for T in ('一',):
            if T in vocab:
                for j,t in enumerate(tM):
                    if t=='j': add(T,[j],'type',GEO_THR)
    return {T:list(v.values()) for T,v in cand.items()}
def resolve(level_ans):
    """level_ans: {T: [(c,score,src)...]} with global indices. one stroke set -> one char."""
    owner={}
    for T,lst in level_ans.items():
        for c,s,src in lst:
            key=tuple(sorted(c))
            owner.setdefault(key,[]).append((T,s,src,c))
    out={}; conflicts=[]
    for key,cl in owner.items():
        if len(cl)>1:
            cl.sort(key=lambda x:(x[2]!='ids',x[1]))
            best=cl[0]
            same=[x for x in cl if (x[2]=='ids')==(best[2]=='ids')]
            top=max(same,key=lambda x:FREQ.get(x[0],0))
            if FREQ.get(top[0],0)>5*FREQ.get(best[0],1): best=top   # 一形两字：差异悬殊时取常用字（日>曰）
            else:
                close=[x for x in same if x[1]-best[1]<0.03]
                if len(close)>1: best=max(close,key=lambda x:FREQ.get(x[0],0))
            conflicts.append((key,[x[0] for x in cl],best[0]))
        else: best=cl[0]
        out.setdefault(best[0],[]).append((best[3],best[1],best[2]))
    return out,conflicts

# ---------- 拓扑：笔画两两 相交 / 相接 / 分离 必须一致 ----------
def _dense(ch):
    if ch in _DC: return _DC[ch]
    out=[]
    for m in gen.G[ch]['medians']:
        P=np.array(m,float); P[:,1]=900-P[:,1]
        seg=np.sqrt(((P[1:]-P[:-1])**2).sum(1)); c=np.concatenate([[0],np.cumsum(seg)]); L=max(c[-1],1)
        t=np.linspace(0,L,max(int(L/6),2)+1)
        out.append((np.stack([np.interp(t,c,P[:,0]),np.interp(t,c,P[:,1])],1),t/L))
    _DC[ch]=out; return out
_DC={}
def _segx(p1,p2,q1,q2):
    d1=p2-p1; d2=q2-q1; den=d1[0]*d2[1]-d1[1]*d2[0]
    if abs(den)<1e-9: return None
    w=q1-p1; s=(w[0]*d2[1]-w[1]*d2[0])/den; u=(w[0]*d1[1]-w[1]*d1[0])/den
    if 0<=s<=1 and 0<=u<=1: return s,u
    return None
def rel(ch,i,j,ext):
    (A,ta),(B,tb)=_dense(ch)[i],_dense(ch)[j]
    # proper interior crossing
    for a in range(len(A)-1):
        for b in range(len(B)-1):
            x=_segx(A[a],A[a+1],B[b],B[b+1])
            if x:
                fa=ta[a]+(ta[a+1]-ta[a])*x[0]; fb=tb[b]+(tb[b+1]-tb[b])*x[1]
                if 0.1<fa<0.9 and 0.1<fb<0.9: return 'X'
    d=np.sqrt(((A[:,None]-B[None])**2).sum(-1)).min()/ext
    if d<0.035: return 'T'
    if d>0.085: return 'A'
    return '?'
def _ext(ch,idx):
    P=np.concatenate([_dense(ch)[i][0] for i in idx]); return max(np.ptp(P,0).max(),1)
def topo_ok(T,M,c,tol=0):
    n=len(c)
    if n<2: return True
    eT=_ext(T,range(n)); eM=_ext(M,c)
    bad=0
    for i in range(n):
        for j in range(i+1,n):
            a=rel(T,i,j,eT); b=rel(M,c[i],c[j],eM)
            if (a=='X')!=(b=='X'): bad+=1
    return bad<=(tol if n>=3 else 0)
_check0=check
def check(T,M,c,mean_thr,max_thr,cos_thr,ar=(0.25,4.0),tol=None):
    if tol is None: tol=1 if (mean_thr,max_thr,cos_thr)==IDS_THR else 0   # IDS 结构来源允许 1 处交叉差异（变形部件）
    f=_check0(T,M,c,mean_thr,max_thr,cos_thr,ar)
    if f and not topo_ok(T,M,c,tol): return None
    return f

def typeok_strict(T,M,c):
    """非结构来源的候选：不允许 撇→竖 的宽松对应"""
    tT=types(T); tM=types(M)
    if tT and tM:
        return all(tcompat(tT[i],tM[j]) and not (tT[i]=='s' and tM[j]=='f') for i,j in enumerate(c))
    return True
