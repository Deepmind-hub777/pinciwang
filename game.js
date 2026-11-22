/* 天天拼词王 · 网页复刻版 v4 —— 字中找字（主园 + 后花园） */
(function(){
"use strict";
var KEY="pinciwang.v1";
var HINT_COST=30, FIND_COIN=2, CLEAR_COIN=20, GIFT_COIN=60, GIFT_MS=4*3600*1000;
var IDX=window.PCW_INDEX; /* {main:[[n,t,count,strokes]...], bonus:[...]} */
var GNAME={main:"主园",bonus:"后花园"};
function blank(){return {found:{},hints:{},miss:{},cleared:{},stars:{},coins:100,gift:Date.now(),cur:0};}
var S={v:3,g:"main",sound:true,music:true,musicVol:0.22,voice:true,reveal:false,G:{main:blank(),bonus:blank()}};
function load(){
  try{var r=localStorage.getItem(KEY);if(r){var p=JSON.parse(r);
    if(p.v===3){ for(var k in p) S[k]=p[k]; S.G.main=S.G.main||blank(); S.G.bonus=S.G.bonus||blank(); }
    else { /* v1/v2 存档迁移到主园 */
      var m=blank(); ["found","hints","miss","cleared","stars","coins","gift","cur"].forEach(function(k){ if(p[k]!=null) m[k]=p[k]; });
      S.G.main=m; ["sound","music","musicVol"].forEach(function(k){ if(p[k]!=null) S[k]=p[k]; });
    }}}catch(e){}
}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}}
function D(){return S.G[S.g];}
/* ---------- sound ---------- */
/* 预生成音频：audio/sfx 音效、audio/vo 语音、audio/zi 单字读音（按关懒加载）。
   首次点击时解锁 AudioContext（iOS/Android 要求用户手势）。文件缺失时退回 speechSynthesis。 */
