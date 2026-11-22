"""后花园 · 部首与结构挑战 题库生成
数据：bushou/sources_3500.json（各来源原始值 + GF 0012 扫描核对结果），见 README「v6」。
输出：../data/bushou.js 及 bushou/questions.json（便于老师核对）、bushou/audio_jobs.json
"""
import json,random,collections,sys,os
sys.path.insert(0,'bushou')
from rads import RAD201
from norm import ATT,main
from names import FIXED,SIDE
from pypinyin import pinyin,Style
SRC=json.load(open('bushou/sources_3500.json'))
L1=list(SRC)
FREQ=json.load(open('charfreq.json'))
MM={}
for l in open('dictionary.txt'):
    d=json.loads(l); MM[d['character']]=d
# ---------- 结构 ----------
MPC={'D':'独体','A':'品字形','B':'上下','E':'上中下','H':'左右','M':'左中右','Q':'全包围','R':'半包围'}
SUB={'R1':'左三包围','R2':'左上包围','R3':'右上包围','R4':'左下包围','R5':'上三包围','R6':'下三包围'}
OPS={'⿰':'左右','⿱':'上下','⿲':'左中右','⿳':'上中下','⿴':'全包围','⿵':'半包围','⿶':'半包围','⿷':'半包围','⿸':'半包围','⿹':'半包围','⿺':'半包围','⿻':'独体'}
OPSUB={'⿵':'上三包围','⿶':'下三包围','⿷':'左三包围','⿸':'左上包围','⿹':'右上包围','⿺':'左下包围'}
ARITY={o:2 for o in '⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻'}; ARITY.update({'⿲':3,'⿳':3})
def parse(s,i=0):
    if i>=len(s): return None,i
    c=s[i]
    if c in ARITY:
        kids=[];j=i+1
        for _ in range(ARITY[c]):
            k,j=parse(s,j); kids.append(k)
        return (c,kids),j
    return c,i+1
def ids(c):
    d=MM.get(c,{}).get('decomposition') or ''
    if not d or d[0] not in ARITY: return None
    t,_=parse(d); return t
def leaves(t,acc):
    if t is None: return acc
    if isinstance(t,str): acc.append(t); return acc
    acc.append(t); [leaves(k,acc) for k in t[1]]; return acc
# 两源一致才收；品字形、左中右按教学惯例采用 mapull（IDS 无法表示品字形，左中右常被 IDS 拆成两层）
SAFE_DUTI=set('二三干工土下上口千王天元无不文方正')
def structure(c):
    s=SRC[c]['structure_mapull']; a=MPC[s[0]]; asub=SUB.get(s)
    t=ids(c); b,bsub=('独体',None) if t is None else (OPS[t[0]],OPSUB.get(t[0]))
    if a==b:
        sub=asub if (asub and (bsub is None or asub==bsub)) else (bsub if a=='半包围' and not asub else None)
        if a=='半包围' and asub and bsub and asub!=bsub: sub=None
        return a,sub,'agree'
    if a=='品字形' and b=='上下': return a,None,'convention'
    if a=='左中右' and b=='左右': return a,None,'convention'
    if a=='独体' and c in SAFE_DUTI: return a,None,'convention'
    return None,None,'conflict'
# ---------- 部首 ----------
DISPLAY_OK=set(json.load(open('bushou/answer_forms.json'))) if os.path.exists('bushou/answer_forms.json') else set(RAD201)
def pos_of(c,form,gmain):
    t=ids(c)
    if c==form: return 'S'
    if t is None: return 'X'
    op,kids=t
    def hit(k):
        if isinstance(k,str): return k==form or (main(k)==gmain and main(k) is not None and (k==form or ATT.get(k)==ATT.get(form,form) or k in (form,)))
        return False
    if op in '⿴⿵⿶⿷⿸⿹⿺': return 'O' if hit(kids[0]) else 'X'
    if op in '⿰⿲':
        if hit(kids[0]): return 'L'
        if hit(kids[-1]): return 'R'
    if op in '⿱⿳':
        if hit(kids[0]): return 'T'
        if hit(kids[-1]): return 'B'
    return 'X'
