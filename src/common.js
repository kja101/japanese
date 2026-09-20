// Shared by every page: on/kun reading engine.
// Built from src/common.js + data/readings.json by build/build.py. Edit those, not assets/common.js.

// ---------- on/kun reading colours ----------
const RD = __READINGS__;
const RD_V={か:"が",き:"ぎ",く:"ぐ",け:"げ",こ:"ご",さ:"ざ",し:"じ",す:"ず",せ:"ぜ",そ:"ぞ",た:"だ",ち:"ぢ",つ:"づ",て:"で",と:"ど",は:"ば",ひ:"び",ふ:"ぶ",へ:"べ",ほ:"ぼ"};
const RD_H={は:"ぱ",ひ:"ぴ",ふ:"ぷ",へ:"ぺ",ほ:"ぽ"};
function rdVariants(r,first,last){
  let out=[[r,0]];
  if(!first){ const f=r[0], rest=r.slice(1);
    if(RD_V[f]) out.push([RD_V[f]+rest,1]); if(RD_H[f]) out.push([RD_H[f]+rest,1]);
    if(f==="ち") out.push(["じ"+rest,1]); if(f==="つ") out.push(["ず"+rest,1]); }
  if(!last){ const more=[]; out.forEach(([s,c])=>{ if(/[つちくき]$/.test(s)) more.push([s.length===1?s+"っ":s.slice(0,-1)+"っ",c+1]); }); out=out.concat(more); }
  return out;
}
const rdHira=s=>s.replace(/[\u30A1-\u30F6]/g,c=>String.fromCharCode(c.charCodeAt(0)-0x60));
function rdSeg(run,reading,vf){
  const ks=[...run], rd=rdHira(reading), n=ks.length, sols=[];
  const expect = n>=2 ? "on" : "kun";
  (function dfs(i,pos,acc,cost){
    if(sols.length>60) return;
    if(i===n){ if(pos===rd.length) sols.push({acc:acc.slice(),cost}); return; }
    let k=ks[i]; const key = k==="々" && i>0 ? ks[i-1] : k;
    const e=RD[key]; if(!e) return;
    const cands=[]; e[0].forEach(r=>cands.push([r,"on"])); e[1].forEach(r=>cands.push([r,"kun"]));
    for(const [r,t] of cands) for(const [s,c] of rdVariants(r,i===0&&!vf,i===n-1)){
      if(s && rd.startsWith(s,pos)){ acc.push({k,r:reading.slice(pos,pos+s.length),t,b:r}); dfs(i+1,pos+s.length,acc,cost+c+(t===expect?0:0.6)); acc.pop(); }
    }
  })(0,0,[],0);
  if(!sols.length) return null;
  sols.sort((a,b)=>a.cost-b.cost);
  return sols[0].acc;
}
function rdAlign(word,reading){
  const parts=word.match(/[\u4e00-\u9fff々]+|[^\u4e00-\u9fff々]+/g)||[];
  const esc2=s=>s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
  const re=new RegExp("^"+parts.map(p=>/[\u4e00-\u9fff]/.test(p)?"(.+?)":esc2(rdHira(p)))+"$".replace(/,/g,""));
  const m=rdHira(reading).match(new RegExp("^"+parts.map(p=>/[\u4e00-\u9fff]/.test(p)?"(.+?)":esc2(rdHira(p))).join("")+"$"));
  if(!m) return null;
  let g=1; return parts.map(p=>/[\u4e00-\u9fff]/.test(p)?{t:p,r:m[g++]}:{t:p,r:null});
}
const rdE=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function rdRuby(run,reading,vf){
  const s=rdSeg(run,reading,vf);
  if(!s) return `<ruby class="rd rd-sp"><span class="rb">${rdE(run)}</span><rt>${rdE(reading)}</rt></ruby>`;
  return s.map(x=>`<ruby class="rd rd-${x.t}"><span class="rb">${rdE(x.k)}</span><rt>${rdE(x.r)}</rt></ruby>`).join("");
}
function rdKanji(run,reading,vf){
  const s=rdSeg(run,reading,vf);
  if(!s) return `<span class="rd rd-sp">${rdE(run)}</span>`;
  return s.map(x=>`<span class="rd rd-${x.t}">${rdE(x.k)}</span>`).join("");
}
function rdKana(run,reading,vf){
  const s=rdSeg(run,reading,vf);
  if(!s) return `<span class="rd kana rd-sp">${rdE(reading)}</span>`;
  return s.map(x=>`<span class="rd kana rd-${x.t}">${rdE(x.r)}</span>`).join("");
}
// whole word (kanji + kana mixed) with a separate reading
function rdWord(word,reading,mode){
  const a=rdAlign(word,String(reading).replace(/ /g,""));
  if(!a) return mode==="kana"?rdE(reading):rdE(word);
  let seen=false; return a.map(p=>{ if(p.r==null) return rdE(p.t); const vf=seen; seen=true; return mode==="ruby"?rdRuby(p.t,p.r,vf):mode==="kana"?rdKana(p.t,p.r,vf):rdKanji(p.t,p.r,vf); }).join("");
}

