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
