import asyncio, edge_tts, edge_tts.communicate as C, sys
_esc=C.escape
def raw_escape(s):  # let our phoneme markup through
    return s
async def say_phoneme(ch, sapi, path, voice="zh-CN-XiaoxiaoNeural", rate="-10%"):
    C.escape=raw_escape
    try:
        txt='<phoneme alphabet="sapi" ph="%s">%s</phoneme>'%(sapi,ch)
        await edge_tts.Communicate(txt,voice,rate=rate).save(path)
    finally:
        C.escape=_esc
if __name__=='__main__':
    async def m():
        await say_phoneme('长','chang 2','/tmp/ref/ph_chang2.mp3')
        await say_phoneme('长','zhang 3','/tmp/ref/ph_zhang3.mp3')
        await say_phoneme('乐','yue 4','/tmp/ref/ph_yue4.mp3')
        await say_phoneme('乐','le 4','/tmp/ref/ph_le4.mp3')
    asyncio.run(m())
