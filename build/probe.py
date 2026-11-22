"""同一把尺子：丁假阳性 / 笔形违规 / 跨字组字 / 同集冲突 / 40 常用字漏收"""
import json, sys, collections
import gen
from v4lib import desc, check, assign, typeok, IDS_THR
PROBE40=list('十口木人土日大火米几车立月目田山王工力又小女子心石禾白言门马牛羊文方寸干刀儿八丁')
assert len(PROBE40)==40, len(PROBE40)
def segs(L):
    out=[];o=0
    for ch in L['ch']: n=len(ch['st']); out.append((ch['c'],o,o+n)); o+=n
    return out
def run(levels):
    r=collections.Counter(); ding=[]; viol=collections.Counter(); confl=[]; miss=[]; cands=0
    for L in levels:
        S=segs(L); selfc={c for c,_,_ in S}
        def seg_of(i): return [k for k,(c,a,b) in enumerate(S) if a<=i<b][0]
        owners=collections.defaultdict(set)
        have={a['c'] for a in L['a']}
        for a in L['a']:
            for k in a['k']:
                owners[tuple(sorted(k))].add(a['c'])
                sg={seg_of(i) for i in k}
                if len(sg)>1: r['cross']+=1; continue
                if a['c'] in selfc and len(k)==S[sg.pop() if False else seg_of(k[0])][2]-S[seg_of(k[0])][1]: continue
                M,o,_=S[seg_of(k[0])]; loc=[i-o for i in k]
                if len(loc)!=len(gen.G[a['c']]['strokes']): viol[a['c']]+=1; r['countbad']+=1; continue
                if not typeok(a['c'],M,assign(a['c'],M,loc)):
                    viol[a['c']]+=1; r['typeviol']+=1
                    if a['c']=='丁': ding.append((L['n'],L['t'],k))
        for key,cs in owners.items():
            if len(cs)>1: confl.append((L['n'],L['t'],list(key),sorted(cs)))
        seen=set()
        for M,o,_ in S:
            for T,Sx in desc(M):
                if T not in PROBE40 or T==M or T in have or (T,L['n']) in seen: continue
                cands+=1
                if check(T,M,assign(T,M,Sx),*IDS_THR): seen.add((T,L['n'])); miss.append((L['n'],L['t'],T))
    return dict(levels=len(levels),answers=sum(len(L['a']) for L in levels),cross=r['cross'],typeviol=r['typeviol'],
        ding_fp=len(ding),ding=ding,viol_top=viol.most_common(15),conflicts=len(confl),conflict_ex=confl[:12],
        probe_cands=cands,probe_miss=len(miss),probe_by=collections.Counter(t for _,_,t in miss).most_common(15),miss_ex=miss[:30])
if __name__=='__main__':
    for f in sys.argv[1:]:
        X=json.load(open(f)); R=run(X)
        print('==',f); 
        for k,v in R.items(): print(' ',k,v)