OUTER={'麻':'麻字头','户':'户字头','走':'走字旁','鬼':'鬼字旁','毛':'毛字旁','气':'气字头','凵':'凶字框','戈':'戈字旁','是':'是字旁','风':'风字框'}
def name(c,form,gmain,pos):
    if form=='阝': return '左耳旁' if gmain=='阜' else '右耳旁'
    if pos=='S': return '本字就是部首'
    if form in FIXED: return FIXED[form]
    if pos=='L': return SIDE.get(form,form+'字旁')
    if pos=='T': return form+'字头'
    if pos=='B': return form+'字底'
    if pos=='O' and form in OUTER: return OUTER[form]
    return form+'部'
SIMILAR=[set('氵冫讠'),set('礻衤'),set('亻彳'),set('扌木牜'),set('日目曰月'),set('宀冖穴'),set('艹⺮'),set('厂广疒尸户'),set('刂卩阝'),
 set('攵夂'),set('土士工干'),set('忄小'),set('钅饣纟'),set('口囗'),set('己巳'),set('人入八'),set('贝见页'),set('门冂'),set('犭豸'),
 set('辶廴'),set('灬火'),set('王玉'),set('刀力'),set('儿几'),set('匚凵'),set('禾木米'),set('石右'),set('衣示'),set('又攵'),set('田由甲'),
 set('白自'),set('大犬'),set('巾市'),set('牛手'),set('羊⺶'),set('目耳'),set('虫史'),set('子孑'),set('女安'),set('彡巛')]
COMMON_FALLBACK=list('氵扌口木艹亻月讠纟土辶忄钅女宀日虫贝竹火心石禾目王山广')
def pool_forms(): return None
def distractors(c,form,gmain,alts,rng):
    out=[];seen={form}; mains={gmain}
    def add(f):
        if f in seen or f not in DISPLAY_OK: return
        m=main(f) or f
        if m in mains: return
        if f=='阝' or (form=='阝' and f=='阝'): return
        seen.add(f); mains.add(m); out.append(f)
    for a in alts: add(a)            # 康熙体系归部（易混项）
    t=ids(c)
    comps=[x for x in leaves(t,[]) if isinstance(x,str)] if t else []
    for f in comps: add(f)           # 本字的其他部件
    for g in SIMILAR:                # 形近部首
        if form in g:
            for f in sorted(g): add(f)
    rest=[f for f in COMMON_FALLBACK]; rng.shuffle(rest)
    for f in rest: add(f)
    return out
# ---------- 读音 ----------
FIX={'肋':'lèi','茸':'róng','勒':'lè','了':'le','卓':'zhuó','只':'zhǐ','罗':'luó','卜':'bǔ','子':'zǐ'}
TM={'ā':('a',1),'á':('a',2),'ǎ':('a',3),'à':('a',4),'ē':('e',1),'é':('e',2),'ě':('e',3),'è':('e',4),'ī':('i',1),'í':('i',2),'ǐ':('i',3),'ì':('i',4),
'ō':('o',1),'ó':('o',2),'ǒ':('o',3),'ò':('o',4),'ū':('u',1),'ú':('u',2),'ǔ':('u',3),'ù':('u',4),'ǖ':('v',1),'ǘ':('v',2),'ǚ':('v',3),'ǜ':('v',4),'ü':('v',0)}
def num(py):
    t=5; o=''
    for ch in py:
        if ch in TM:
            b,tt=TM[ch]; o+=b
            if tt: t=tt
        else: o+=ch
    return o+str(t)
