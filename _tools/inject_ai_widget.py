# -*- coding: utf-8 -*-
import sys

FILES = {
 "index.html": dict(lang="vi",
   title="Trợ lý AI Pháp lý", sub="Pháp điển · Án lệ · TMĐT · Kinh tế số",
   btn="Hỏi Trợ lý AI", z15="Trợ lý AI",
   ph="Hỏi về luật, án lệ, TMĐT…", send="Gửi",
   greet="Xin chào! Tôi là Trợ lý AI của ông Nguyễn Tấn Phong, có thể tra cứu Pháp điển và Án lệ Việt Nam. Bạn cần hỏi điều gì?",
   typing="Đang tra cứu…", err="Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
   disc="Thông tin mang tính tham khảo, không thay thế tư vấn pháp lý chính thức."),
 "en.html": dict(lang="en",
   title="AI Legal Assistant", sub="Codified law · Case law · E-commerce",
   btn="Ask the AI Assistant", z15="AI Assistant",
   ph="Ask about law, precedents, e-commerce…", send="Send",
   greet="Hello! I'm Nguyen Tan Phong's AI assistant. I can look up Vietnam's codified law and case law. How can I help?",
   typing="Searching…", err="Sorry, something went wrong. Please try again.",
   disc="For reference only; not a substitute for formal legal advice."),
 "ja.html": dict(lang="ja",
   title="AI法務アシスタント", sub="法典 · 判例 · EC · デジタル経済",
   btn="AIアシスタントに質問", z15="AIアシスタント",
   ph="法律・判例・ECについて質問…", send="送信",
   greet="こんにちは！グエン・タン・フォン氏のAIアシスタントです。ベトナムの法典・判例を検索できます。ご質問をどうぞ。",
   typing="検索中…", err="申し訳ありません。エラーが発生しました。もう一度お試しください。",
   disc="本情報は参考用であり、正式な法的助言に代わるものではありません。"),
 "zh.html": dict(lang="zh",
   title="AI 法律助手", sub="法典 · 判例 · 电商 · 数字经济",
   btn="咨询 AI 助手", z15="AI 助手",
   ph="咨询法律、判例、电商…", send="发送",
   greet="您好！我是阮晋峰先生的 AI 助手，可检索越南法典与判例。请问有什么可以帮您？",
   typing="检索中…", err="抱歉，出现错误，请重试。",
   disc="信息仅供参考，不能替代正式法律咨询。"),
}

# ---- Nút Z15 (chèn trước nút Save) ----
def z15_btn(c):
    return ('<button type="button" class="v-sq v-ai blink" title="__Z15__" onclick="openAIChat()" aria-label="__Z15__">'
            '<i class="fas fa-robot"></i></button>\n  ').replace("__Z15__", c["z15"])

# ---- Nút Hero (chèn cuối hero-2col-text) ----
def hero_btn(c):
    return ('<div class="hero-2col-cta"><button type="button" class="btn-ai-hero" onclick="openAIChat()">'
            '<i class="fas fa-robot"></i> <span>__BTN__</span></button></div>\n      ').replace("__BTN__", c["btn"])

