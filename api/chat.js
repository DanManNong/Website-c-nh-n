// Vercel Serverless Function — Trợ lý AI Pháp lý (RAG) cho nguyentanphong.com
// LLM: Google Gemini 2.5 — LUÂN PHIÊN 3 model (flash / flash-lite / pro) + dự phòng khi 429.
// Luồng: (1) viết lại câu hỏi -> cụm từ khoá; (2) tìm Pháp điển + Án lệ (Supabase PGroonga);
//        (3) trả lời kèm trích dẫn.
// ENV bắt buộc (đặt trên Vercel): GEMINI_API_KEY

// Thứ tự xoay vòng — bỏ bớt model nào thì xoá khỏi mảng này.
const MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"];
const MAX_TOKENS = 1100;
const MAX_MSG = 12;
const MAX_CHARS = 2000;
const TARGET_ROWS = 7;

const SUPABASE_URL = process.env.SUPABASE_URL || "https://dcmtbgcltopnqsiedwlg.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY || "sb_publishable_goPNlFYvQUspbFSvDzkN3w_KMapxvUq";
const endpointFor = m => `https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent`;

// Xoay vòng cho tác vụ nhẹ (viết lại câu hỏi): bắt đầu ngẫu nhiên để trải đều quota.
function rotatedModels() {
  const i = Math.floor(Math.random() * MODELS.length);
  return MODELS.map((_, k) => MODELS[(i + k) % MODELS.length]);
}
// Thứ tự cho CÂU TRẢ LỜI: ưu tiên model mạnh (flash) -> pro -> lite (lite chỉ là cứu cánh) để câu trả lời chất lượng hơn.
const ANSWER_ORDER = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"];

const ANSWER_SYSTEM = `Bạn là Trợ lý AI Pháp lý trên website của ông Nguyễn Tấn Phong — Phó Chủ tịch Hiệp hội Thương mại điện tử Việt Nam (VECOM), chuyên gia Kinh tế số & Pháp luật. Trả lời câu hỏi pháp luật Việt Nam, ưu tiên DỰA TRÊN NGỮ CẢNH (các điều luật Pháp điển + án lệ) cung cấp bên dưới.

CÁCH TRẢ LỜI:
- Hãy trả lời HỮU ÍCH và trực tiếp: tóm tắt, giải thích, kết nối các điều luật liên quan trong NGỮ CẢNH để giải đáp câu hỏi — KỂ CẢ khi điều luật không khớp 100%, hãy nêu những gì gần nhất và hữu ích.
- Khi dùng nội dung từ một mục, TRÍCH DẪN mã điều/số án lệ theo [n] (kèm link nếu có).
- KHÔNG bịa số điều, tên văn bản hay nội dung không có trong ngữ cảnh. Có thể bổ sung kiến thức pháp lý phổ thông để làm rõ, nhưng phải nói rõ phần nào là dẫn chiếu điều luật, phần nào là giải thích chung.
- CHỈ nói "Tôi chưa tìm thấy quy định cụ thể trong dữ liệu tra cứu" khi NGỮ CẢNH hoàn toàn không liên quan đến câu hỏi.
- Trả lời bằng ĐÚNG ngôn ngữ người dùng. Trình bày rõ ràng, có cấu trúc (gạch đầu dòng khi phù hợp), không lan man.
- Kết thúc bằng 1 dòng ngắn: thông tin mang tính tham khảo, không thay thế tư vấn pháp lý chính thức; vụ việc cụ thể nên liên hệ ông Phong.
- Lịch sự từ chối nội dung ngoài phạm vi pháp luật.`;

const REWRITE_SYSTEM = `Bạn tạo TRUY VẤN TÌM KIẾM cho cơ sở dữ liệu pháp luật Việt Nam (Pháp điển + Án lệ).
Dựa vào hội thoại, đưa ra 3-4 cụm từ khoá, mỗi cụm 1 dòng, xếp từ CỤ THỂ đến RỘNG.
YÊU CẦU:
- Dùng ĐÚNG THUẬT NGỮ PHÁP LÝ CHÍNH THỨC trong văn bản luật VN (vd: "sàn giao dịch thương mại điện tử" chứ không phải "sàn TMĐT"; "bảo vệ dữ liệu cá nhân"; "hợp đồng điện tử"; "hành vi bị nghiêm cấm").
- Mỗi cụm là một cụm danh từ pháp lý hoàn chỉnh, KHÔNG động từ, KHÔNG stopword, KHÔNG ngoặc kép, KHÔNG đánh số.
- Dòng đầu nên là thuật ngữ cốt lõi & đầy đủ nhất của vấn đề.
Nếu câu hỏi (kể cả tiếng Anh/Nhật/Trung) không liên quan pháp luật, trả về đúng 1 dòng: NONE
Nếu hỏi bằng ngôn ngữ khác, vẫn tạo cụm từ khoá bằng TIẾNG VIỆT (vì dữ liệu là tiếng Việt).`;

