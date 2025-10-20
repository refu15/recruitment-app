-- 採用書類選考アプリ Supabase スキーマ定義

-- 応募者テーブル
CREATE TABLE IF NOT EXISTS public.applicants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,

    -- 基本情報
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,

    -- 応募書類
    resume_url TEXT,
    cover_letter TEXT,

    -- 構造化データ（JSONB）
    applicant_data JSONB,
    -- {
    --   "name": "氏名",
    --   "email": "メール",
    --   "phone": "電話",
    --   "education": [...],
    --   "work_experience": [...],
    --   "technical_skills": [...],
    --   "soft_skills": [...],
    --   "certifications": [...],
    --   "motivation": "志望動機",
    --   "career_goals": "キャリア目標",
    --   "additional_info": "その他",
    --   "extracted_text": "抽出テキスト",
    --   "ocr_confidence": 0.0
    -- }

    -- 評価結果（JSONB）
    evaluation JSONB,
    -- {
    --   "skill_evaluations": [...],
    --   "mindset_evaluations": [...],
    --   "skill_score": 0.0,
    --   "mindset_score": 0.0,
    --   "total_score": 0.0,
    --   "skill_ratio": 0.2,
    --   "mindset_ratio": 0.8,
    --   "summary": "評価サマリー",
    --   "strengths": [...],
    --   "concerns": [...]
    -- }

    -- ステータス
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'screening', 'interview', 'passed', 'rejected')),

    -- 面接
    interview_questions TEXT[],
    interview_transcript TEXT,
    interview_summary TEXT,

    -- メタデータ
    tags TEXT[],
    notes TEXT
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_applicants_email ON public.applicants(email);
CREATE INDEX IF NOT EXISTS idx_applicants_status ON public.applicants(status);
CREATE INDEX IF NOT EXISTS idx_applicants_created_at ON public.applicants(created_at DESC);

-- 評価スコアでのフィルタリング用インデックス（JSONB）
CREATE INDEX IF NOT EXISTS idx_applicants_total_score ON public.applicants((evaluation->>'total_score'));

-- 更新日時の自動更新トリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_applicants_updated_at BEFORE UPDATE ON public.applicants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ストレージバケット作成（履歴書等のファイル保存用）
-- Supabase管理画面で以下のバケットを作成してください：
-- バケット名: applicant-documents
-- 公開設定: Private（認証ユーザーのみアクセス可能）

-- Row Level Security (RLS) ポリシー
-- 本番環境では適切な認証・認可ポリシーを設定してください
ALTER TABLE public.applicants ENABLE ROW LEVEL SECURITY;

-- 開発用: 全ユーザーが読み書き可能（本番環境では削除すること）
CREATE POLICY "Enable all access for development" ON public.applicants
    FOR ALL USING (true) WITH CHECK (true);

-- 本番用ポリシー例（コメントアウト）
-- CREATE POLICY "Enable read access for authenticated users" ON public.applicants
--     FOR SELECT USING (auth.role() = 'authenticated');
--
-- CREATE POLICY "Enable insert access for authenticated users" ON public.applicants
--     FOR INSERT WITH CHECK (auth.role() = 'authenticated');
--
-- CREATE POLICY "Enable update access for authenticated users" ON public.applicants
--     FOR UPDATE USING (auth.role() = 'authenticated');
--
-- CREATE POLICY "Enable delete access for authenticated users" ON public.applicants
--     FOR DELETE USING (auth.role() = 'authenticated');

-- サンプルデータ（開発用）
-- INSERT INTO public.applicants (name, email, phone, status)
-- VALUES
--     ('山田太郎', 'taro.yamada@example.com', '090-1234-5678', 'pending'),
--     ('佐藤花子', 'hanako.sato@example.com', '080-9876-5432', 'screening');
