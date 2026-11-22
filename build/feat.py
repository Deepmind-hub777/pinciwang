import json, math, numpy as np
G={}
for ln in open('graphics.txt',encoding='utf8'):
    d=json.loads(ln); G[d['character']]=d
def resample(P,step=4.0):
    seg=np.sqrt(((P[1:]-P[:-1])**2).sum(1)); c=np.concatenate([[0],np.cumsum(seg)]); L=c[-1]
    n=max(int(L/step),2); t=np.linspace(0,L,n+1)
    return np.stack([np.interp(t,c,P[:,0]),np.interp(t,c,P[:,1])],1),L,t
def ang(v): return math.degrees(math.atan2(v[1],v[0]))
def dang(a,b): return abs((b-a+180)%360-180)
def feat(med):
    P=np.array(med,float); P[:,1]=900-P[:,1]
    Q,L,t=resample(P)
    if L<60: return dict(hook=0,turns=0,L=L,corners=[])
    w=max(0.1*L,30); k=max(int(round(w/(t[1]-t[0]))),1)
    n=len(Q); th=np.zeros(n)
    for i in range(1,n-1):
        a=Q[max(i-k,0)]; b=Q[i]; c=Q[min(i+k,n-1)]
        v1=b-a; v2=c-b
        if np.linalg.norm(v1)<1e-6 or np.linalg.norm(v2)<1e-6: continue
        th[i]=dang(ang(v1),ang(v2))
    cs=[]
    i=1
    while i<n-1:
        if th[i]>=60 and th[i]==th[max(i-k,1):min(i+k+1,n-1)].max():
            cs.append((t[i],th[i])); i+=k
        else: i+=1
    hook=0; corners=[]
    for s,a in cs:
        if s<0.12*L or (s<0.25*L and a<80): continue   # serif（起笔顿笔/短笔噪声）
        corners.append((round(s/L,2),round(a)))
    turns=len(corners)
    if corners:
        s,a=corners[-1]; tail=1-s
        if tail<0.33 and a>=70:
            hook=2 if (tail>=0.16 and a>=80) else 1
            turns-=1
    return dict(hook=hook,turns=turns,L=round(L),corners=corners)
FC={}
def feats(ch):
    if ch not in FC: FC[ch]=[feat(m) for m in G[ch]['medians']]
    return FC[ch]
def strong(f):
    cs=f['corners'][:f['turns']]   # 去掉末尾钩
    return sum(1 for _,ang in cs if ang>=80)
def compat(a,b):
    """T stroke a may be represented by M stroke b"""
    if a['turns']!=b['turns']:
        # v4.1：缺笔形数据时，角度<80°的弱折角可能是平滑误差；只要求双方的强折角都能在对方找到对应
        sa=strong(a); sb=strong(b)
        if not (sa<=b['turns'] and sb<=a['turns'] and abs(a['turns']-b['turns'])==1): return False
    if a['hook'] and not b['hook']: return False
    if not a['hook'] and b['hook']==2: return False
    return True
if __name__=='__main__':
    import sys
    for c in sys.argv[1]:
        print(c,' | '.join('H%d T%d %s'%(f['hook'],f['turns'],f['corners']) for f in feats(c)))