var AU=(function(){
  var ctx=null, buf={}, pend={}, bgmSrc=null, bgmGain=null, voiceSrc=null, unlocked=false, queue=Promise.resolve();
  var SFX=["tap","untap","click","correct","wrong","dup","hint","coin","clear","gift","start"];
  var VO={"小试牛刀":"xiaoshiniudao","渐入佳境":"jianrujiajing","炉火纯青":"luhuochunqing","登峰造极":"dengfengzaoji",
    "无懈可击":"wuxiekeji","游刃有余":"yourenyouyu","略有小成":"lueyouxiaocheng","勉强过关":"mianqiangguoguan",
    "太棒了":"taibangle","真厉害":"zhenlihai","好眼力":"haoyanli","恭喜过关":"gongxiguoguan","再想想":"zaixiangxiang",
    "这个字已经找到过了":"yizhaodao","加油":"jiayou"};
  function mk(){ if(ctx) return ctx; var C=window.AudioContext||window.webkitAudioContext; if(!C) return null;
    ctx=new C(); return ctx; }
  function load(url){
    if(buf[url]) return Promise.resolve(buf[url]);
    if(pend[url]) return pend[url];
    if(!mk()) return Promise.reject(new Error("no audio"));
    pend[url]=fetch(url).then(function(r){ if(!r.ok) throw new Error("404 "+url); return r.arrayBuffer(); })
      .then(function(ab){ return new Promise(function(res,rej){ ctx.decodeAudioData(ab,res,rej); }); })
      .then(function(b){ buf[url]=b; delete pend[url]; return b; })
      .catch(function(e){ delete pend[url]; throw e; });
    return pend[url];
  }
  function playBuf(b,gain,loop){
    var src=ctx.createBufferSource(), g=ctx.createGain(); src.buffer=b; src.loop=!!loop; g.gain.value=gain==null?1:gain;
    src.connect(g); g.connect(ctx.destination); src.start(0); return {src:src,g:g};
  }
  function unlock(){
    if(unlocked) return; if(!mk()) return;
    try{ var b=ctx.createBuffer(1,1,22050); var s=ctx.createBufferSource(); s.buffer=b; s.connect(ctx.destination); s.start(0); }catch(e){}
    if(ctx.resume) ctx.resume();
    unlocked=true;
    SFX.forEach(function(n){ load("audio/sfx/"+n+".mp3").catch(function(){}); });
    Object.keys(VO).forEach(function(k){ load("audio/vo/"+VO[k]+".mp3").catch(function(){}); });
    if(S.music) startBgm();
  }
  ["pointerdown","touchend","mousedown","keydown"].forEach(function(ev){ document.addEventListener(ev,unlock,{capture:true,passive:true}); });
  function sfx(name,gain){
    if(!S.sound||!ctx) return;
    load("audio/sfx/"+name+".mp3").then(function(b){ playBuf(b,gain==null?0.8:gain); }).catch(function(){});
  }
  function tts(text){
    try{ if(!window.speechSynthesis) return; var u=new SpeechSynthesisUtterance(text); u.lang="zh-CN"; u.rate=0.9;
      speechSynthesis.cancel(); speechSynthesis.speak(u);}catch(e){}
  }
  function voiceURL(url,fallbackText,delay){
    if(!S.sound) return Promise.resolve();
    if(!ctx){ tts(fallbackText); return Promise.resolve(); }
    return new Promise(function(res){
      setTimeout(function(){
        load(url).then(function(b){
          if(voiceSrc){ try{voiceSrc.stop();}catch(e){} }
          var p=playBuf(b,1); voiceSrc=p.src; p.src.onended=function(){res();};
          if(bgmGain){ bgmGain.gain.setTargetAtTime(0.06,ctx.currentTime,0.05); bgmGain.gain.setTargetAtTime(S.musicVol||0.22,ctx.currentTime+b.duration,0.3); }
        }).catch(function(){ tts(fallbackText); res(); });
      },delay||0);
    });
  }
  function line(text,delay){ var k=VO[text]; return voiceURL(k?"audio/vo/"+k+".mp3":"audio/vo/__none.mp3",text,delay); }
  function zi(a,delay){ return voiceURL("audio/"+a.au+".mp3",a.nm||a.c,delay); }
  function preloadLevel(L){ if(!ctx) return; L.a.forEach(function(a){ load("audio/"+a.au+".mp3").catch(function(){}); }); }
  function startBgm(){
    if(!ctx||bgmSrc||!S.music) return;
    load("audio/sfx/bgm.mp3").then(function(b){ if(bgmSrc||!S.music) return; var p=playBuf(b,0,true); bgmSrc=p.src; bgmGain=p.g;
      p.g.gain.setTargetAtTime(S.musicVol||0.22,ctx.currentTime,0.8); }).catch(function(){});
  }
  function stopBgm(){ if(bgmSrc){ try{bgmSrc.stop();}catch(e){} } bgmSrc=null; bgmGain=null; }
  document.addEventListener("visibilitychange",function(){ if(!ctx) return; if(document.hidden) ctx.suspend&&ctx.suspend(); else ctx.resume&&ctx.resume(); });
  return {sfx:sfx,line:line,zi:zi,preloadLevel:preloadLevel,startBgm:startBgm,stopBgm:stopBgm,unlock:unlock,
          _state:function(){return {ctx:ctx&&ctx.state,loaded:Object.keys(buf).length,bgm:!!bgmSrc};}};
})();
var sfx={
  tap:function(on){AU.sfx(on?"tap":"untap",0.7);},
  click:function(){AU.sfx("click",0.6);},
  ok:function(){AU.sfx("correct",0.8);},
  no:function(){AU.sfx("wrong",0.7);},
  dup:function(){AU.sfx("dup",0.8);},
  hint:function(){AU.sfx("hint",0.7);},
  coin:function(){AU.sfx("coin",0.7);},
  gift:function(){AU.sfx("gift",0.8);},
  start:function(){AU.sfx("start",0.6);},
  win:function(){AU.sfx("clear",0.9);}
};
/* ---------- helpers ---------- */
function $(id){return document.getElementById(id);}
function toast(msg){var el=$("toast");el.textContent=msg;el.classList.add("show");clearTimeout(el._t);
  el._t=setTimeout(function(){el.classList.remove("show");},1700);}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function list(){return IDX[S.g];}
function meta(i){var x=list()[i];return {n:x[0],t:x[1],cnt:x[2],sk:x[3]};}
function foundOf(n){var d=D();if(!d.found[n])d.found[n]=[];return d.found[n];}
function hintedOf(n){var d=D();if(!d.hints[n])d.hints[n]=[];return d.hints[n];}
function isCleared(i){return !!D().cleared[list()[i][0]];}
function unlocked(i){return i===0||isCleared(i-1)||isCleared(i);}
function firstOpen(){var L=list();for(var i=0;i<L.length;i++){if(!isCleared(i))return i;}return L.length-1;}
var TIERS=["小试牛刀","渐入佳境","炉火纯青","登峰造极","无懈可击"];
function tier(i,g){ g=g||S.g; var b=g==="bonus"?[10,30,60,80]:[30,120,300,600];
  for(var k=0;k<4;k++){ if(i<b[k]) return TIERS[k]; } return TIERS[4]; }