# ---- Widget (chèn trước </body>) ----
WIDGET = r"""
<!-- ============ Z16 · TRỢ LÝ AI PHÁP LÝ (RAG) ============ -->
<style>
  .btn-ai-hero{display:inline-flex;align-items:center;gap:9px;margin-top:22px;padding:13px 24px;border-radius:12px;
    background:linear-gradient(135deg,var(--gold),var(--gold-light));color:var(--navy);font-weight:700;font-size:14px;
    border:0;cursor:pointer;box-shadow:0 8px 24px rgba(224,170,121,0.32);transition:transform .15s,box-shadow .15s;font-family:inherit;}
  .btn-ai-hero:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(224,170,121,0.45);}
  .btn-ai-hero i{font-size:15px;}
  .v-sq.v-ai{background:linear-gradient(135deg,#6d4bd1,#9b6cff)!important;color:#fff!important;border-color:#9b6cff!important;}
  .v-sq.v-ai:hover{transform:scale(1.1);box-shadow:-3px 3px 18px rgba(155,108,255,0.5)!important;}
  #ai-chat{position:fixed;bottom:20px;right:20px;width:390px;max-width:calc(100vw - 32px);height:600px;max-height:80vh;
    background:#15110d;border:1px solid var(--border);border-radius:18px;z-index:10000;display:none;flex-direction:column;
    overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,0.6);}
  #ai-chat.open{display:flex;}
  .ai-head{display:flex;align-items:center;gap:12px;padding:16px 18px;background:linear-gradient(135deg,#1f1812,#15110d);border-bottom:1px solid var(--border);}
  .ai-head-ic{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--gold),var(--gold-light));
    display:flex;align-items:center;justify-content:center;color:var(--navy);font-size:18px;flex-shrink:0;}
  .ai-head-tt{flex:1;min-width:0;}
  .ai-head-tt b{display:block;color:#fff;font-size:15px;font-weight:700;}
  .ai-head-tt span{display:block;color:var(--text-soft);font-size:10.5px;letter-spacing:.02em;margin-top:2px;}
  .ai-close{background:none;border:0;color:var(--text-soft);font-size:20px;cursor:pointer;padding:4px 8px;border-radius:8px;line-height:1;}
  .ai-close:hover{color:var(--gold);background:rgba(224,170,121,0.1);}
  .ai-msgs{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:12px;}
  .ai-msg{max-width:85%;padding:11px 14px;border-radius:14px;font-size:13.5px;line-height:1.6;word-wrap:break-word;white-space:pre-wrap;}
  .ai-msg a{color:var(--gold-light);text-decoration:underline;}
  .ai-msg.user{align-self:flex-end;background:linear-gradient(135deg,var(--gold),var(--gold-light));color:var(--navy);border-bottom-right-radius:4px;font-weight:500;}
  .ai-msg.bot{align-self:flex-start;background:rgba(255,255,255,0.06);color:#e8e2da;border:1px solid var(--border);border-bottom-left-radius:4px;}
  .ai-msg.typing{color:var(--text-soft);font-style:italic;}
  .ai-foot{padding:12px 14px;border-top:1px solid var(--border);background:#15110d;}
  .ai-input-row{display:flex;gap:8px;align-items:flex-end;}
  .ai-input-row textarea{flex:1;resize:none;background:rgba(255,255,255,0.05);border:1px solid var(--border);border-radius:10px;
    color:#fff;padding:10px 12px;font-size:13.5px;font-family:inherit;max-height:96px;line-height:1.4;}
  .ai-input-row textarea:focus{outline:none;border-color:var(--gold);}
  .ai-send{flex-shrink:0;width:40px;height:40px;border-radius:10px;border:0;cursor:pointer;
    background:linear-gradient(135deg,var(--gold),var(--gold-light));color:var(--navy);font-size:15px;}
  .ai-send:disabled{opacity:.5;cursor:not-allowed;}
  .ai-disc{color:var(--text-soft);font-size:9.5px;line-height:1.4;margin-top:8px;text-align:center;opacity:.75;}
  @media(max-width:480px){#ai-chat{right:0;left:0;bottom:0;width:100%;max-width:100%;height:88vh;border-radius:18px 18px 0 0;}}
</style>
<section id="ai-chat" data-zone="Z16 · Trợ lý AI" role="dialog" aria-label="__TITLE__" aria-modal="false">
  <div class="ai-head">
    <div class="ai-head-ic"><i class="fas fa-robot"></i></div>
    <div class="ai-head-tt"><b>__TITLE__</b><span>__SUB__</span></div>
    <button type="button" class="ai-close" onclick="closeAIChat()" aria-label="Đóng">&times;</button>
  </div>
  <div class="ai-msgs" id="ai-msgs"></div>
  <div class="ai-foot">
    <div class="ai-input-row">
      <textarea id="ai-input" rows="1" placeholder="__PH__" aria-label="__PH__"></textarea>
      <button type="button" class="ai-send" id="ai-send" onclick="sendAIMsg()" aria-label="__SEND__"><i class="fas fa-paper-plane"></i></button>
    </div>
    <div class="ai-disc">__DISC__</div>
  </div>
</section>
<script>
(function(){
  var LANG="__LANG__", GREET="__GREET__", TYPING="__TYPING__", ERR="__ERR__";
  var msgs=[], started=false, busy=false;
  function el(id){return document.getElementById(id);}
  function esc(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
  function linkify(s){return s.replace(/(https?:\/\/[^\s<]+)/g,'<a href="$1" target="_blank" rel="noopener">$1</a>');}
  function render(){
    var box=el("ai-msgs"); box.innerHTML="";
    var g=document.createElement("div"); g.className="ai-msg bot"; g.innerHTML=linkify(esc(GREET)); box.appendChild(g);
    msgs.forEach(function(m){
      var d=document.createElement("div"); d.className="ai-msg "+(m.role==="user"?"user":"bot");
      d.innerHTML=linkify(esc(m.content)); box.appendChild(d);
    });
    if(busy){var t=document.createElement("div"); t.className="ai-msg bot typing"; t.textContent=TYPING; box.appendChild(t);}
    box.scrollTop=box.scrollHeight;
  }
  window.openAIChat=function(){el("ai-chat").classList.add("open"); if(!started){started=true; render();} setTimeout(function(){el("ai-input").focus();},100);};
  window.closeAIChat=function(){el("ai-chat").classList.remove("open");};
  window.sendAIMsg=async function(){
    if(busy)return; var inp=el("ai-input"); var text=(inp.value||"").trim(); if(!text)return;
    msgs.push({role:"user",content:text}); inp.value=""; inp.style.height="auto"; busy=true; el("ai-send").disabled=true; render();
    try{
      var r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({messages:msgs,lang:LANG})});
      var data=await r.json().catch(function(){return {};});
      var reply=(data&&data.reply)?data.reply:ERR;
      msgs.push({role:"assistant",content:reply});
    }catch(e){ msgs.push({role:"assistant",content:ERR}); }
    busy=false; el("ai-send").disabled=false; render();
  };
  document.addEventListener("DOMContentLoaded",function(){
    var inp=el("ai-input"); if(!inp)return;
    inp.addEventListener("keydown",function(e){ if(e.key==="Enter"&&!e.shiftKey){e.preventDefault(); sendAIMsg();} });
    inp.addEventListener("input",function(){ this.style.height="auto"; this.style.height=Math.min(this.scrollHeight,96)+"px"; });
  });
})();
</script>
<!-- ============ /Z16 ============ -->
"""