function rdKanaU(run,reading){
  const s=rdSeg(run,reading);
  if(!s) return `<span class="rd rd-sp">${rdE(reading)}</span>`;
  return s.map(x=>`<span class="rd rd-${x.t}">${rdE(x.r)}</span>`).join("");
}
function rdWordU(word,reading){
  const a=rdAlign(word,String(reading).replace(/ /g,""));
  if(!a) return null;
  return a.map(p=>p.r==null?rdE(p.t):rdKanaU(p.t,p.r)).join("");
}
function rdTypeOf(word,reading,k){
  const a=rdAlign(word,String(reading).replace(/ /g,"")); if(!a) return null;
  for(const p of a){ if(p.r==null||!p.t.includes(k)) continue; const s=rdSeg(p.t,p.r); if(!s) return "sp"; const hit=s.find(x=>x.k===k); return hit?hit.t:null; }
  return null;
}

// ---------- romaji (Hepburn, long vowels written out) ----------
const KR_BASE={あ:"a",い:"i",う:"u",え:"e",お:"o",か:"ka",き:"ki",く:"ku",け:"ke",こ:"ko",さ:"sa",し:"shi",す:"su",せ:"se",そ:"so",た:"ta",ち:"chi",つ:"tsu",て:"te",と:"to",な:"na",に:"ni",ぬ:"nu",ね:"ne",の:"no",は:"ha",ひ:"hi",ふ:"fu",へ:"he",ほ:"ho",ま:"ma",み:"mi",む:"mu",め:"me",も:"mo",や:"ya",ゆ:"yu",よ:"yo",ら:"ra",り:"ri",る:"ru",れ:"re",ろ:"ro",わ:"wa",を:"o",ん:"n",が:"ga",ぎ:"gi",ぐ:"gu",げ:"ge",ご:"go",ざ:"za",じ:"ji",ず:"zu",ぜ:"ze",ぞ:"zo",だ:"da",ぢ:"ji",づ:"zu",で:"de",ど:"do",ば:"ba",び:"bi",ぶ:"bu",べ:"be",ぼ:"bo",ぱ:"pa",ぴ:"pi",ぷ:"pu",ぺ:"pe",ぽ:"po",ゔ:"vu","、":", ","。":". ","〜":"~","～":"~"};
const KR_SY={ゃ:"a",ゅ:"u",ょ:"o"}, KR_SV={ぁ:"a",ぃ:"i",ぅ:"u",ぇ:"e",ぉ:"o"};
function krRomaji(k){ const s=rdHira(k); let o="",i=0; while(i<s.length){ const c=s[i],n=s[i+1];
  if(c==="っ"){ const r=krRomaji(s.slice(i+1,i+3)); o+=r.startsWith("ch")?"t":(r[0]||""); i++; continue; }
  if(c==="ー"){ o+=o.slice(-1); i++; continue; }
  if(n&&KR_SY[n]&&KR_BASE[c]){ const b=KR_BASE[c]; o+=(["shi","chi","ji"].includes(b)?b.slice(0,-1):b.slice(0,-1)+"y")+KR_SY[n]; i+=2; continue; }
  if(n&&KR_SV[n]&&KR_BASE[c]){ const b=KR_BASE[c]; o+=(b==="fu"?"f":b==="u"?"w":b==="te"?"t":b==="de"?"d":b==="shi"?"sh":b==="chi"?"ch":b==="ji"?"j":b.slice(0,-1))+KR_SV[n]; i+=2; continue; }
  if(c==="ん"){ o+=(n&&/[あいうえおやゆよ]/.test(n))?"n'":"n"; i++; continue; }
  o+=KR_BASE[c]!==undefined?KR_BASE[c]:(KR_SV[c]||c); i++; } return o.trim(); }


// ---------- small helpers ----------
const jpEsc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

// ---------- shared progress: one spaced-repetition record for the study plan and the kanji deck ----------
const SRS_KEY="kanji-srs-v1";
function srsLoad(){ try{ return JSON.parse(localStorage.getItem(SRS_KEY)||"null")||{cards:{},day:{key:"",newDone:0},settings:{perDay:10,order:"shape",upto:4},log:{}}; }catch(e){ return {cards:{},day:{key:"",newDone:0},settings:{perDay:10,order:"shape",upto:4},log:{}}; } }
function srsSave(S){ try{ localStorage.setItem(SRS_KEY,JSON.stringify(S)); }catch(e){} }
function srsKnown(k){ const c=srsLoad().cards["m:"+k]; return !!(c&&c.step===-1); }
function srsKnownList(){ const S=srsLoad(); return Object.keys(S.cards).filter(id=>id.startsWith("m:")&&S.cards[id].step===-1).map(id=>id.slice(2)); }
function srsMarkKnown(k){ const S=srsLoad(); const id="m:"+k; if(!S.cards[id]||S.cards[id].step!==-1){ S.cards[id]={step:-1,due:Date.now()+4*864e5,ivl:4,ease:2.5,reps:1,lapses:0,rivl:0}; srsSave(S); } }
function srsUnmark(k){ const S=srsLoad(); delete S.cards["m:"+k]; delete S.cards["w:"+k]; srsSave(S); }
(function migrateKnown(){ try{ const old=JSON.parse(localStorage.getItem("heisig-known")||"null"); if(Array.isArray(old)&&old.length){ old.forEach(srsMarkKnown); } localStorage.removeItem("heisig-known"); }catch(e){} })();