function unitWord(){return S.g==="bonus"?"个偏旁部件":"个常用字";}
function stats(g){var d=S.G[g],L=IDX[g],got=0,cl=0,stars=0;
  L.forEach(function(x){var f=d.found[x[0]];got+=f?Math.min(f.length,x[2]):0; if(d.cleared[x[0]])cl++; stars+=d.stars[x[0]]||0;});
  return {got:got,cl:cl,stars:stars,total:L.length};}
var GEAR='<svg viewBox="0 0 48 48"><defs><radialGradient id="gg" cx="40%" cy="35%"><stop offset="0" stop-color="#d9b98b"/><stop offset="1" stop-color="#8b6a43"/></radialGradient></defs>'+
  '<path d="M24 2c4 0 5 4 8 5s7-1 9 2-1 6 0 9 5 4 5 6-4 4-5 6 2 6 0 9-6 1-9 2-4 5-8 5-5-4-8-5-7 1-9-2 1-6 0-9-5-4-5-6 4-4 5-6-2-6 0-9 6-1 9-2 4-5 8-5z" fill="url(#gg)" stroke="#5e4428" stroke-width="1.5"/>'+
  '<circle cx="24" cy="24" r="11" fill="#f6ead2" stroke="#5e4428" stroke-width="1.5"/>'+
  '<path d="M24 16.5l1.6 2.3 2.8-.4.6 2.7 2.5 1.3-1.2 2.6 1.2 2.6-2.5 1.3-.6 2.7-2.8-.4L24 33.5l-1.6-2.3-2.8.4-.6-2.7-2.5-1.3 1.2-2.6-1.2-2.6 2.5-1.3.6-2.7 2.8.4z" fill="#8b6a43"/><circle cx="24" cy="25" r="3" fill="#f6ead2"/></svg>';
function coinHTML(){return '<span class="coin" id="coin"><i>¥</i><span id="coinv">'+D().coins+'</span></span>';}
function refreshCoin(){var e=$("coinv");if(e)e.textContent=D().coins;}

/* ---------- 关卡数据：按 50 关一包懒加载 ---------- */
var CH={main:{},bonus:{}}, CHUNK=50, waiting={};
window.PCW_CHUNK=function(g,start,levels){ levels.forEach(function(L,k){ CH[g][start+k]=L; });
  var key=g+start; if(waiting[key]){ waiting[key].forEach(function(f){f();}); delete waiting[key]; } };
