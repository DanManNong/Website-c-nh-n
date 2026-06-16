-- ============================================================
-- RAG Pháp lý: PGroonga index + RPC tìm kiếm
-- Áp dụng SAU khi đã nạp dữ liệu vào bảng `phapdien` và `anle`.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgroonga;

-- 1) Khoá chính (duckdb tạo bảng không có PK)
ALTER TABLE phapdien ADD COLUMN IF NOT EXISTS id bigint GENERATED ALWAYS AS IDENTITY;
ALTER TABLE anle     ADD COLUMN IF NOT EXISTS id bigint GENERATED ALWAYS AS IDENTITY;

-- 2) PGroonga full-text index (tiếng Việt) — multicolumn, không index cột markdown khổng lồ
CREATE INDEX IF NOT EXISTS idx_phapdien_ft ON phapdien USING pgroonga (article_title, content_text);
CREATE INDEX IF NOT EXISTS idx_anle_ft     ON anle     USING pgroonga (title, subject, principle_text);

-- 3) RLS: khoá truy cập trực tiếp; chỉ cho phép qua RPC (SECURITY DEFINER)
ALTER TABLE phapdien ENABLE ROW LEVEL SECURITY;
ALTER TABLE anle     ENABLE ROW LEVEL SECURITY;
-- (không tạo policy => không ai SELECT trực tiếp được; RPC bên dưới bỏ qua RLS)

-- 4) RPC tìm kiếm: trả top-k điều luật + top-k án lệ liên quan
CREATE OR REPLACE FUNCTION phaply_search(q text, k int DEFAULT 6)
RETURNS TABLE(kind text, citation text, title text, snippet text, url text)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  (SELECT 'phapdien'::text AS kind,
          p.article_anchor AS citation,
          coalesce(p.subject_title,'') || ' — ' || coalesce(p.article_title,'') AS title,
          left(p.content_text, 1200) AS snippet,
          p.source_url AS url
   FROM phapdien p
   WHERE p.article_title &@~ q OR p.content_text &@~ q
   ORDER BY pgroonga_score(p.tableoid, p.ctid) DESC
   LIMIT greatest(1, least(k, 10)))
  UNION ALL
  (SELECT 'anle'::text AS kind,
          coalesce(a.precedent_number, a.doc_code) AS citation,
          coalesce(a.title,'') AS title,
          left(coalesce(nullif(a.principle_text,''), a.markdown), 1200) AS snippet,
          coalesce(a.detail_url, a.pdf_url) AS url
   FROM anle a
   WHERE a.title &@~ q OR a.subject &@~ q OR a.principle_text &@~ q
   ORDER BY pgroonga_score(a.tableoid, a.ctid) DESC
   LIMIT greatest(1, least(k, 10)));
$$;

-- Cho phép anon (publishable key) gọi RPC
GRANT EXECUTE ON FUNCTION phaply_search(text, int) TO anon, authenticated;
