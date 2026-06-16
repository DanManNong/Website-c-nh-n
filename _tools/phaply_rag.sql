-- ============================================================
-- RAG Pháp lý — schema ĐÃ ÁP DỤNG trên Supabase (dcmtbgcltopnqsiedwlg)
-- Dữ liệu nạp bằng duckdb (xem _tools/load_rag.md). Đây là phần index + RPC.
-- LƯU Ý QUAN TRỌNG: cột tìm kiếm phải là TEXT (không phải varchar) thì
-- PGroonga mới dùng opclass full-text mặc định cho toán tử &@~.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgroonga;

-- 1) Cột tìm kiếm: varchar -> text (bắt buộc để &@~ dùng được index)
ALTER TABLE public.phapdien
  ALTER COLUMN content_text  TYPE text,
  ALTER COLUMN article_title TYPE text,
  ALTER COLUMN subject_title TYPE text;
ALTER TABLE public.anle
  ALTER COLUMN title          TYPE text,
  ALTER COLUMN subject        TYPE text,
  ALTER COLUMN principle_text TYPE text,
  ALTER COLUMN markdown       TYPE text;

-- 2) PGroonga full-text index — ĐƠN CỘT (multicolumn không phục vụ query 1 cột)
CREATE INDEX IF NOT EXISTS idx_phapdien_content ON public.phapdien USING pgroonga (content_text);
CREATE INDEX IF NOT EXISTS idx_phapdien_title   ON public.phapdien USING pgroonga (article_title);
CREATE INDEX IF NOT EXISTS idx_anle_principle   ON public.anle     USING pgroonga (principle_text);
CREATE INDEX IF NOT EXISTS idx_anle_title       ON public.anle     USING pgroonga (title);

-- 3) RLS: khoá truy cập trực tiếp, chỉ cho qua RPC (SECURITY DEFINER)
ALTER TABLE public.phapdien ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.anle     ENABLE ROW LEVEL SECURITY;

-- 4) RPC tìm kiếm: top-k điều luật + top-k án lệ. citation = mã "Điều X" tách từ article_title.
CREATE OR REPLACE FUNCTION public.phaply_search(q text, k int DEFAULT 6)
RETURNS TABLE(kind text, citation text, title text, snippet text, url text)
LANGUAGE sql SECURITY DEFINER SET search_path = public
SET statement_timeout = '12s' AS $$
  (SELECT 'phapdien'::text,
          coalesce(nullif(rtrim(substring(p.article_title from '^Điều \S+'),'.'),''),'Pháp điển'),
          coalesce(p.subject_title,'')||' — '||coalesce(p.article_title,''),
          left(p.content_text,1200), p.source_url
   FROM phapdien p WHERE p.content_text &@~ q OR p.article_title &@~ q
   ORDER BY pgroonga_score(p.tableoid,p.ctid) DESC LIMIT greatest(1,least(k,10)))
  UNION ALL
  (SELECT 'anle'::text, coalesce(a.precedent_number,a.doc_code,'Án lệ'), coalesce(a.title,''),
          left(coalesce(nullif(a.principle_text,''),a.markdown),1200), coalesce(a.detail_url,a.pdf_url)
   FROM anle a WHERE a.principle_text &@~ q OR a.title &@~ q OR a.subject &@~ q
   ORDER BY pgroonga_score(a.tableoid,a.ctid) DESC LIMIT greatest(1,least(k,10)));
$$;

GRANT EXECUTE ON FUNCTION public.phaply_search(text,int) TO anon, authenticated;
