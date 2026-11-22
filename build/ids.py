import json
from feat import G
D={}
for ln in open('dictionary.txt',encoding='utf8'):
    d=json.loads(ln); D[d['character']]=d
AR={c:3 if c in '⿲⿳' else 2 for c in '⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻'}
def parse(s,i=0):
    c=s[i]
    if c in AR:
        kids=[];j=i+1
        for _ in range(AR[c]):
            k,j=parse(s,j); kids.append(k)
        return (c,kids),j
    return (c,None),i+1
def nodes(tree,path=()):
    lab,kids=tree
    if kids is None: yield path,lab
    else:
        for i,k in enumerate(kids): yield from nodes(k,path+(i,))
DC={}
def desc(M,depth=0):
    """full IDS descendants: list of (char, stroke indices in M)"""
    if M in DC: return DC[M]
    out=[]
    d=D.get(M)
    if d and d.get('decomposition') and depth<8:
        try: tree,_=parse(d['decomposition'])
        except Exception: tree=None
        mt=d.get('matches') or []
        if tree and tree[1] is not None:
            for p,lab in nodes(tree):
                if lab in AR or lab in '？' or lab not in G: continue
                S=[i for i,m in enumerate(mt) if m is not None and tuple(m[:len(p)])==p]
                if len(S)!=len(G[lab]['strokes']) or len(S)==len(G[M]['strokes']): continue
                out.append((lab,S))
                for c2,S2 in desc(lab,depth+1):
                    out.append((c2,[S[j] for j in S2]))
    # dedupe
    seen=set(); res=[]
    for c,S in out:
        key=(c,tuple(sorted(S)))
        if key not in seen: seen.add(key); res.append((c,sorted(S)))
    DC[M]=res; return res
if __name__=='__main__':
    import sys
    for M in sys.argv[1]: print(M,[(c,S) for c,S in desc(M)])