function getLevel(g,i){
  if(CH[g][i]) return Promise.resolve(CH[g][i]);
  var start=Math.floor(i/CHUNK)*CHUNK, key=g+start;
  return new Promise(function(res,rej){
    var first=!waiting[key]; (waiting[key]=waiting[key]||[]).push(function(){res(CH[g][i]);});
    if(first){ var sc=document.createElement("script"); sc.src="data/"+g+"-"+String(start/CHUNK).padStart(2,"0")+".js?v=4";
      sc.onerror=function(){ delete waiting[key]; rej(new Error("关卡数据加载失败")); }; document.body.appendChild(sc); }
  });
}
/* ---------- home ---------- */
function renderHome(){
  stopTimer();
  var nx=firstOpen(), L=list(), allDone=L.every(function(_,i){return isCleared(i);}), sm=stats(S.g);
  var giftReady=D().gift+GIFT_MS<=Date.now();
  var h='<div class="home"><div class="topline"><span class="mus'+(S.music?" on":"")+'" id="mus" title="背景音乐">♪</span>'+coinHTML()+'</div>'+
    '<div class="logo"><div class="ink-blob"></div><h1>天天拼词王</h1><div class="seal">字中找字</div></div>'+
    '<div class="slogan">一字拆出千万意</div>'+
    '<div class="gtabs">'+["main","bonus"].map(function(g){return '<div class="gtab'+(S.g===g?" on":"")+'" data-g="'+g+'">'+GNAME[g]+'<small>'+IDX[g].length+' 关</small></div>';}).join("")+'</div>'+
    '<div class="gdesc">'+(S.g==="main"?"从汉字里描出藏着的<b>常用字</b>":"从汉字里描出<b>偏旁部件</b>，点一下能听名称")+' · 金币与进度各自独立</div>'+
    '<div class="stats"><div><b>'+sm.got+'</b><span>已得字</span></div><div><b>'+sm.cl+'/'+sm.total+'</b><span>通关</span></div><div><b>'+sm.stars+'</b><span>星</span></div></div>'+
    '<div class="menu">'+
      (giftReady?'<div class="bigbtn red" id="hgift">领取每日礼包<small>金币 +'+GIFT_COIN+'</small></div>':'')+
      '<div class="bigbtn" id="start">'+(allDone?"再玩一遍":"继续游戏")+'<small>'+GNAME[S.g]+' 第 '+meta(nx).n+' 关 · '+tier(nx)+'</small></div>'+
      '<div class="bigbtn green" id="pick">选择关卡</div>'+
    '</div>'+
    '<div class="howto"><b>玩法说明</b><br>每关给出一个汉字（或一句话），字里藏着若干<b>'+(S.g==="main"?"常用字":"偏旁部件")+'</b>。<br>'+
    '点选或划过笔画把它们<b>描黑</b>，拼成一个就点「提交」；点已找到的字能听读音。<br>找齐即可过关；卡住时用「提示」（'+HINT_COST+' 金币）。</div>'+
    '</div>';
  $("app").innerHTML=h;
  $("start").onclick=function(){sfx.click();renderLevel(nx);};
  $("pick").onclick=function(){openPicker();};
  if($("hgift")) $("hgift").onclick=function(){claimGift();renderHome();};
  document.querySelectorAll(".gtab").forEach(function(el){el.onclick=function(){var g=el.getAttribute("data-g");if(g!==S.g){S.g=g;save();sfx.click();renderHome();}};});
  $("mus").onclick=function(){S.music=!S.music;save();this.classList.toggle("on",S.music);AU.unlock();if(S.music)AU.startBgm();else AU.stopBgm();toast(S.music?"背景音乐：开":"背景音乐：关");};
}
/* ---------- play ---------- */
var st={idx:0,L:null,svg:null,geoms:[],sel:new Set(),down:false,moved:false,mode:true,sx:0,sy:0,timer:null,token:0};
function layout(k){ // returns [cols,rows,positions]
  var rows=k<=3?1:2, perRow=k<=3?k:Math.ceil(k/2);
  if(k===3){rows=1;perRow=3;}
  var pos=[],idx=0;
  for(var r=0;r<rows;r++){var n=Math.min(perRow,k-idx);var off=(perRow-n)/2;
    for(var c=0;c<n;c++){pos.push([off+c,r]);idx++;}}
  return [perRow,rows,pos];
}