// ---------- shared stories: written in the kanji deck or the study plan, shown in both ----------
const STORY_KEY="heisig-stories";
function storiesLoad(){ try{ return JSON.parse(localStorage.getItem(STORY_KEY)||"{}"); }catch(e){ return {}; } }
function storyGet(k){ return storiesLoad()[k]||""; }
function storySet(k,v){ const s=storiesLoad(); if(v) s[k]=v; else delete s[k]; try{ localStorage.setItem(STORY_KEY,JSON.stringify(s)); }catch(e){} }

// ---------- audio: the browser's own Japanese voice ----------
let jaVoiceCache=null;
function jaVoice(){ if(jaVoiceCache) return jaVoiceCache; if(!window.speechSynthesis) return null; const vs=speechSynthesis.getVoices().filter(v=>/^ja/i.test(v.lang));
  jaVoiceCache=vs.find(v=>/Kyoko|O-ren|Otoya|Google/i.test(v.name))||vs[0]||null; return jaVoiceCache; }
if(window.speechSynthesis) speechSynthesis.onvoiceschanged=()=>{ jaVoiceCache=null; jaVoice(); };
function speak(text){ if(!window.speechSynthesis||!text) return; speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(String(text).replace(/[＿_]+/g,"")); u.lang="ja-JP"; const v=jaVoice(); if(v) u.voice=v; u.rate=0.85; speechSynthesis.speak(u); }
function sayBtn(text){ return window.speechSynthesis&&text?`<button type="button" class="say" data-say="${jpEsc(text)}" aria-label="Play the Japanese" title="Play">`+`<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path fill="currentColor" d="M4 9v6h4l5 4V5L8 9H4zm12.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4z"/></svg></button>`:""; }
document.addEventListener("click",e=>{ const b=e.target.closest("[data-say]"); if(!b) return; e.preventDefault(); e.stopPropagation(); speak(b.dataset.say); b.classList.add("playing"); setTimeout(()=>b.classList.remove("playing"),900); },true);
(function(){ const st=document.createElement("style"); st.textContent=`.say{display:inline-grid;place-items:center;width:1.7em;height:1.7em;border-radius:50%;border:1px solid rgba(127,127,127,.35);background:transparent;color:inherit;opacity:.7;cursor:pointer;vertical-align:middle;margin:0 .25em;padding:0;font:inherit;line-height:1}.say:hover,.say:focus-visible{opacity:1}.say.playing{opacity:1;background:rgba(127,127,127,.15)}`; document.head.appendChild(st); })();

