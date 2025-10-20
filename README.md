# 採用書類選考アプリ

マインドセット評価を中心とした、書類選考から面接評価までの採用プロセス自動化システム

## 技術スタック

- **バックエンド**: FastAPI (Python)
- **フロントエンド**: React
- **データベース**: Supabase (PostgreSQL)
- **AI**: Google Cloud AI (Vision API, Gemini, Speech-to-Text)

## 主な機能

### 1. 書類処理
- PDF OCR解析（Google Vision API）
- 応募者情報の自動抽出・構造化

### 2. AI評価
- スキル + マインドセット分析
- 評価比率調整機能（初期値: スキル20%, マインド80%）

### 3. 面接管理
- マインドセット重視の一次面接質問自動生成
- 音声文字起こし・要約機能

### 4. 並列処理
- CSV一括処理によるバッチ評価

### 5. 自動化
- Google Calendar連携（日程調整）

## プロジェクト構造

```
recruitment-app/
├── backend/          # FastAPI バックエンド
│   ├── app/
│   │   ├── main.py
│   │   ├── api/      # APIルート
│   │   ├── models/   # データモデル
│   │   ├── services/ # ビジネスロジック
│   │   └── utils/    # ユーティリティ
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # React フロントエンド
└── docs/            # ドキュメント
```

## セットアップ

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 環境変数を設定
uvicorn app.main:app --reload
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

## 環境変数

`.env.example`を参照して、以下の環境変数を設定してください：

- `SUPABASE_URL`: SupabaseプロジェクトURL
- `SUPABASE_KEY`: Supabaseアクセスキー
- `GOOGLE_CLOUD_PROJECT_ID`: Google CloudプロジェクトID
- `GOOGLE_APPLICATION_CREDENTIALS`: Google Cloud認証情報ファイルパス
- `DEFAULT_SKILL_RATIO`: スキル評価比率（デフォルト: 0.2）
- `DEFAULT_MINDSET_RATIO`: マインドセット評価比率（デフォルト: 0.8）

## ライセンス

MIT

## 起動方法（ポート競合回避版）

### バックエンド
```bash
cd backend
uvicorn app.main:app --reload --port 8001
```
→ http://localhost:8001 で起動

### フロントエンド
```bash
cd frontend
npm run dev
```
→ http://localhost:3001 で起動

詳細は `START.md` を参照してください。