function renderLevel(i){
  var tok=++st.token;
  $("app").innerHTML='<div class="loading">正在载入第 '+meta(i).n+' 关…</div>';
  getLevel(S.g,i).then(function(L){ if(tok===st.token) drawLevel(i,L); })
    .catch(function(e){ toast(e.message||"载入失败"); renderHome(); });
  // 预取下一包
  var nxt=i+1; if(nxt<list().length && nxt%CHUNK===0) getLevel(S.g,nxt).catch(function(){});
}
function drawLevel(i,L){
  st.idx=i; st.L=L; st.sel=new Set(); D().cur=i; pruneSave(L); save();
  var lay=layout(L.ch.length), cols=lay[0], rows=lay[1];
  var CELL=1024, pad=40, W=cols*CELL, H=rows*CELL;
  var svg='<svg id="board" viewBox="'+(-pad)+' '+(-pad)+' '+(W+2*pad)+' '+(H+2*pad)+'" xmlns="http://www.w3.org/2000/svg">';
  var gi=0;
  L.ch.forEach(function(c,ci){
    var p=lay[2][ci], sc=cols>1?0.94:1, ox=p[0]*CELL+CELL*(1-sc)/2, oy=p[1]*CELL+CELL*(1-sc)/2;
    svg+='<g class="cg" transform="translate('+ox+' '+(oy+900*sc)+') scale('+sc+' '+(-sc)+')">';
    c.st.forEach(function(d){svg+='<path class="st" data-i="'+gi+'" d="'+d+'"/>';gi++;});
    svg+='</g>';
  });
  svg+='</svg>';
  var h='<div class="hdr"><div class="gear" id="gear">'+GEAR+'</div>'+
        '<div class="gift" id="gift"><div class="box">🎁</div><div class="cd" id="cd">--:--:--</div></div>'+
        '<div class="titlebox"><div class="lvl">'+(S.g==="bonus"?'<span class="gtag">后花园</span>':'')+'第'+L.n+'关</div><div class="goal">找出<b>'+L.a.length+'</b>'+unitWord()+'</div></div></div>'+
        coinHTML().replace('class="coin"','class="coin" style="position:absolute;right:14px;top:14px"')+
        '<div class="slots kai'+(S.g==="bonus"?" bonus":"")+'" id="slots"></div>'+
        '<div class="stage">'+svg+'</div>'+
        '<div class="tip" id="tip"></div>'+
        '<div class="acts"><div class="btn" id="hint">提示<span class="cost">-'+HINT_COST+'</span></div>'+
        '<div class="btn" id="clear">清空</div><div class="btn primary off" id="submit">提交</div></div>';
  $("app").innerHTML=h;
  $("board").style.height=(Math.min(window.innerWidth*0.86,360)*(H+2*pad)/(W+2*pad))+"px";
  $("gear").onclick=openSettings;
  $("gift").onclick=claimGift;
  $("clear").onclick=function(){st.sel.clear();paint();sfx.click();};
  $("hint").onclick=useHint;
  $("submit").onclick=submit;
  buildGeom(); renderSlots(); paint(); bindPointer(); startTimer();
  st.streak=0; st.wrongRun=0; AU.preloadLevel(L); sfx.start(); AU.line(tier(i),350);
}
/* 存档兼容：答案表更新后，去掉已不在本关答案里的旧记录；已通关与星级保持不变 */
function pruneSave(L){
  var ok={}; L.a.forEach(function(a){ok[a.c]=1;}); var d=D();
  ["found","hints"].forEach(function(k){ var f=d[k][L.n]; if(f){ var g=f.filter(function(c,j){return ok[c]&&f.indexOf(c)===j;}); if(g.length!==f.length) d[k][L.n]=g; } });
}
function buildGeom(){
  st.svg=$("board"); st.geoms=[];
  st.svg.querySelectorAll("path.st").forEach(function(p){
    var len=p.getTotalLength(), n=40, pts=[];
    for(var k=0;k<=n;k++){var q=p.getPointAtLength(len*k/n);pts.push([q.x,q.y]);}
    st.geoms.push({el:p,i:+p.getAttribute("data-i"),pts:pts,g:p.parentNode});
  });
}
function renderSlots(newc){
  var L=st.L, f=foundOf(L.n), hs=hintedOf(L.n), h="", bonus=S.g==="bonus";
  var main={}; L.ch.forEach(function(c){main[c.c]=1;});
  L.a.forEach(function(a){
    var on=f.indexOf(a.c)>=0, hi=hs.indexOf(a.c)>=0, lab=bonus?a.nm:a.py;
    h+='<div class="slot'+(a.c===newc?" new":"")+(main[a.c]?" main":"")+'"><div class="py'+(hi&&!on?" hinted":"")+'">'+(on||hi?esc(lab):"")+'</div>'+
       '<div class="cell">'+(on?'<span>'+esc(a.c)+'</span>':"")+'</div></div>';
  });
  $("slots").innerHTML=h;
  $("slots").querySelectorAll(".slot").forEach(function(el,k){
    var a=L.a[k]; if(f.indexOf(a.c)<0) return;
    el.classList.add("speak"); el.title="点击朗读";
    el.onclick=function(){ el.classList.remove("say"); void el.offsetWidth; el.classList.add("say"); AU.zi(a,0); };
  });
}
function paint(){
  st.geoms.forEach(function(g){
    var on=st.sel.has(g.i);
    g.el.setAttribute("fill",on?"#2a2119":(g.hover?"#b38f60":"#c6a476"));
  });
  var L=st.L, need=L.a.length-foundOf(L.n).length;
  $("tip").innerHTML=st.sel.size?'已描黑 <b>'+st.sel.size+'</b> 笔 · 还差 <b>'+need+'</b> 个'
    :(need?(foundOf(L.n).length?'点选或划过笔画描黑后「提交」 · 点已找到的字可听读音':'点选或划过笔画，把字描黑后点「提交」'):'本关已全部找齐 · 点字可听读音');
  $("submit").classList.toggle("off",st.sel.size===0);
}
function local(g,cx,cy){var p=st.svg.createSVGPoint();p.x=cx;p.y=cy;return p.matrixTransform(g.getScreenCTM().inverse());}
function inside(g,cx,cy){
  var q=local(g.g,cx,cy);
  try{ if(g.el.isPointInFill(new DOMPoint(q.x,q.y))) return 0; }catch(e){}
  var best=Infinity; for(var k=0;k<g.pts.length;k++){var dx=g.pts[k][0]-q.x,dy=g.pts[k][1]-q.y;var d=dx*dx+dy*dy;if(d<best)best=d;}
  return Math.sqrt(best);
}
function edgeDist(g,cx,cy){var q=local(g.g,cx,cy),best=Infinity;
  for(var k=0;k<g.pts.length;k++){var dx=g.pts[k][0]-q.x,dy=g.pts[k][1]-q.y;var d=dx*dx+dy*dy;if(d<best)best=d;}return Math.sqrt(best);}
