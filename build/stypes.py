import json
from feat import G
from ids import D, parse, nodes, AR
T0=json.load(open('stroke_types.json'))
EXTRA={'犭':'sts','冫':'ki','礻':'kefk','彳':'ssf','灬':'kkkk','衤':'kefsk','罒':'fcffj','夂':'sel','宀':'kke',
 '疒':'kjkis','讠':'kp','艹':'jff','刂':'fg','氵':'kki','辶':'kal','爫':'skks','亠':'kj','匚':'jb','冖':'ke',
 '忄':'kkf','丷':'ks','纟':'nni','耂':'jfjs','卩':'rf','⺮':'sjksjk','阝':'wf','扌':'jgi','畐':'jfcjfcjfj',
 '亅':'g','丨':'f','丿':'s','丶':'k','乛':'e','𠃌':'r','⺈':'se','廴':'al','钅':'sjjjh','饣':'seh','攵':'sjsl',
 '彐':'cjj','龹':'ksjjsl','覀':'jfcffj','虍':'fjesju','⺌':'fks','㔾':'ru','丬':'kif','癶':'ekksl','廾':'jsf',
 '凵':'bf','囗':'fcj','勹':'sr','冂':'fr','厶':'nk','彡':'sss'}
TC={}
def types(c):
    if c in TC: return TC[c]
    r=None
    if c in EXTRA: r=EXTRA[c]
    elif c in T0 and c in G and len(T0[c])==len(G[c]['strokes']): r=T0[c]
    elif c in D and c in G:
        d=D[c]; n=len(G[c]['strokes'])
        try:
            tree,_=parse(d['decomposition']); mt=d.get('matches') or []
            out=[None]*n
            leaves={p:lab for p,lab in nodes(tree)}
            ok=True
            for p,lab in leaves.items():
                S=[i for i,m in enumerate(mt) if m is not None and tuple(m[:len(p)])==p]
                if not S: continue
                t=types(lab) if lab not in AR and lab!='？' else None
                if t is None or len(t)!=len(S): ok=False; break
                for i,x in zip(S,t): out[i]=x
            if ok and all(out): r=''.join(out)
        except Exception: r=None
    TC[c]=r; return r
COMPAT={('s','f'),('j','i'),('k','l'),('l','k'),('k','d'),('d','k'),('d','i'),('k','i')}
def tcompat(a,b): return a==b or (a,b) in COMPAT
if __name__=='__main__':
    import sys
    for c in sys.argv[1]: print(c,types(c))
