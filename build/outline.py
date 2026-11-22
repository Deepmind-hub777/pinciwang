import re, numpy as np
from shapely.geometry import Polygon
from shapely.validation import make_valid
import gen
_PC={}
def poly(ch,i):
    key=(ch,i)
    if key in _PC: return _PC[key]
    d=gen.G[ch]['strokes'][i]
    tok=re.findall(r'[MLQCZ]|-?\d+(?:\.\d+)?',d)
    pts=[];k=0;cur=None;cmd=None
    while k<len(tok):
        t=tok[k]
        if t in 'MLQCZ': cmd=t;k+=1
        if cmd=='Z': k+=0; cmd=None; continue
        if cmd in ('M','L'):
            cur=(float(tok[k]),float(tok[k+1]));pts.append(cur);k+=2
        elif cmd=='Q':
            c1=np.array(tok[k:k+2],float);p=np.array(tok[k+2:k+4],float);a=np.array(cur)
            for s in np.linspace(0,1,7)[1:]: pts.append(tuple((1-s)**2*a+2*(1-s)*s*c1+s*s*p))
            cur=tuple(p);k+=4
        elif cmd=='C':
            c1=np.array(tok[k:k+2],float);c2=np.array(tok[k+2:k+4],float);p=np.array(tok[k+4:k+6],float);a=np.array(cur)
            for s in np.linspace(0,1,7)[1:]: pts.append(tuple((1-s)**3*a+3*(1-s)**2*s*c1+3*(1-s)*s*s*c2+s**3*p))
            cur=tuple(p);k+=6
        else: k+=1
    P=Polygon(pts)
    if not P.is_valid: P=make_valid(P)
    _PC[key]=P; return P
def bbox_ext(ch,idx):
    b=np.array([poly(ch,i).bounds for i in idx]); return max(b[:,2].max()-b[:,0].min(), b[:,3].max()-b[:,1].min(),1)
def orel(ch,i,j,ext):
    d=poly(ch,i).distance(poly(ch,j))/ext
    return 'T' if d<=0.004 else ('A' if d>0.03 else '?')
def outline_ok(T,M,c):
    n=len(c)
    if n<2: return True
    eT=bbox_ext(T,range(n)); eM=bbox_ext(M,c)
    bad=0
    for i in range(n):
        for j in range(i+1,n):
            if {orel(T,i,j,eT),orel(M,c[i],c[j],eM)}=={'T','A'}: bad+=1
    return bad<=(0 if n<=4 else 1)