function nearest(cx,cy,maxD){var bi=null,bd=maxD,inner=null,depth=-1;
  st.geoms.forEach(function(g){var d=inside(g,cx,cy);
    if(d===0){var e=edgeDist(g,cx,cy);if(e>depth){depth=e;inner=g;}}
    else if(d<bd){bd=d;bi=g;}});
  return inner||bi;}
function setStroke(i,on){
  st.geoms.forEach(function(g){g.hint=false;});
  if(on&&!st.sel.has(i)){st.sel.add(i);sfx.tap(true);paint();}
  else if(!on&&st.sel.has(i)){st.sel.delete(i);sfx.tap(false);paint();}
}
function bindPointer(){
  var svg=st.svg;
  svg.addEventListener("pointerdown",function(e){
    e.preventDefault(); try{svg.setPointerCapture(e.pointerId);}catch(_){}
    st.down=true;st.moved=false;st.sx=e.clientX;st.sy=e.clientY;
    var nb=nearest(e.clientX,e.clientY,36); st.mode=nb?!st.sel.has(nb.i):true;
  });
  svg.addEventListener("pointermove",function(e){
    if(!st.down){ if(e.pointerType!=="mouse") return; var hv=nearest(e.clientX,e.clientY,30);
      var ch=false; st.geoms.forEach(function(g){var v=!!(hv&&g===hv); if(g.hover!==v){g.hover=v;ch=true;}}); if(ch) paint(); return; }
    if(!st.moved&&Math.hypot(e.clientX-st.sx,e.clientY-st.sy)>8){
      st.moved=true; var f=nearest(st.sx,st.sy,24); if(f) setStroke(f.i,st.mode);
    }
    if(st.moved){ st.geoms.forEach(function(g){ if(inside(g,e.clientX,e.clientY)===0) setStroke(g.i,st.mode); }); }
  });
  svg.addEventListener("pointerup",function(e){
    if(!st.down) return; st.down=false;
    if(!st.moved){var nb=nearest(e.clientX,e.clientY,36); if(nb) setStroke(nb.i,!st.sel.has(nb.i));}
  });
  svg.addEventListener("pointercancel",function(){st.down=false;});
  svg.addEventListener("pointerleave",function(){ var ch=false; st.geoms.forEach(function(g){ if(g.hover){g.hover=false;ch=true;} }); if(ch) paint(); });
}

/* ---------- judge ---------- */
function same(set,arr){if(set.size!==arr.length)return false;for(var k=0;k<arr.length;k++)if(!set.has(arr[k]))return false;return true;}
function submit(){
  if(st.sel.size===0){toast("先描黑几笔再提交");sfx.no();return;}
  var L=st.L, f=foundOf(L.n), hit=null, dup=false;
  L.a.forEach(function(a){ a.k.forEach(function(c){ if(same(st.sel,c)){ if(f.indexOf(a.c)>=0) dup=true; else if(!hit) hit=a; } }); });
  if(hit){
    f.push(hit.c); D().coins+=FIND_COIN; save();
    sfx.ok(); toast("找到「"+hit.c+"」"+(S.g==="bonus"?" "+hit.nm:"")+"！金币 +"+FIND_COIN);
    st.streak=(st.streak||0)+1; st.wrongRun=0;
    var last=L.a.every(function(a){return f.indexOf(a.c)>=0;});
    (S.voice?AU.zi(hit,380):Promise.resolve()).then(function(){ if(!last&&st.streak%3===0){ AU.line(["好眼力","真厉害","太棒了"][(st.streak/3-1)%3],120); } });
    flash(Array.from(st.sel));
    st.sel.clear(); paint(); renderSlots(hit.c); refreshCoin();
    if(last) setTimeout(function(){sfx.win();openWin();},S.voice?1100:700);
    return;
  }
  D().miss[L.n]=(D().miss[L.n]||0)+1; save();
  toast(dup?"这个已经找到过了":"这组笔画拼不出隐藏字，换个组合试试");
  st.streak=0;
  if(dup){ sfx.dup(); AU.line("这个字已经找到过了",250); }
  else { sfx.no(); st.wrongRun=(st.wrongRun||0)+1; if(st.wrongRun%3===0) AU.line("再想想",350); }
  shake();
}
function flash(ids){
  st.geoms.forEach(function(g){ if(ids.indexOf(g.i)>=0){ g.el.setAttribute("fill","#c8402f"); } });
  setTimeout(function(){paint();},520);
}
function shake(){
  var b=st.svg, n=0; var iv=setInterval(function(){n++;b.style.transform="translateX("+(n%2?6:-6)+"px)";
    if(n>5){clearInterval(iv);b.style.transform="";}},45);
}
function useHint(){
  var L=st.L, f=foundOf(L.n), hs=hintedOf(L.n);
  var unf=L.a.filter(function(a){return f.indexOf(a.c)<0;});
  if(!unf.length){toast("本关已全部找齐");return;}
  if(D().coins<HINT_COST){toast("金币不足 "+HINT_COST+"，领取礼包或多找几个字吧");sfx.no();return;}
  var target=unf.filter(function(a){return hs.indexOf(a.c)<0;})[0]||unf[0];
  D().coins-=HINT_COST; if(hs.indexOf(target.c)<0) hs.push(target.c); save(); refreshCoin(); sfx.hint(); setTimeout(sfx.coin,250);
  st.sel=new Set(target.k[0]);
  paint(); renderSlots();
  toast("已帮你描黑一个（"+(S.g==="bonus"?target.nm:target.py)+"），直接提交即可");
}

