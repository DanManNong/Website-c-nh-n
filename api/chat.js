// Vercel Serverless Function — Trợ lý AI Pháp lý (RAG) cho nguyentanphong.com
// Luồng: tìm kiếm Pháp điển + Án lệ trên Supabase (PGroonga) -> đưa vào prompt -> Claude trả lời kèm trích dẫn.
// Biến môi trường BẮT BUỘC (đặt trên Vercel): ANTHROPIC_API_KEY
// (Supabase URL + publishable key là công khai nên để mặc định; có thể override bằng env.)

const MODEL = "claude-haiku-4-5-20251001"; // đổi sang claude-sonnet-4-6 nếu cần chất lượng cao hơn
const MAX_TOKENS = 900;
const MAX_MSG = 12;
const MAX_CHARS = 2000;
const TOP_K = 6; // số điều luật/án lệ lấy mỗi nguồn

const SUPABASE_URL = process.env.SUPABASE_URL || "https://dcmtbgcltopnqsiedwlg.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY || "sb_publishable_goPNlFYvQUspbFSvDzkN3w_KMapxvUq";

const SYSTEM_PROMPT = `Bạn là Trợ lý AI Pháp lý trên website của ông Nguyễn Tấn Phong — Phó Chủ tịch Hiệp hội Thương mại điện tử Việt Nam (VECOM), chuyên gia Kinh tế số & Pháp luật.

NHIỆM VỤ: Trả lời câu hỏi pháp luật Việt Nam dựa trên NGỮ CẢNH (điều luật trong Pháp điển và Án lệ) được cung cấp bên dưới mỗi câu hỏi.

QUY TẮC BẮT BUỘC:
- CHỈ dựa vào NGỮ CẢNH được cung cấp để trả lời về nội dung pháp luật. Nếu ngữ cảnh không đủ, nói rõ "Tôi chưa tìm thấy quy định cụ thể trong dữ liệu" và gợi ý người dùng liên hệ trực tiếp ông Phong qua form/Zalo trên trang.
- TUYỆT ĐỐI KHÔNG bịa số điều, tên văn bản, hay nội dung không có trong ngữ cảnh.
- Luôn TRÍCH DẪN nguồn: ghi mã điều (article_anchor) hoặc số án lệ, kèm link nguồn nếu có.
- Trả lời bằng ĐÚNG ngôn ngữ người dùng. Ngắn gọn, rõ ràng, có cấu trúc (gạch đầu dòng khi cần).
- Cuối câu trả lời pháp lý, thêm dòng nhắc: thông tin mang tính tham khảo, không thay thế tư vấn pháp lý chính thức; với vụ việc cụ thể nên liên hệ ông Phong để được tư vấn.
- Lịch sự từ chối nội dung ngoài phạm vi pháp luật/chuyên môn.`;

function send(res, status, obj) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(obj));
}

async function searchLaw(query) {
  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/rpc/phaply_search`, {
      method: "POST",
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ q: query, k: TOP_K }),
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
    const cite = x.citation || "";
    const title = x.title || "";
    const body = (x.snippet || "").slice(0, 900);
    const url = x.url ? `\nNguồn: ${x.url}` : "";
    return `[${i + 1}] (${kind}) ${cite} — ${title}\n${body}${url}`;
  }).join("\n\n");
}

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "method_not_allowed" });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return send(res, 503, { error: "not_configured", reply: "Trợ lý AI đang được cấu hình. Vui lòng liên hệ trực tiếp qua Zalo/điện thoại trên trang." });

  let body = req.body;
  try {
    if (!body) {
      const raw = await new Promise((resolve, reject) => { let d = ""; req.on("data", c => (d += c)); req.on("end", () => resolve(d)); req.on("error", reject); });
      body = raw ? JSON.parse(raw) : {};
    } else if (typeof body === "string") { body = JSON.parse(body); }
  } catch (e) { return send(res, 400, { error: "bad_json" }); }

  let messages = Array.isArray(body && body.messages) ? body.messages : [];
  messages = messages
    .filter(m => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string" && m.content.trim())
    .slice(-MAX_MSG)
    .map(m => ({ role: m.role, content: String(m.content).slice(0, MAX_CHARS) }));
  if (!messages.length || messages[messages.length - 1].role !== "user") return send(res, 400, { error: "no_user_message" });

  const userQuery = messages[messages.length - 1].content;

  // 1) RAG retrieval
  const rows = await searchLaw(userQuery);
  const context = buildContext(rows);

  // 2) Ghép ngữ cảnh vào tin nhắn cuối của người dùng
  const augmented = messages.slice();
  augmented[augmented.length - 1] = {
    role: "user",
    content: `NGỮ CẢNH PHÁP LUẬT (dùng để trả lời, trích dẫn theo số [n]):\n\n${context}\n\n---\nCÂU HỎI: ${userQuery}`,
  };

  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        system: [{ type: "text", text: SYSTEM_PROMPT, cache_control: { type: "ephemeral" } }],
        messages: augmented,
      }),
    });
    if (!r.ok) {
      console.error("Anthropic API error", r.status, await r.text().catch(() => ""));
      return send(res, 502, { error: "upstream", reply: "Xin lỗi, trợ lý đang bận. Vui lòng thử lại sau ít phút." });
    }
    const data = await r.json();
    const reply = Array.isArray(data.content) ? data.content.filter(b => b.type === "text").map(b => b.text).join("\n").trim() : "";
    return send(res, 200, { reply: reply || "…", sources: rows.map(x => ({ citation: x.citation, url: x.url, kind: x.kind })) });
  } catch (e) {
    console.error("chat handler error", e);
    return send(res, 500, { error: "server_error", reply: "Có lỗi xảy ra. Vui lòng thử lại sau." });
  }
};
