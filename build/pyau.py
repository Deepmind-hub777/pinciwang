import gen
from pypinyin import pinyin, Style
FIX={'肋':'lèi','茸':'róng','勒':'lè','了':'le','卓':'zhuó','只':'zhǐ','罗':'luó','卜':'bǔ','子':'zǐ'}
def py_of(c):
    if c in FIX: return FIX[c]
    mm=[p for p in (gen.D.get(c,{}).get('pinyin') or []) if any(ord(x)>127 for x in p)]
    d=pinyin(c,style=Style.TONE)[0][0]
    if d in mm or not mm: return d
    return mm[0]
from tts import pinyin_to_num
def au_of(c,py): return 'zi/%04x_%s'%(ord(c),pinyin_to_num(py))