/* ---------- win ---------- */
function rateOf(L){
  var h=hintedOf(L.n).length, m=D().miss[L.n]||0;
  if(h===0&&m<=3) return [3,"无懈可击"];
  if(h<=1&&m<=8) return [2,"游刃有余"];
  if(h<=3) return [1,"略有小成"];
  return [1,"勉强过关"];
}
function openWin(){
  var L=st.L, d=D(), first=!d.cleared[L.n], r=rateOf(L);
  if(first){d.cleared[L.n]=1;d.coins+=CLEAR_COIN;}
  d.stars[L.n]=Math.max(d.stars[L.n]||0,r[0]); save(); refreshCoin();
  var strokes=L.ch.reduce(function(s,c){return s+c.st.length;},0);
  var stars=""; for(var k=0;k<3;k++) stars+='<span class="'+(k<r[0]?"on":"")+'">★</span>';
  var m=$("mask");
  m.innerHTML='<div class="card"><div class="ribbon">恭喜过关</div>'+
    '<div class="big kai">'+esc(L.t)+'</div><div class="meta">'+GNAME[S.g]+' 第 '+L.n+' 关 · 共 '+strokes+' 笔 · '+L.a.length+' 个</div>'+
    '<div class="stars">'+stars+'</div><div class="rank">'+r[1]+'</div>'+
    '<div class="found kai">共找出 '+L.a.length+' 个：<br><b>'+L.a.map(function(a){return '<i class="say1" data-c="'+esc(a.c)+'">'+esc(a.c)+'</i>';}).join("　")+'</b></div>'+
    '<div class="reward">'+(first?'过关奖励：金币 +'+CLEAR_COIN+' · ':'')+'提示 '+hintedOf(L.n).length+' 次 · 失误 '+(d.miss[L.n]||0)+' 次</div>'+
    '<div class="acts"><div class="btn" id="rh">返回首页</div><div class="btn primary" id="rn">下一关</div></div></div>';
  m.classList.add("open");
  m.querySelectorAll(".say1").forEach(function(el){ el.onclick=function(){ var c=el.getAttribute("data-c"); var a=L.a.filter(function(x){return x.c===c;})[0]; if(a) AU.zi(a,0); }; });
  AU.line("恭喜过关",900).then(function(){ AU.line(r[1],150); });
  $("rh").onclick=function(){sfx.click();m.classList.remove("open");renderHome();};
  $("rn").onclick=function(){sfx.click();m.classList.remove("open");renderLevel((st.idx+1)%list().length);};
}

/* ---------- gift / timer ---------- */
function fmt(ms){var s=Math.max(0,Math.ceil(ms/1000));var h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;
  return [h,m,x].map(function(v){return String(v).padStart(2,"0");}).join(":");}
function tick(){var el=$("cd"),g=$("gift");if(!el)return;var left=D().gift+GIFT_MS-Date.now();
  if(left<=0){el.textContent="可领取";g.classList.add("ready");}else{el.textContent=fmt(left);g.classList.remove("ready");}}
