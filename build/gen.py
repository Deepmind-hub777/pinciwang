import json, math, sys
import numpy as np
G={}
for ln in open('graphics.txt',encoding='utf8'):
    d=json.loads(ln); G[d['character']]=d
D={}
for ln in open('dictionary.txt',encoding='utf8'):
    d=json.loads(ln); D[d['character']]=d
def rs(med,n=8):
    p=np.array(med,float); p[:,1]=900-p[:,1]
    seg=np.sqrt(((p[1:]-p[:-1])**2).sum(1)); L=seg.sum()
    if L<1e-6: return np.repeat(p[:1],n,0),1.0
    c=np.concatenate([[0],np.cumsum(seg)]); t=np.linspace(0,L,n)
    return np.stack([np.interp(t,c,p[:,0]),np.interp(t,c,p[:,1])],1),L
CACHE={}
def prep(ch):
    if ch in CACHE: return CACHE[ch]
    g=G[ch]; P=[];Ls=[];S=[]
    for m in g['medians']:
        r,L=rs(m); P.append(r); Ls.append(L)
        S.append((r-r[0])/max(L,1))
    v=(np.array(P),np.array(Ls),np.array(S)); CACHE[ch]=v; return v
def norm(P):
    pts=P.reshape(-1,2); mn=pts.min(0); mx=pts.max(0); ext=mx-mn
    m=max(ext.max(),1); ext=np.maximum(ext,0.3*m)
    c=(mn+mx)/2
    return (P-c)/ext, ext
def dist(PT,PM):
    a,ea=norm(PT); b,eb=norm(PM)
    ar=(ea[0]/ea[1])/(eb[0]/eb[1])
    d=np.sqrt(((a-b)**2).sum(-1)).mean()
    return d, ar
def match(T,M,thr=0.13,maxnodes=20000):
    PT,LT,ST=prep(T); PM,LM,SM=prep(M)
    n,N=len(PT),len(PM)
    if n>N: return []
    # shape compat
    C=np.sqrt(((ST[:,None]-SM[None])**2).sum(-1)).mean(-1) < 0.28
    vT=ST[:,-1]; vM=SM[:,-1]
    vT=vT/ (np.linalg.norm(vT,axis=1,keepdims=True)+1e-9); vM=vM/(np.linalg.norm(vM,axis=1,keepdims=True)+1e-9)
    C = C | ((vT@vM.T)>0.85)
    if not C.any(1).all(): return []
    res=[]; nodes=[0]
    def dfs(k,start,ch):
        nodes[0]+=1
        if nodes[0]>maxnodes: return
        if k==n:
            d,ar=dist(PT,PM[ch])
            if d<thr and 1/2.3<ar<2.3:
                # relative length consistency
                r=LM[ch]/LT; r=r/np.median(r)
                if r.max()<2.2 and r.min()>0.25: res.append((d,list(ch)))
            return
        for j in range(start,N-(n-k)+1):
            if C[k,j]:
                nc=ch+[j]
                if k>=2:
                    d,_=dist(PT[:k+1],PM[nc])
                    if d>thr*2.2: continue
                dfs(k+1,j+1,nc)
    dfs(0,0,[])
    res.sort()
    return res
VOC=[c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip()]
extra=[c.strip() for c in open('level-2.txt',encoding='utf8') if c.strip()]
EX=set('亍乂夂亠廿卅彡丫乜兀弋幺孑丐亓爻')
VOC=[c for c in VOC if c in G]+[c for c in extra if c in G and c in EX]
def solve(M,thr=0.13):
    out=[]
    N=len(G[M]['medians'])
    for T in VOC:
        if T==M: continue
        if len(G[T]['medians'])>=N: continue
        r=match(T,M,thr)
        if r:
            combos=[]; 
            for d,c in r:
                if c not in combos: combos.append(c)
            out.append({'c':T,'k':combos[:4],'sc':round(r[0][0],3)})
    out.sort(key=lambda a:(len(G[a['c']]['medians']),a['sc']))
    return out
if __name__=='__main__':
    for M in sys.argv[1:]:
        r=solve(M); print(M, ' '.join(a['c']+str(a['sc']) for a in r))

def judge(T,M,c):
    PT=prep(T)[0]; PM=prep(M)[0][c]
    A=PT.reshape(-1,2); B=PM.reshape(-1,2)
    ext=max(np.ptp(B,0).max(),1)
    out=np.zeros_like(B); s=[]
    for ax in range(2):
        a=A[:,ax]; b=B[:,ax]; va=a.var()
        sc=((a-a.mean())*(b-b.mean())).mean()/va if va>1e-3 else 1.0
        s.append(sc); out[:,ax]=sc*(a-a.mean())+b.mean()
    if min(s)<=0.15: return None
    ar=s[0]/s[1]
    if not (0.4<ar<2.5): return None
    O=out.reshape(PT.shape)
    d=np.sqrt(((O-PM)**2).sum(-1)).mean(-1)/ext
    # direction check on transformed strokes
    vo=O[:,-1]-O[:,0]; vm=PM[:,-1]-PM[:,0]
    lo=np.linalg.norm(vo,axis=1); lm=np.linalg.norm(vm,axis=1)
    cos=(vo*vm).sum(1)/(lo*lm+1e-9)
    big=lo>0.12*ext
    if (cos[big]<0.8).any(): return None
    return d.mean(), d.max()
def solve2(M, mean_thr=0.06, max_thr=0.13):
    N=len(G[M]['medians']); out=[]
    for T in VOC:
        if T==M or len(G[T]['medians'])>=N: continue
        r=match(T,M,thr=0.2,maxnodes=30000)
        good=[]
        for _,c in r:
            j=judge(T,M,c)
            if j and j[0]<mean_thr and j[1]<max_thr: good.append((j[0],c))
        if good:
            good.sort(); out.append((good[0][0],T,[c for _,c in good][:6]))
    return out
