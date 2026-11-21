import json, asyncio, os, subprocess, sys
import edge_tts
from pypinyin import pinyin, Style
VOICE="zh-CN-XiaoxiaoNeural"
L=json.load(open('levels_out.json'))
pairs=sorted({(a['c'],a['py']) for l in L for a in l['a']})
def num(py):  # tone-mark -> ascii+number
    return pinyin_to_num(py)
TM={'ā':('a',1),'á':('a',2),'ǎ':('a',3),'à':('a',4),'ē':('e',1),'é':('e',2),'ě':('e',3),'è':('e',4),'ī':('i',1),'í':('i',2),'ǐ':('i',3),'ì':('i',4),
'ō':('o',1),'ó':('o',2),'ǒ':('o',3),'ò':('o',4),'ū':('u',1),'ú':('u',2),'ǔ':('u',3),'ù':('u',4),'ǖ':('v',1),'ǘ':('v',2),'ǚ':('v',3),'ǜ':('v',4),'ü':('v',0)}
def pinyin_to_num(py):
    t=5; out=''
    for ch in py:
        if ch in TM:
            b,tt=TM[ch]; out+=b
            if tt: t=tt
        else: out+=ch
    return out+str(t)
# homophone substitution: chars whose displayed reading is not their default single-char reading
VOC=[c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip()]
def default(c): return pinyin(c,style=Style.TONE)[0][0]
def mono(c): return len(pinyin(c,style=Style.TONE,heteronym=True)[0])==1
SUB={}
for c,py in pairs:
    if default(c)!=py:
        cand=[v for v in VOC if mono(v) and default(v)==py]
        SUB[c]=cand[0] if cand else None
OV=json.load(open('tts_override.json')) if os.path.exists('tts_override.json') else {}
SUB.update(OV)
os.makedirs('../audio/zi',exist_ok=True)
def fname(c,py): return '%04x_%s.mp3'%(ord(c),pinyin_to_num(py))
async def one(sem,c,py):
    out='../audio/zi/'+fname(c,py)
    if os.path.exists(out) and c not in OV: return
    text=SUB.get(c) or c
    tmp='/tmp/tts/'+fname(c,py)
    async with sem:
        for k in range(4):
            try:
                await edge_tts.Communicate(text,VOICE,rate="-10%").save(tmp); break
            except Exception as e: await asyncio.sleep(2)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-af',
      'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.08',
      '-ac','1','-ar','24000','-b:a','32k',out],check=True)
async def main():
    sem=asyncio.Semaphore(8)
    await asyncio.gather(*[one(sem,c,py) for c,py in pairs])
    # voice lines
    os.makedirs('../audio/vo',exist_ok=True)
    lines={'xiaoshiniudao':'小试牛刀！','jianrujiajing':'渐入佳境！','luhuochunqing':'炉火纯青！','dengfengzaoji':'登峰造极！',
      'wuxiekeji':'无懈可击！','yourenyouyu':'游刃有余！','lueyouxiaocheng':'略有小成！','mianqiangguoguan':'勉强过关！',
      'taibangle':'太棒了！','zhenlihai':'真厉害！','haoyanli':'好眼力！','gongxiguoguan':'恭喜过关！','zaixiangxiang':'再想想~','yizhaodao':'这个字已经找到过了','jiayou':'加油！'}
    for k,t in lines.items():
        tmp='/tmp/tts/vo_'+k+'.mp3'; out='../audio/vo/'+k+'.mp3'
        await edge_tts.Communicate(t,"zh-CN-XiaoyiNeural",rate="+0%").save(tmp)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
          '-ac','1','-ar','24000','-b:a','40k',out],check=True)
    # write map into levels
    for l in L:
        for a in l['a']: a['au']=fname(a['c'],a['py'])[:-4]
    json.dump(L,open('levels_out.json','w'),ensure_ascii=False,separators=(',',':'))
    json.dump({c:SUB[c] for c in SUB},open('tts_subs.json','w'),ensure_ascii=False,indent=0)
    print('subs',SUB)
if __name__=='__main__':
    asyncio.run(main())