function send(res, status, obj) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(obj));
}

// Gọi 1 model cụ thể.
async function callModel(apiKey, model, system, messages, maxTokens) {
  const contents = messages.map(m => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.content }] }));
  const gc = { maxOutputTokens: maxTokens, temperature: 0.3 };
  // flash/flash-lite: tắt thinking cho rẻ/nhanh. pro KHÔNG cho tắt -> để mặc định.
  if (!model.includes("pro")) gc.thinkingConfig = { thinkingBudget: 0 };
  const r = await fetch(endpointFor(model), {
    method: "POST",
    headers: { "x-goog-api-key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ systemInstruction: { parts: [{ text: system }] }, contents, generationConfig: gc }),
  });
  if (!r.ok) { const t = await r.text().catch(() => ""); const e = new Error("gemini " + r.status + " " + t); e.status = r.status; throw e; }
  const data = await r.json();
  const cand = data && data.candidates && data.candidates[0];
  if (!cand || !cand.content || !Array.isArray(cand.content.parts)) return "";
  return cand.content.parts.filter(p => p && p.text).map(p => p.text).join("").trim();
}

// Luân phiên + dự phòng: thử lần lượt theo thứ tự `order`; nếu 429/5xx thì sang model kế tiếp.
async function gemini(apiKey, system, messages, maxTokens, order) {
  let lastErr;
  for (const model of (order || rotatedModels())) {
    try { const text = await callModel(apiKey, model, system, messages, maxTokens); return { text, model }; }
    catch (e) {
      lastErr = e;
      const retryable = e.status === 429 || (e.status >= 500 && e.status < 600);
      if (retryable) { console.warn("model busy, fallback:", model, e.status); continue; }
      throw e;
    }
  }
  throw lastErr;
}

async function rewriteQueries(apiKey, history) {
  try {
    const { text: txt } = await gemini(apiKey, REWRITE_SYSTEM, history, 120);
    const lines = txt.split("\n").map(s => s.replace(/^[-*\d.)\s"]+/, "").replace(/["]+$/, "").trim()).filter(s => s.length >= 2 && s.length <= 80);
    if (lines.length === 1 && lines[0].toUpperCase() === "NONE") return [];
    return lines.slice(0, 3);
  } catch (e) { console.error("rewrite err", e.message); return []; }
}

function logAI(question, lang, n, model) {
  try {
    fetch(`${SUPABASE_URL}/rest/v1/ai_logs`, {
      method: "POST",
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, "Content-Type": "application/json", Prefer: "return=minimal" },
      body: JSON.stringify({ question: String(question || "").slice(0, 500), lang: String(lang || "").slice(0, 8), n_sources: n, model: String(model || "").slice(0, 40) }),
    }).catch(() => {});
  } catch (e) { /* fire-and-forget */ }
}