// ---------- particles: what each one does, shown when you tap it ----------
const PINFO={
 "は":["wa","Topic","Marks what the sentence is about: \"as for …\". Written は but said wa.","私は学生です: as for me, I'm a student."],
 "が":["ga","Subject","Picks out who or what does something, or is new information. Also used with 好き, 分かる, 欲しい and ある.","頭が痛いです: my head hurts."],
 "を":["o","Object","Marks the thing acted on by the verb. Written を, said o, and only ever a particle.","コーヒーを飲みます: I drink coffee."],
 "に":["ni","Time, destination or target","A point in time (七時に), where something goes or exists (日本に), or who receives something.","六時に会いましょう: let's meet at six."],
 "で":["de","Place of action, or means","Where an action happens (カフェで), or how it's done (電車で, カードで).","電車で行きます: I go by train."],
 "へ":["e","Direction","Towards a place. Written へ but said e. Close to に for destinations.","日本へ行きます: I'm going to Japan."],
 "と":["to","With, and, or a quote","With someone (友達と), and between nouns (パンと水), or before 思う and 言う to quote.","友達と行きます: I'll go with a friend."],
 "から":["kara","From, or because","Starting point in place or time, or a reason after a sentence.","駅から歩きます: I'll walk from the station."],
 "まで":["made","Until, as far as","The end point in place or time.","京都までお願いします: to Kyoto, please."],
 "の":["no","Of, 's","Joins two nouns: the first describes or owns the second.","私の家: my house."],
 "も":["mo","Also, too","Replaces は, が or を to add \"too\".","私も行きます: I'm going too."],
 "か":["ka","Question","Turns the sentence into a question. No question mark needed in Japanese.","駅はどこですか: where is the station?"],
 "ね":["ne","Isn't it?","Asks for agreement or softens a statement.","いい天気ですね: nice weather, isn't it?"],
 "よ":["yo","You know","Tells the listener something new, with emphasis.","おいしいですよ: it's delicious, you know."],
 "や":["ya","And (among others)","Lists examples, implying there are more.","パンや水: bread, water and so on."],
 "には":["ni wa","に + は","に with extra focus or contrast: \"as for at / in …\".",""],"では":["de wa","で + は","で with extra focus or contrast.",""],
 "にも":["ni mo","に + も","\"To … too\" or \"at … too\".",""],"でも":["de mo","で + も","\"At … too\", or \"even\".",""],"とは":["to wa","と + は","と with extra focus.",""],"へは":["e wa","へ + は","へ with extra focus.",""]
};
const ROLEHINT={W:"who or topic",T:"time",P:"place",H:"how or with",O:"what",V:"verb",Q:"question"};
const PEND=/(から|まで|には|では|へは|とは|にも|でも|は|が|を|に|で|へ|と|も|の|か|ね|よ|や)$/;
const isKK=c=>!!c&&/[\u4e00-\u9fff\u30a0-\u30ff々]/.test(c);
function jpChunkParts(k,kn,role){
  // parts: {t, r (reading or null), p (particle flag)}
  let a=/[\u4e00-\u9fff]/.test(k)?rdAlign(k,kn.replace(/ /g,"")):null;
  if(!a) a=[{t:k,r:null}];
  const out=[];
  a.forEach((p,idx)=>{
    if(p.r!=null){ out.push({t:p.t,r:p.r}); return; }
    const s=p.t; let buf="";
    for(let i=0;i<s.length;i++){
      const c=s[i], prev=i>0?s[i-1]:(idx>0?a[idx-1].t.slice(-1):""), next=i<s.length-1?s[i+1]:(idx<a.length-1?a[idx+1].t[0]:"");
      const before=(idx>0&&i===0?a[idx-1].t:"")+s.slice(0,i);
      let isP=false;
      if(c==="を") isP=true;
      else if(c==="の"&&next&&isKK(next)&&(isKK(prev)||/(これ|それ|あれ|私|あなた)$/.test(before))) isP=true;
      if(isP){ if(buf) out.push({t:buf,r:null}); buf=""; out.push({t:c,r:null,p:true}); }
      else buf+=c;
    }
    if(buf) out.push({t:buf,r:null});
  });
  // trailing particle
  const last=out[out.length-1];
  if(last&&last.r==null&&!last.p&&role!=="V"){
    const m=last.t.match(PEND);
    if(m&&(last.t.length>m[1].length||out.length>1||role==="Q")){
      const rest=last.t.slice(0,-m[1].length);
      out.pop(); if(rest) out.push({t:rest,r:null}); out.push({t:m[1],r:null,p:true});
    }
  }
  return out;
}

// ---------- particle pop-up ----------
function initParticlePopup(){
  if(window.__ppInit) return; window.__ppInit=true;
  const pop=document.createElement("div"); pop.className="ppop"; pop.hidden=true; document.body.appendChild(pop);
  let cur=null;
  function show(b){
    const p=b.dataset.p, info=PINFO[p]||[p,"Particle","",""], role=b.dataset.role;
    let ctx="";
    if(p==="に"&&role) ctx=role==="T"?"Here it marks a <b>time</b>.":role==="P"?"Here it marks a <b>destination or place</b>.":role==="H"?"Here it turns the word before it into an adverb (別々に, 一緒に).":"";
    if(p==="で"&&role) ctx=role==="P"?"Here it marks <b>where the action happens</b>.":role==="H"?"Here it marks <b>how</b> it's done.":role==="T"?"Here it marks <b>when</b> (after dinner).":"";
    if(p==="と"&&role==="H"&&/高いと/.test(b.parentElement.textContent)) ctx="Here it quotes a thought before 思います.";
    if(!ctx&&role&&ROLEHINT[role]) ctx=`It closes the <b>${ROLEHINT[role]}</b> block of this sentence.`;
    pop.innerHTML=`<div class="pp-h"><span class="pp-p">${jpEsc(p)}</span><span class="pp-r">${jpEsc(info[0])}</span><span class="pp-n">${jpEsc(info[1])}</span><button class="pp-x" aria-label="Close">×</button></div><p>${jpEsc(info[2])}</p>${ctx?`<p class="pp-c">${ctx}</p>`:""}${info[3]?`<p class="pp-e">${jpEsc(info[3])}</p>`:""}`;
    pop.hidden=false;
    const r=b.getBoundingClientRect(), w=Math.min(320,window.innerWidth-24);
    pop.style.width=w+"px";
    let left=Math.max(12,Math.min(r.left+window.scrollX-w/2+r.width/2,window.scrollX+window.innerWidth-w-12));
    pop.style.left=left+"px"; pop.style.top=(r.bottom+window.scrollY+8)+"px";
    cur=b;
  }
  document.addEventListener("click",e=>{
    const b=e.target.closest(".pt"); if(b){ e.preventDefault(); if(cur===b&&!pop.hidden){ pop.hidden=true; cur=null; } else show(b); return; }
    if(!e.target.closest(".ppop")||e.target.closest(".pp-x")){ pop.hidden=true; cur=null; }
  });
  document.addEventListener("keydown",e=>{ if(e.key==="Escape"){ pop.hidden=true; cur=null; } });
  window.addEventListener("resize",()=>{ pop.hidden=true; });
}

