# 天天拼词王 · 网页复刻版（字中找字）

纯静态网页，直接打开 `index.html` 或任意静态服务器即可运行（移动端优先）。

- `index.html / style.css / game.js`：界面与玩法
- `levels.js`：130 关数据（关卡顺序参照《天天拼词王》公开攻略的关卡字；含"不对心""马上有钱"等多字关）
- `fonts/brush.woff2`：马善政毛笔字体子集（SIL OFL，见 fonts/OFL-MaShanZheng.txt）
- `build/gen.py, build/levels.py`：关卡生成脚本——笔画数据来自 Make Me a Hanzi（Arphic Public License），
  对《通用规范汉字表》一级字逐个做笔画几何匹配，找出母字里能"描"出来的常用字。
  重新生成：下载 makemeahanzi 的 graphics.txt / dictionary.txt 到 build/ 后运行 `python3 levels.py`。

存档保存在浏览器 localStorage（键 `pinciwang.v1`）。
