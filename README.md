# 天天拼词王 · 网页复刻版（字中找字）

纯静态网页，直接打开 `index.html` 或任意静态服务器即可运行（移动端优先）。

- `index.html / style.css / game.js`：界面与玩法
- `levels.js`：130 关数据（关卡顺序参照《天天拼词王》公开攻略的关卡字；含"不对心""马上有钱"等多字关）
- `fonts/brush.woff2`：马善政毛笔字体子集（SIL OFL，见 fonts/OFL-MaShanZheng.txt）
- `build/gen.py, build/levels.py`：关卡生成脚本——笔画数据来自 Make Me a Hanzi（Arphic Public License），
  对《通用规范汉字表》一级字逐个做笔画几何匹配，找出母字里能"描"出来的常用字。
  重新生成：下载 makemeahanzi 的 graphics.txt / dictionary.txt 到 build/ 后运行 `python3 levels.py`。

存档保存在浏览器 localStorage（键 `pinciwang.v1`）。

## 声音（v2）
- `audio/sfx/`：程序合成的音效（选笔、取消、按钮、答对、答错、重复、提示、金币、礼包、开局、过关）和古筝风背景音乐 `bgm.mp3`（循环），由 `build/gen_sfx.py` 生成。
- `audio/vo/`：语音（小试牛刀/渐入佳境/炉火纯青/登峰造极/无懈可击/游刃有余/略有小成/勉强过关/恭喜过关/太棒了/真厉害/好眼力/再想想/这个字已经找到过了），edge-tts `zh-CN-XiaoyiNeural`。
- `audio/zi/`：405 个答案字的读音（`<码位>_<拼音声调>.mp3`），edge-tts `zh-CN-XiaoxiaoNeural`，按关懒加载；点击已找到的字即朗读。
  多音字：用同音单音字替读（`build/tts_override.json`），并用"同音字音频几乎完全相同"做比对验证（`build/verify4.py`）。
- 首次触摸时解锁 AudioContext（iOS/Android）；文件缺失时退回浏览器 speechSynthesis。设置里可分别开关「音效与语音」「背景音乐」。