// ---------- kanji links that remember where you left off ----------
// On a click of a.kl, remember the enclosing item; on coming back with the Back button, scroll to it and flash it.
function initReturnLinks(storeKey,itemSel,idAttr,flashClass){
  document.addEventListener("click",e=>{ const a=e.target.closest("a.kl,a.kw"); if(!a) return; const it=a.closest(itemSel);
    try{ sessionStorage.setItem(storeKey,JSON.stringify({id:it?it.getAttribute(idAttr):null,y:window.scrollY})); }catch(err){} });
  let ret=null; try{ ret=JSON.parse(sessionStorage.getItem(storeKey)||"null"); }catch(e){}
  if(!ret) return;
  window.addEventListener("pageshow",ev=>{ const nav=(performance.getEntriesByType&&performance.getEntriesByType("navigation")[0])||{};
    if(ev.persisted||nav.type==="back_forward") setTimeout(()=>{ const el=ret.id!=null?document.querySelector(`${itemSel}[${idAttr}="${CSS.escape(String(ret.id))}"]`):null;
      if(el){ const bar=document.querySelector(".controls,.bar"); window.scrollTo(0,el.getBoundingClientRect().top+window.scrollY-(bar?bar.offsetHeight:0)-16); el.classList.remove(flashClass); void el.offsetWidth; el.classList.add(flashClass); }
      else window.scrollTo(0,ret.y); },40);
    try{ sessionStorage.removeItem(storeKey); }catch(e){} },{once:true});
}


// romaji for one space-separated token of a phrase: particles は/を/へ as wa/o/e, a trailing か split off
const JP_PARTICLE={"は":"wa","を":"o","へ":"e"}, JP_SPECIAL={"こんにちは":"konnichiwa","こんばんは":"konbanwa"};
function jpRomajiToken(t){ if(JP_PARTICLE[t]) return JP_PARTICLE[t]; if(JP_SPECIAL[t]) return JP_SPECIAL[t];
  if(t.length>2&&t.endsWith("か")&&/[すんた]/.test(t[t.length-2])) return krRomaji(t.slice(0,-1))+" ka"; return krRomaji(t); }

