// Vercel Serverless Function — Trợ lý AI Pháp lý (RAG) cho nguyentanphong.com
// Luồng: (1) Claude viết lại câu hỏi -> cụm từ khoá tra cứu; (2) tìm Pháp điển + Án lệ (PGroonga, phrase);
//        (3) Claude trả lời dựa trên ngữ cảnh, kèm trích dẫn.
// ENV bắt buộc (đặt trên Vercel): ANTHROPIC_API_KEY

const MODEL = "claude-haiku-4-5-20251001"; // đổi sang claude-sonnet-4-6 nếu cần chất lượng cao hơn
const MAX_TOKENS = 1000;
const MAX_MSG = 12;
const MAX_CHARS = 2000;
const TARGET_ROWS = 7;

const SUPABASE_URL = process.env.SUPABASE_URL || "https://dcmtbgcltopnqsiedwlg.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY || "sb_publishable_goPNlFYvQUspbFSvDzkN3w_KMapxvUq";

const ANSWER_SYSTEM = `Bạn là Trợ lý AI Pháp lý trên website của ông Nguyễn Tấn Phong — Phó Chủ tịch Hiệp hội Thương mại điện tử Việt Nam (VECOM), chuyên gia Kinh tế số & Pháp luật.

Trả lời câu hỏi pháp luật Việt Nam DỰA TRÊN NGỮ CẢNH (điều luật Pháp điển + án lệ) cung cấp bên dưới.

QUY TẮC:
- CHỈ dùng NGỮ CẢNH để nêu nội dung pháp luật. Nếu ngữ cảnh không đủ/không liên quan, nói rõ "Tôi chưa tìm thấy quy định cụ thể trong dữ liệu tra cứu" và gợi ý liên hệ ông Phong qua form/Zalo trên trang.
- TUYỆT ĐỐI KHÔNG bịa số điều, tên văn bản, nội dung. Luôn TRÍCH DẪN mã điều/số án lệ theo [n] và kèm link nếu có.
- Trả lời bằng ĐÚNG ngôn ngữ người dùng. Ngắn gọn, có cấu trúc.
- Kết thúc bằng 1 dòng nhắc: thông tin mang tính tham khảo, không thay thế tư vấn pháp lý chính thức; vụ việc cụ thể nên liên hệ ông Phong.
- Lịch sự từ chối nội dung ngoài phạm vi pháp luật.`;

function send(res, status, obj) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(obj));
}

async function claude(apiKey, system, messages, maxTokens) {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({
      model: MODEL, max_tokens: maxTokens,
      system: [{ type: "text", text: system, cache_control: { type: "ephemeral" } }],
      messages,
    }),
  });
  if (!r.ok) { const t = await r.text().catch(() => ""); const e = new Error("anthropic " + r.status + " " + t); e.status = r.status; throw e; }
  const data = await r.json();
  return Array.isArray(data.content) ? data.content.filter(b => b.type === "text").map(b => b.text).join("\n").trim() : "";
}

// Bước 1: viết lại câu hỏi -> 2-3 cụm từ khoá pháp lý (cụ thể -> rộng)
async function rewriteQueries(apiKey, history) {
  const sys = `Bạn tạo TRUY VẤN TÌM KIẾM cho cơ sở dữ liệu pháp luật Việt Nam. Dựa vào hội thoại, hãy đưa ra 2-3 cụm từ khoá pháp lý (cụm danh từ), xếp từ CỤ THỂ đến RỘNG, mỗi cụm trên 1 dòng. KHÔNG giải thích, KHÔNG đánh số, KHÔNG dấu ngoặc, không stopword. Nếu câu hỏi không liên quan pháp luật, trả về 1 dòng: NONE`;
  try {
    const txt = await claude(apiKey, sys, history, 80);
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
  const apiKey = process.env.ANTHROPIC_API_KEY;
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
      const phrase = /\s/.test(q) ? `"${q}"` : q; // nhiều từ -> phrase
      const r = await searchLaw(phrase, 5);
      for (const x of r) { const key = (x.kind || "") + "|" + (x.citation || "") + "|" + (x.title || ""); if (!seen.has(key)) { seen.add(key); rows.push(x); } }
    }
    // fallback: chưa đủ -> tìm OR theo câu hỏi gốc
    if (rows.length < 3) {
      const r = await searchLaw(userQuery, 6);
      for (const x of r) { const key = (x.kind || "") + "|" + (x.citation || "") + "|" + (x.title || ""); if (!seen.has(key)) { seen.add(key); rows.push(x); } }
    }
    const top = rows.slice(0, TARGET_ROWS);

    // 3) Sinh câu trả lời
    const augmented = messages.slice();
    augmented[augmented.length - 1] = { role: "user", content: `NGỮ CẢNH PHÁP LUẬT (trích dẫn theo số [n]):\n\n${buildContext(top)}\n\n---\nCÂU HỎI: ${userQuery}` };
    const reply = await claude(apiKey, ANSWER_SYSTEM, augmented, MAX_TOKENS);
    return send(res, 200, { reply: reply || "…", sources: top.map(x => ({ citation: x.citation, url: x.url, kind: x.kind })) });
  } catch (e) {
    console.error("chat handler error", e.message);
    const code = e.status === 429 ? "Trợ lý đang quá tải, vui lòng thử lại sau ít phút." : "Có lỗi xảy ra. Vui lòng thử lại sau.";
    return send(res, 502, { error: "upstream", reply: code });
  }
};