async function searchLaw(q, k) {
  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/rpc/phaply_search`, {
      method: "POST",
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ q, k }),
    });
    if (!r.ok) { console.error("search rpc", r.status, await r.text().catch(() => "")); return []; }
    const data = await r.json();
    return Array.isArray(data) ? data : [];
  } catch (e) { console.error("searchLaw err", e); return []; }
}

function buildContext(rows) {
  if (!rows.length) return "(Không tìm thấy điều luật/án lệ liên quan trong dữ liệu.)";
  return rows.map((x, i) => {
    const kind = x.kind === "anle" ? "ÁN LỆ" : "ĐIỀU LUẬT";
    const url = x.url ? `\nNguồn: ${x.url}` : "";
    return `[${i + 1}] (${kind}) ${x.citation || ""} — ${x.title || ""}\n${(x.snippet || "").slice(0, 900)}${url}`;
  }).join("\n\n");
}

// ====== CÔNG TẮC TẠM TẮT AI ======
// Đặt true để tắt tạm (trả lời "đang phát triển"); đặt false để bật lại AI.
const MAINTENANCE = true;
const MAINTENANCE_MSG = {
  vi: "Trợ lý AI đang trong quá trình phát triển. Vui lòng liên hệ 0915159499 để được hỗ trợ.",
  en: "The AI assistant is under development. Please contact 0915159499 for support.",
  ja: "AIアシスタントは現在開発中です。サポートは 0915159499 までご連絡ください。",
  zh: "AI 助手正在开发中。如需帮助，请联系 0915159499。",
};

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "method_not_allowed" });

  // Tắt tạm: trả lời ngay, KHÔNG gọi Gemini (khỏi tốn quota)
  if (MAINTENANCE) {
    let lang = "vi";
    try { const b = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {}); if (b && b.lang) lang = b.lang; } catch (e) {}
    return send(res, 200, { reply: MAINTENANCE_MSG[lang] || MAINTENANCE_MSG.vi, sources: [], maintenance: true });
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) return send(res, 503, { error: "not_configured", reply: "Trợ lý AI đang được cấu hình. Vui lòng liên hệ trực tiếp qua Zalo/điện thoại trên trang." });

  let body = req.body;
  try {
    if (!body) { const raw = await new Promise((rs, rj) => { let d = ""; req.on("data", c => (d += c)); req.on("end", () => rs(d)); req.on("error", rj); }); body = raw ? JSON.parse(raw) : {}; }
    else if (typeof body === "string") { body = JSON.parse(body); }
  } catch (e) { return send(res, 400, { error: "bad_json" }); }

  let messages = (Array.isArray(body && body.messages) ? body.messages : [])
    .filter(m => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string" && m.content.trim())
    .slice(-MAX_MSG).map(m => ({ role: m.role, content: String(m.content).slice(0, MAX_CHARS) }));
  if (!messages.length || messages[messages.length - 1].role !== "user") return send(res, 400, { error: "no_user_message" });
  const userQuery = messages[messages.length - 1].content;

  try {
    // 1) Viết lại -> truy vấn
    const queries = await rewriteQueries(apiKey, messages.slice(-4));

    // 2) Tìm kiếm: phrase trước (cụ thể->rộng), gộp & loại trùng
    const seen = new Set(); const rows = [];
    for (const q of queries) {
      if (rows.length >= TARGET_ROWS) break;
      const phrase = /\s/.test(q) ? `"${q}"` : q;
      const r = await searchLaw(phrase, 5);
      for (const x of r) { const key = (x.kind || "") + "|" + (x.citation || "") + "|" + (x.title || ""); if (!seen.has(key)) { seen.add(key); rows.push(x); } }
    }
    if (rows.length < 3) {
      const r = await searchLaw(userQuery, 6);
      for (const x of r) { const key = (x.kind || "") + "|" + (x.citation || "") + "|" + (x.title || ""); if (!seen.has(key)) { seen.add(key); rows.push(x); } }
    }
    const top = rows.slice(0, TARGET_ROWS);

    // 3) Sinh câu trả lời
    const augmented = messages.slice();
    augmented[augmented.length - 1] = { role: "user", content: `NGỮ CẢNH PHÁP LUẬT (trích dẫn theo số [n]):\n\n${buildContext(top)}\n\n---\nCÂU HỎI: ${userQuery}` };
    const { text: reply, model: usedModel } = await gemini(apiKey, ANSWER_SYSTEM, augmented, MAX_TOKENS, ANSWER_ORDER);
    logAI(userQuery, body.lang, top.length, usedModel);
    return send(res, 200, { reply: reply || "Tôi chưa tìm thấy quy định cụ thể trong dữ liệu tra cứu. Vui lòng liên hệ trực tiếp để được tư vấn.", sources: top.map(x => ({ citation: x.citation, url: x.url, kind: x.kind })), model: usedModel });
  } catch (e) {
    console.error("chat handler error", e.message);
    const msg = e.status === 429 ? "Trợ lý đang quá tải, vui lòng thử lại sau ít phút." : "Có lỗi xảy ra. Vui lòng thử lại sau.";
    return send(res, 502, { error: "upstream", reply: msg });
  }
};