function startTimer(){stopTimer();tick();st.timer=setInterval(tick,1000);}
function stopTimer(){if(st.timer)clearInterval(st.timer);st.timer=null;}
function claimGift(){
  var left=D().gift+GIFT_MS-Date.now();
  if(left>0){toast("礼包还在准备中，"+fmt(left)+" 后可领取");return;}
  D().gift=Date.now();D().coins+=GIFT_COIN;save();refreshCoin();tick();sfx.gift();setTimeout(sfx.coin,500);
  toast("领取每日礼包：金币 +"+GIFT_COIN);
}
/* ---------- settings / picker ---------- */
function sw(id,on,label,sub){return '<div class="setrow"><div><div>'+label+'</div>'+(sub?'<div class="sub">'+sub+'</div>':'')+'</div><div class="switch'+(on?" on":"")+'" id="'+id+'"></div></div>';}
function openSettings(){
  sfx.click();
  var m=$("mask"), sm=stats(S.g);
  m.innerHTML='<div class="card"><h3>设置</h3>'+
    sw("sw",S.sound,"音效与语音","答对、答错、评价等声音")+
    sw("swm",S.music,"背景音乐","古筝轻音乐")+
    sw("swv",S.voice,"找到时朗读","找到一个字后自动读一遍")+
    sw("swr",S.reveal,"明牌","选关时直接显示未通关的母字")+
    '<div class="setrow"><span>'+GNAME[S.g]+' · 金币 / 通关 / 星</span><b style="color:var(--bronze)">'+D().coins+' / '+sm.cl+' / '+sm.stars+'</b></div>'+
    '<div class="note">主园与后花园的金币、进度、星级各自独立。提示 '+HINT_COST+' · 找到 +'+FIND_COIN+' · 通关 +'+CLEAR_COIN+' · 礼包 '+GIFT_COIN+' / 4 小时</div>'+
    '<div class="acts"><div class="btn" id="sh">返回首页</div><div class="btn" id="sp">选择关卡</div></div>'+
    '<div class="acts"><div class="btn" id="sr" style="font-size:13px;color:#a0503c">重置进度</div><div class="btn primary" id="sc">继续游戏</div></div></div>';
  m.classList.add("open");
  $("sw").onclick=function(){S.sound=!S.sound;save();this.classList.toggle("on",S.sound);sfx.click();};
  $("swm").onclick=function(){S.music=!S.music;save();this.classList.toggle("on",S.music);if(S.music)AU.startBgm();else AU.stopBgm();};
  $("swv").onclick=function(){S.voice=!S.voice;save();this.classList.toggle("on",S.voice);};
  $("swr").onclick=function(){S.reveal=!S.reveal;save();this.classList.toggle("on",S.reveal);};
  $("sh").onclick=function(){m.classList.remove("open");renderHome();};
  $("sp").onclick=function(){openPicker();};
  $("sc").onclick=function(){m.classList.remove("open");};
  $("sr").onclick=function(){ if(confirm("确定清空"+GNAME[S.g]+"的全部进度和金币？")){ S.G[S.g]=blank(); save(); location.reload(); } };
}
function openPicker(){
  sfx.click();
  var m=$("mask"), L=list(), d=D(), h='<div class="picker"><div class="h"><b>'+GNAME[S.g]+' · 选关</b><span class="x" id="px">✕</span></div>';
  TIERS.forEach(function(t){
    var items=L.map(function(_,i){return i;}).filter(function(i){return tier(i)===t;});
    if(!items.length) return;
    var done=items.filter(isCleared).length;
    h+='<div class="sec">'+t+'<em>'+done+'/'+items.length+'</em></div><div class="prow">';
    items.forEach(function(i){var x=L[i],lk=!unlocked(i),cl=isCleared(i),s=d.stars[x[0]]||0;
      var show=cl||S.reveal;
      h+='<div class="pitem'+(cl?" done":"")+(lk?" lock":"")+(i===d.cur?" cur":"")+(x[1].length>1&&show?" long":"")+'" data-i="'+i+'">'+
        '<span class="c kai">'+(lk&&!S.reveal?"🔒":(show?esc(x[1]):"？"))+'</span><span>'+x[0]+'</span>'+
        (cl?'<span class="ps">'+"★★★".slice(0,s)+'</span>':'')+'</div>';});
    h+='</div>';
  });
  h+='</div>';
  m.innerHTML=h; m.classList.add("open");
  $("px").onclick=function(){m.classList.remove("open");};
  m.querySelector(".picker").onclick=function(e){var el=e.target.closest(".pitem"); if(!el) return;
    var i=+el.getAttribute("data-i"); if(!unlocked(i)){toast("先通过第 "+L[i-1][0]+" 关才能解锁");sfx.no();return;}
    m.classList.remove("open"); renderLevel(i);};
  var cur=m.querySelector(".pitem.cur"); if(cur) cur.scrollIntoView({block:"center"});
}

load(); renderHome();
window.__pcw={AU:AU,S:S,st:st,IDX:IDX,getLevel:getLevel,renderLevel:renderLevel,submit:submit,useHint:useHint,renderHome:renderHome};
})();