// ---------- kana word links: hiragana and katakana words that have a card on the kana word pages ----------
// words: {word: "h" | "k"}; base: path to the kana folder; from: short name of this page for the back button.
const JP_PART_CHARS="はがをにでへともかやねよの";
function linkKanaWords(roots,words,base,from){
  const list=Object.keys(words).filter(w=>w.length>=2).sort((a,b)=>b.length-a.length);
  if(!list.length) return;
  const isHira=c=>c>="\u3041"&&c<="\u309f", isKata=c=>(c>="\u30a0"&&c<="\u30ff")||c==="ー", isKan=c=>/[\u4e00-\u9fff々]/.test(c);
  const re=new RegExp(list.map(w=>w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|"),"g");
  const set=new Set(list);
  const ok=(text,i,w,prevCh,nextCh)=>{
    const kata=isKata(w[0]);
    if(kata) return !isKata(prevCh||"")&&!isKata(nextCh||"");
    if(prevCh&&isKan(prevCh)) return false;                     // okurigana: the tail of a kanji word
    for(let k=1;k<=3&&i-k>=0;k++){ if(set.has(text.slice(i-k,i+w.length))) return false; }   // inside a longer word
    if(nextCh&&isHira(nextCh)&&!JP_PART_CHARS.includes(nextCh)&&!/^(です|でした|ます|ました|ません|ください|だ|な|に|て|で)/.test(text.slice(i+w.length))) return false;
    return true;
  };
  [].forEach.call(roots,root=>{
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest("rt,a,button,.slot,mark")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
    const nodes=[]; while(walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(n=>{
      const t=n.nodeValue; let m, last=0, out=[]; re.lastIndex=0;
      const prevText=()=>{ let p=n.previousSibling; while(p&&!p.textContent) p=p.previousSibling; return p?p.textContent.slice(-1):""; };
      const nextText=()=>{ let p=n.nextSibling; while(p&&!p.textContent) p=p.nextSibling; return p?p.textContent[0]:""; };
      while((m=re.exec(t))){ const i=m.index, w=m[0];
        const prevCh=i>0?t[i-1]:prevText(), nextCh=i+w.length<t.length?t[i+w.length]:nextText();
        if(!ok(t,i,w,prevCh,nextCh)) { re.lastIndex=i+1; continue; }
        out.push(document.createTextNode(t.slice(last,i)));
        const a=document.createElement("a"); a.className="kw"; a.textContent=w; a.title="Open "+w+" in "+(words[w]==="k"?"katakana":"kana")+" words";
        a.href=`${base}${words[w]==="k"?"katakana-words":"kana-words"}.html?from=${from}#w-${encodeURIComponent(w)}`;
        out.push(a); last=i+w.length; }
      if(out.length){ out.push(document.createTextNode(t.slice(last))); n.replaceWith(...out); }
    });
  });
}
(function(){ const st=document.createElement("style"); st.textContent=`a.kw{color:inherit;text-decoration:none;border-bottom:1px dotted currentColor;cursor:pointer}a.kw:hover{background:rgba(127,127,127,.15);border-radius:2px}`; document.head.appendChild(st); })();

// ---------- grammar blocks: colour each part of a sentence by its job ----------
// One setting for every page (the phrasebook, sentence builder, grammar and situation pages).
const JP_NOTE=/([\u4e00-\u9fff々ヶ]+)\{([^}]+)\}/g;
const jpKanaOf=s=>s.replace(JP_NOTE,"$2"), jpPlainOf=s=>s.replace(JP_NOTE,"$1");
function blocksOn(){ try{ return localStorage.getItem("blocks")!=="off"; }catch(e){ return true; } }
function setBlocks(on){ try{ localStorage.setItem("blocks",on?"on":"off"); }catch(e){} }
const JP_ROLE={W:"--rW",T:"--rT",P:"--rP",H:"--rH",O:"--rO",V:"--rV",Q:"--rQ"};
const JP_PARTS=new Set(["は","が","を","に","で","へ","と","も","の","か","から","まで","や","ね","よ","には","では","にも","でも"]);
const JP_TIMEW=/[時日週月年今朝夜晩曜昼]|いつ|何時|あした|きょう/;
const JP_PLACEW=/^(ここ|そこ|あそこ|どこ|この 近く|近く)$|[駅店家館院局港場所屋社]/;
const JP_QWORD={"どこ":"P","どちら":"P","いつ":"T","何時{なんじ}":"T","何{なに}":"O","何{なん}":"O","誰{だれ}":"W","どう":"H","どうして":"H","いくら":"O","どれ":"O","どの":"O","いくつ":"O","何人{なんにん}":"O","何名様{なんめいさま}":"O","何番線{なんばんせん}":"O","何分{なんぷん}":"T","何曜日{なんようび}":"T","何日{なんにち}":"T"};
const JP_ADV=new Set(["もう","少{すこ}し","ちょっと","ゆっくり","まっすぐ","もっと","とても","あまり","一緒{いっしょ}に","また","すぐ","まだ"]);
function jpRolesFor(toks){
  // returns [{t, r, p}] ; r role letter, p = particle flag
  const out=[]; let buf=[];
  const flush=(role)=>{ buf.forEach(t=>out.push({t,r:role})); buf=[]; };
  toks.forEach((t,i)=>{
    const bare=t.replace(/[、。]$/,"");
    if(JP_PARTS.has(bare)&&buf.length){
      const txt=buf.join(" ");
      let r="V";
      if(bare==="も"&&/[てで]$/.test(jpKanaOf(buf[buf.length-1]))) r="V";
      else if(["は","が","も"].includes(bare)) r="W";
      else if(bare==="を") r="O";
      else if(bare==="に"||bare==="には"||bare==="にも") r=JP_TIMEW.test(txt)?"T":"P";
      else if(bare==="で"||bare==="では"||bare==="でも") r=JP_PLACEW.test(txt)?"P":"H";
      else if(bare==="へ"||bare==="まで") r="P";
      else if(bare==="から") r=JP_TIMEW.test(txt)?"T":"P";
      else if(bare==="と") r="H";
      else if(bare==="の"){ buf.push(t); out.push(...[]); return; }
      else if(bare==="か"){ flush("V"); out.push({t,r:"Q",p:true}); return; }
      flush(r); out.push({t,r,p:true}); return;
    }
    if(bare==="か"&&i===toks.length-1){ flush("V"); out.push({t,r:"Q",p:true}); return; }
    buf.push(t);
  });
  // tail: predicate, with question words and adverbs picked out
  buf.forEach(t=>{ const b=t.replace(/[、。]$/,""); out.push({t,r:b==="___"?"O":/^[一二三四五六七八九十何]\{[^}]*\}つ$|^[一二三四五六七八九十]\{[^}]*\}(人|枚|本|杯)/.test(b)?"O":JP_QWORD[b]||(JP_ADV.has(b)?"H":"V")}); });
  // mark の inside chunks as particle (keep chunk role)
  return out.map(x=>x.t==="の"?{...x,p:true}:x);
}

