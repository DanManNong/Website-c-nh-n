// Vercel Serverless Function — Trợ lý AI Pháp lý (RAG) cho nguyentanphong.com
// LLM: Google Gemini 2.5 Flash. Luồng: (1) viết lại câu hỏi -> cụm từ khoá;
//      (2) tìm Pháp điển + Án lệ (Supabase PGroonga, phrase); (3) trả lời kèm trích dẫn.
// ENV bắt buộc (đặt trên Vercel): GEMINI_API_KEY

const MODEL = "gemini-2.5-flash";
const MAX_TOKENS = 1100;
const MAX_MSG = 12;
const MAX_CHARS = 2000;
const TARGET_ROWS = 7;

const SUPABASE_URL = process.env.SUPABASE_URL || "https://dcmtbgcltopnqsiedwlg.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY || "sb_publishable_goPNlFYvQUspbFSvDzkN3w_KMapxvUq";
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;

const ANSWER_SYSTEM = `Bạn là Trợ lý AI Pháp lý trên website của ông Nguyễn Tấn Phong — Phó Chủ tịch Hiệp hội Thương mại điện tử Việt Nam (VECOM), chuyên gia Kinh tế số & Pháp luật.

Trả lời câu hỏi pháp luật Việt Nam DỰA TRÊN NGỮ CẢNH (điều luật Pháp điển + án lệ) cung cấp bên dưới.

QUY TẮC:
- CHỈ dùng NGỮ CẢNH để nêu nội dung pháp luật. Nếu ngữ cảnh không đủ/không liên quan, nói rõ "Tôi chưa tìm thấy quy định cụ thể trong dữ liệu tra cứu" và gợi ý liên hệ ông Phong qua form/Zalo trên trang.
- TUYỆT ĐỐI KHÔNG bịa số điều, tên văn bản, nội dung. Luôn TRÍCH DẪN mã điều/số án lệ theo [n] và kèm link nếu có.
- Trả lời bằng ĐÚNG ngôn ngữ người dùng. Ngắn gọn, có cấu trúc.
- Kết thúc bằng 1 dòng nhắc: thông tin mang tính tham khảo, không thay thế tư vấn pháp lý chính thức; vụ việc cụ thể nên liên hệ ông Phong.
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

// Gọi Gemini. messages: [{role:'user'|'assistant', content}]. thinking tắt để rẻ/nhanh.
async function gemini(apiKey, system, messages, maxTokens) {
  const contents = messages.map(m => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.content }] }));
  const r = await fetch(GEMINI_ENDPOINT, {
    method: "POST",
    headers: { "x-goog-api-key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({
      systemInstruction: { parts: [{ text: system }] },
      contents,
      generationConfig: { maxOutputTokens: maxTokens, temperature: 0.3, thinkingConfig: { thinkingBudget: 0 } },
    }),
  });
  if (!r.ok) { const t = await r.text().catch(() => ""); const e = new Error("gemini " + r.status + " " + t); e.status = r.status; throw e; }
  const data = await r.json();
  const cand = data && data.candidates && data.candidates[0];
  if (!cand || !cand.content || !Array.isArray(cand.content.parts)) return "";
  return cand.content.parts.filter(p => p && p.text).map(p => p.text).join("").trim();
}

async function rewriteQueries(apiKey, history) {
  try {
    const txt = await gemini(apiKey, REWRITE_SYSTEM, history, 120);
    const lines = txt.split("\n").map(s => s.replace(/^[-*\d.)\s"]+/, "").replace(/["]+$/, "").trim()).filter(s => s.length >= 2 && s.length <= 80);
    if (lines.length === 1 && lines[0].toUpperCase() === "NONE") return [];
    return lines.slice(0, 3);
  } catch (e) { console.error("rewrite err", e.message); return []; }
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

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "method_not_allowed" });
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
    const reply = await gemini(apiKey, ANSWER_SYSTEM, augmented, MAX_TOKENS);
    return send(res, 200, { reply: reply || "Tôi chưa tìm thấy quy định cụ thể trong dữ liệu tra cứu. Vui lòng liên hệ trực tiếp để được tư vấn.", sources: top.map(x => ({ citation: x.citation, url: x.url, kind: x.kind })) });
  } catch (e) {
    console.error("chat handler error", e.message);
    const msg = e.status === 429 ? "Trợ lý đang quá tải, vui lòng thử lại sau ít phút." : "Có lỗi xảy ra. Vui lòng thử lại sau.";
    return send(res, 502, { error: "upstream", reply: msg });
  }
};
