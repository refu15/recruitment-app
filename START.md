# 起動方法

## ポート設定

- バックエンド: http://localhost:8001
- フロントエンド: http://localhost:3001

## バックエンド起動

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

起動後、以下にアクセス可能：
- API: http://localhost:8001
- APIドキュメント: http://localhost:8001/docs

## フロントエンド起動（別のターミナル）

```bash
cd frontend
npm install
npm run dev
```

起動後、以下にアクセス：
- アプリ: http://localhost:3001

## 注意事項

1. **環境変数設定**
   - `backend/.env` にGoogle Cloud、Supabaseの設定を追加
   - `frontend/.env` にSupabase URLとキーを設定

2. **Supabaseセットアップ**
   - `docs/supabase-schema.sql` を実行してテーブル作成

3. **Google Cloud設定**
   - サービスアカウントのJSONキーを `backend/credentials.json` に配置
   - Vision API、Vertex AI API を有効化

詳細は `docs/setup-guide.md` を参照してください。
