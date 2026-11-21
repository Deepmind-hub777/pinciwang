import json, asyncio, os, subprocess
import edge_tts
from pypinyin import pinyin, Style
from tts import pinyin_to_num
VOICE="zh-CN-XiaoxiaoNeural"
L=json.load(open('main_levels.json'))
pairs=sorted({(a['c'],a['py'],a['au']) for l in L for a in l['a']})
ALL=[c.strip() for c in open('level-1.txt',encoding='utf8') if c.strip()]+[c.strip() for c in open('level-2.txt',encoding='utf8') if c.strip()]
d=lambda c: pinyin(c,style=Style.TONE)[0][0]
het=lambda c: pinyin(c,style=Style.TONE,heteronym=True)[0]
OV=json.load(open('tts_override.json'))
for c,py,au in pairs:
    if c in OV: continue
    if not os.path.exists('../audio/'+au+'.mp3') and (len(het(c))>1 or d(c)!=py):
        cand=[v for v in ALL if v!=c and len(het(v))==1 and d(v)==py]
        if cand: OV[c]=cand[0]
json.dump(OV,open('tts_override.json','w'),ensure_ascii=False)
async def synth(text,out,voice=VOICE,rate="-10%",br='32k'):
    tmp='/tmp/tts/'+os.path.basename(out)
    for k in range(6):
        try: await edge_tts.Communicate(text,voice,rate=rate).save(tmp); break
        except Exception: await asyncio.sleep(3)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-af',
      'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.08',
      '-ac','1','-ar','24000','-b:a',br,out],check=True)
async def main():
    os.makedirs('/tmp/tts',exist_ok=True); os.makedirs('../audio/bu',exist_ok=True)
    sem=asyncio.Semaphore(8)
    async def one(text,out,**kw):
        if os.path.exists(out): return
        async with sem: await synth(text,out,**kw)
    jobs=[one(OV.get(c,c),'../audio/'+au+'.mp3') for c,py,au in pairs]
    B=json.load(open('bonus_levels.json'))
    for l in B:
        for a in l['a']: jobs.append(one(a['nm'],'../audio/'+a['au']+'.mp3',rate="-5%"))
    await asyncio.gather(*jobs)
    print('done',len(pairs))
asyncio.run(main())
