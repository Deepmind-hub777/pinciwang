"""书法字体子集：取现有子集已有的字 + game.js / index.html 里的全部汉字 + 后花园档位名，生成 ../fonts/callig.woff2"""
import re,json,subprocess
from fontTools.ttLib import TTFont
old=set(chr(c) for c in TTFont('../fonts/callig.woff2').getBestCmap())
txt=open('../game.js').read()+open('../index.html').read()+'常见部首少见部首易混部首后花园主园第关0123456789'
new=set(ch for ch in txt if '\u3400'<=ch<='\u9fff' or ch in '0123456789·（）')
chars=''.join(sorted(old|new))
open('/tmp/callig_chars.txt','w').write(chars)
subprocess.run(['pyftsubset','ZhiMangXing-Regular.ttf','--text-file=/tmp/callig_chars.txt','--flavor=woff2','--output-file=../fonts/callig.woff2','--layout-features=*'],check=True)
print('old',len(old),'new total',len(set(chars)))