const jpPbtn=(t,r,cls="")=>`<button type="button" class="pt${cls}" data-p="${jpEsc(t)}" data-role="${r||""}">${jpEsc(t)}</button>`;
const jpWrap=(r,inner)=>`<span class="ck" data-r="${r}" style="--c:var(${JP_ROLE[r]})">${inner}</span>`;
// a sentence written as space-separated tokens with 漢字{かんじ} readings
function jpRolesWith(n,roles){ const R=jpRolesFor(n.split(" ")); if(roles) R.forEach((x,i)=>{ if(roles[i]) x.r=roles[i]; }); return R; }
function jpBlocksLine(n,link,roles){
  const L=link||(h=>h);
  const ruby=t=>{ let o="",last=0; t.replace(JP_NOTE,(m,b,r,off)=>{ o+=jpEsc(t.slice(last,off))+rdRuby(b,r); last=off+m.length; return m; }); return L(o+jpEsc(t.slice(last))); };
  return jpRolesWith(n,roles).map(x=>{
    if(x.p) return jpWrap(x.r,jpPbtn(x.t.replace(/[、。]$/,""),x.r)+(/[、。]$/.test(x.t)?x.t.slice(-1):""));
    const m=x.r==="V"&&x.t.length>2&&x.t.match(/^(.*[すんた])か$/);
    if(m) return jpWrap("V",ruby(m[1]))+jpWrap("Q",jpPbtn("か","Q"));
    return jpWrap(x.r,ruby(x.t)); }).join(" ");
}
function jpBlocksRom(n,roles){
  return jpRolesWith(n,roles).map(x=>{ const r=jpRomajiToken(jpKanaOf(x.t));
    if(x.p) return jpWrap(x.r,jpPbtn(x.t.replace(/[、。]$/,""),x.r," pr").replace(/>[^<]*<\/button>/,">"+jpEsc(r.replace(/,\s*$/,""))+"</button>")+(/、$/.test(x.t)?",":""));
    const m=x.r==="V"&&r.match(/^(.*) ka$/); if(m) return jpWrap("V",jpEsc(m[1]))+" "+jpWrap("Q",'<button type="button" class="pt pr" data-p="か" data-role="Q">ka</button>');
    return jpWrap(x.r,jpEsc(r)); }).join(" ").replace(/ ,/g,",");
}
// a sentence-builder sentence: chunks with their roles
function jpBlocksChunks(kj,kn,roles,link){
  const L=link||(h=>h);
  return kj.map((k,i)=>{ const r=roles&&roles[i]; const parts=jpChunkParts(k,kn[i],r); let vf=false;
    const inner=parts.map(p=>{ if(p.p) return jpPbtn(p.t,r); if(p.r!=null){ const x=rdRuby(p.t,p.r,vf); vf=true; return L(x); } return jpEsc(p.t); }).join("");
    return r?jpWrap(r,inner):`<span class="ck">${inner}</span>`; }).join(" ");
}
// English coloured to match, when the sentence has its English marked up: [[role, text], ...]
function jpEnHtml(s){ return s.enb&&s.enb.length?s.enb.map(([r,t])=>r?jpWrap(r,jpEsc(t)):jpEsc(t)).join(""):jpEsc(s.en); }
// any sentence record (tokens with readings, or sentence-builder chunks) → {jp, rom, en} html
function jpSentence(s,link){
  if(s.kj) return {jp:jpBlocksChunks(s.kj,s.kn,s.roles,link), rom:(s.rj||[]).map((r,i)=>s.roles&&s.roles[i]?jpWrap(s.roles[i],jpEsc(r)):jpEsc(r)).join(" "), en:jpEnHtml(s), say:s.kj.join("")};
  return {jp:jpBlocksLine(s.n,link,s.roles), rom:jpBlocksRom(s.n,s.roles), en:jpEnHtml(s), say:jpPlainOf(s.n).replace(/ /g,"")};
}
function jpKeybar(){ return `<div class="keybar" aria-label="Block colours"><span style="--c:var(--rW)">WHO / TOPIC<small>は・が</small></span><span style="--c:var(--rT)">TIME<small>に</small></span><span style="--c:var(--rP)">PLACE<small>で・に・へ・から・まで</small></span><span style="--c:var(--rH)">HOW / WITH<small>と・で</small></span><span style="--c:var(--rO)">WHAT<small>を</small></span><span style="--c:var(--rV)">VERB / です</span><span style="--c:var(--rQ)">QUESTION<small>か</small></span><span class="kp">particle<small>tap one</small></span></div>`; }
(function(){ const st=document.createElement("style"); st.textContent=`
:root{--rW:#e8384f;--rT:#12a5c9;--rP:#22a36b;--rH:#d99a00;--rO:#ef7020;--rV:#7b3fa0;--rQ:#dd3b8c}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--rW:#ff6b7d;--rT:#4fc6e6;--rP:#4fcf92;--rH:#f0c040;--rO:#ff9a52;--rV:#b184d6;--rQ:#f06db0}}
body.jb-on .ck[data-r]{color:var(--c)}
body.jb-on .keybar{display:flex}
.jb-page .keybar{display:none;gap:5px;overflow-x:auto;scrollbar-width:none;padding:0 1.25rem .5rem;margin:0 auto}
.jb-page .keybar span{flex:1 0 auto;background:var(--c);color:#fff;border-radius:4px;padding:3px 8px;font-size:11px;font-weight:700;text-align:center;white-space:nowrap;font-family:system-ui,sans-serif}
.jb-page .keybar span small{font-weight:500;opacity:.9;margin-left:4px}
.jb-page .keybar span.kp{background:rgba(127,127,127,.2);color:inherit}
.jb-page .pt{font:inherit;font-weight:700;color:inherit;background:rgba(127,127,127,.18);border:0;border-radius:4px;padding:0 .18em;margin:0 .04em;cursor:pointer;line-height:inherit}
.jb-page .pt.pr{font-style:normal}
.jb-page .ppop{position:absolute;z-index:60;background:var(--sheet,#fff);color:var(--ink,#111);border:1px solid rgba(127,127,127,.35);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.2);padding:10px 12px;font-size:.92rem;line-height:1.5}
.jb-page .ppop[hidden]{display:none}
.jb-page .pp-h{display:flex;align-items:baseline;gap:8px;margin-bottom:4px}
.jb-page .pp-p{font-size:1.5rem;font-weight:700}
.jb-page .pp-r{font-style:italic;opacity:.7}
.jb-page .pp-n{font-weight:600}
.jb-page .pp-x{margin-left:auto;border:0;background:none;font-size:1.3rem;line-height:1;cursor:pointer;color:inherit;opacity:.6}
.jb-page .ppop p{margin:4px 0}
.jb-page .pp-c{background:rgba(127,127,127,.12);border-radius:4px;padding:4px 8px}
.jb-page .pp-e{opacity:.75;font-size:.85rem}`; document.head.appendChild(st); })();