def build_widget(c):
    w = WIDGET
    repl = {"__TITLE__":c["title"],"__SUB__":c["sub"],"__PH__":c["ph"],"__SEND__":c["send"],
            "__DISC__":c["disc"],"__LANG__":c["lang"],"__GREET__":c["greet"],"__TYPING__":c["typing"],"__ERR__":c["err"]}
    for k,v in repl.items():
        w = w.replace(k, v)
    return w

for fn, c in FILES.items():
    s = open(fn, encoding="utf-8").read()
    rep=[]
    if "id=\"ai-chat\"" in s:
        print(f"{fn} ⏭ widget đã có, bỏ qua"); continue
    # 1) nút Z15 trước nút save
    save_anchor = '<button type="button" class="v-sq v-save"'
    if save_anchor in s:
        s = s.replace(save_anchor, z15_btn(c) + save_anchor, 1); rep.append("nút Z15")
    else: rep.append("⚠ ko thấy v-save")
    # 2) nút hero cuối hero-2col-text
    hero_anchor = '    </div>\n    <div class="hero-2col-img">'
    if hero_anchor in s:
        s = s.replace(hero_anchor, '    ' + hero_btn(c) + '</div>\n    <div class="hero-2col-img">', 1); rep.append("nút hero")
    else: rep.append("⚠ ko thấy hero anchor")
    # 3) widget trước </body>
    if "</body>" in s:
        s = s.replace("</body>", build_widget(c) + "\n</body>", 1); rep.append("widget")
    else: rep.append("⚠ ko thấy </body>")
    open(fn,"w",encoding="utf-8").write(s)
    print(f"{fn} ✅ " + "; ".join(rep))