def py_of(c): return FIX.get(c) or pinyin(c,style=Style.TONE)[0][0]
def mono(c): return len(set(pinyin(c,style=Style.TONE,heteronym=True)[0]))==1
OV=json.load(open('tts_override.json'))
# ---------- 汇总 ----------
pool=[];stats=collections.Counter();excl=collections.Counter()
for c in L1:
    s=SRC[c]
    if not s['gf']: excl['部首未能核实']+=1; continue
    st,sub,how=structure(c)
    if not st: excl['结构两源不一致']+=1; continue
    form,gmain,rsrc=s['gf']
    pos=pos_of(c,form,gmain)
    alts=[]
    for k in ('hanzidict','xinhua','mapull'):
        v=(s[k] or '').split('、')[0]
        if v and main(v) and main(v)!=gmain and v not in alts: alts.append(v)
    py=py_of(c)
    pool.append(dict(c=c,st=st,sub=sub,sts=how,r=form,m=gmain,rs=rsrc,pos=pos,nm=name(c,form,gmain,pos),alts=alts,py=py,f=FREQ.get(c,0)))
    stats[rsrc]+=1
json.dump(sorted(set(q['r'] for q in pool)-set('亅乚⺄龵㔾⺪')),open('bushou/answer_forms.json','w'),ensure_ascii=False)
DISPLAY_OK=set(json.load(open('bushou/answer_forms.json')))
print('pool',len(pool),dict(stats),'excluded',dict(excl))
# ---------- 分级 ----------
fc=collections.Counter(q['r'] for q in pool)
STROKE1=set('一丨丿丶乛')
COMMON=set(f for f,n in fc.items() if n>=35 and f not in STROKE1 and f!='疒')
def tier(q):
    if q['rs']!='agree' or q['alts']: return 2
    if q['r'] in COMMON and q['c']!=q['r']: return 0
    return 1
for q in pool: q['tier']=tier(q)
rng=random.Random(20261122)
levels=[];TIERN=['常见部首','少见部首','易混部首']
for t in range(3):
    qs=sorted([q for q in pool if q['tier']==t],key=lambda q:-q['f'])
    for i in range(0,len(qs),10):
        chunk=qs[i:i+10]
        if len(chunk)<5 and levels and levels[-1]['t']==t: levels[-1]['q']+=chunk; continue
        levels.append(dict(t=t,q=chunk))
# distractors & options
out_levels=[]
for n,L in enumerate(levels):
    ql=[]
    for q in L['q']:
        ds=distractors(q['c'],q['r'],q['m'],q['alts'],rng)[:3]
        assert len(ds)==3,(q['c'],ds)
        opts=ds+[q['r']]; rng.shuffle(opts)
        au='zi/%04x_%s'%(ord(q['c']),num(q['py']))
        ql.append([q['c'],q['st'],q['sub'] or '',q['r'],q['nm'],''.join(opts) if all(len(o)==1 for o in opts) else opts,q['py'],au,q['m']])
    out_levels.append(dict(n=n+1,t=L['t'],q=ql))
cnt=collections.Counter(L['t'] for L in out_levels)
print('levels',len(out_levels),{TIERN[k]:v for k,v in cnt.items()},'questions/tier',collections.Counter(q['tier'] for q in pool))
json.dump(dict(tiers=TIERN,levels=out_levels),open('bushou/questions.json','w'),ensure_ascii=False,indent=0)
# audio jobs
jobs=[]
have=set(os.listdir('../audio/zi'))
for L in out_levels:
    for q in L['q']:
        fn=q[7].split('/')[1]+'.mp3'
        if fn in have: continue
        c,py=q[0],q[6]
        text=OV.get(c)
        if not text and not mono(c):
            cand=sorted([v for v in L1 if mono(v) and py_of(v)==py and v!=c],key=lambda v:-FREQ.get(v,0))
            text=cand[0] if cand else c
        jobs.append([c,py,text or c,fn])
json.dump(jobs,open('bushou/audio_jobs.json','w'),ensure_ascii=False)
print('audio to make',len(jobs),'subs',sum(1 for j in jobs if j[2]!=j[0]))
js='/* 后花园 · 部首与结构挑战：[字,结构,半包围细类,部首(显示形),部首名称,四个选项,拼音,读音文件,GF主部首]。数据来源见 README v6 */\n'
js+='window.PCW_BUSHOU='+json.dumps(dict(tiers=TIERN,levels=[[L['t'],L['q']] for L in out_levels]),ensure_ascii=False,separators=(',',':'))+';\n'
open('../data/bushou.js','w').write(js)
print('bytes',len(js.encode()))