// ---------- a link back to the home page, on every page ----------
(function(){
  const me=document.currentScript&&document.currentScript.src; if(!me) return;
  const root=me.replace(/assets\/common\.js.*$/,"");
  const st=document.createElement("style");
  st.textContent=`.homelink{display:block;max-width:1000px;margin:0 auto;padding:calc(.6rem + env(safe-area-inset-top,0px)) 1.25rem .2rem;font:600 .85rem/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;color:inherit;opacity:.65;text-decoration:none;letter-spacing:.01em}
.homelink:hover,.homelink:focus-visible{opacity:1;text-decoration:underline}
.homelink .jp{font-family:"Noto Serif JP","Hiragino Mincho ProN",serif;margin-left:.3em}
header.top,header.masthead,.masthead{padding-top:.6rem}`;
  document.head.appendChild(st);
  document.addEventListener("DOMContentLoaded",()=>{
    if(document.querySelector(".homelink")) return;
    const a=document.createElement("a");
    a.className="homelink"; a.href=root+"index.html";
    a.innerHTML='← All pages<span class="jp">日本語</span>';
    document.body.insertBefore(a,document.body.firstChild);
  });
})();

// ---------- floating buttons: back to the top, and home ----------
(function(){
  const me=document.currentScript&&document.currentScript.src; if(!me) return;
  const root=me.replace(/assets\/common\.js.*$/,"");
  const st=document.createElement("style");
  st.textContent=`.floatnav{position:fixed;left:.9rem;bottom:calc(.9rem + env(safe-area-inset-bottom,0px));z-index:40;display:flex;flex-direction:column;gap:.4rem;opacity:0;visibility:hidden;transition:opacity .18s}
.floatnav.on{opacity:.92;visibility:visible}
.floatnav a,.floatnav button{display:grid;place-items:center;width:2.6rem;height:2.6rem;border-radius:50%;border:1px solid rgba(127,127,127,.35);background:var(--sheet,#fff);color:var(--ink,#1b2a3a);box-shadow:0 2px 10px rgba(0,0,0,.18);cursor:pointer;font:600 1rem/1 system-ui,sans-serif;text-decoration:none;padding:0}
.floatnav a:hover,.floatnav button:hover,.floatnav a:focus-visible,.floatnav button:focus-visible{opacity:1;border-color:currentColor}
@media (prefers-color-scheme: dark){.floatnav a,.floatnav button{background:#1C2029;color:#E6E8EE}}
@media print{.floatnav{display:none}}`;
  document.head.appendChild(st);
  document.addEventListener("DOMContentLoaded",()=>{
    if(document.querySelector(".floatnav")) return;
    const nav=document.createElement("div"); nav.className="floatnav";
    nav.innerHTML=`<a href="${root}index.html" title="Home: all pages" aria-label="Home: all pages">⌂</a>`+
      `<button type="button" title="Back to the top" aria-label="Back to the top">↑</button>`;
    nav.querySelector("button").onclick=()=>window.scrollTo({top:0,behavior:"smooth"});
    document.body.appendChild(nav);
    const show=()=>nav.classList.toggle("on",window.scrollY>400);
    window.addEventListener("scroll",show,{passive:true}); show();
  });
})();

// ---------- offline support: register the service worker at the site root ----------
(function(){ if(!("serviceWorker" in navigator)||location.protocol==="file:") return;
  const me=document.currentScript&&document.currentScript.src; if(!me) return;
  const root=me.replace(/assets\/common\.js.*$/,"");
  window.addEventListener("load",()=>navigator.serviceWorker.register(root+"sw.js").catch(()=>{})); })();
