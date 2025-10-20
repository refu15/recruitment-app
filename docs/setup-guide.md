# セットアップガイド

## 前提条件

- Python 3.10以上
- Node.js 18以上
- Google Cloud アカウント
- Supabase アカウント

## 1. Google Cloud セットアップ

### 1.1 プロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. プロジェクトIDをメモ

### 1.2 API有効化

以下のAPIを有効化します：

- Cloud Vision API（OCR用）
- Vertex AI API（Gemini用）
- Cloud Speech-to-Text API（音声文字起こし用）※将来使用
- Google Calendar API（日程調整用）

```bash
gcloud services enable vision.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable speech.googleapis.com
gcloud services enable calendar-json.googleapis.com
```

### 1.3 サービスアカウント作成

1. Google Cloud Console > IAM > サービスアカウント
2. 「サービスアカウントを作成」をクリック
3. 必要な権限を付与：
   - Cloud Vision API ユーザー
   - Vertex AI ユーザー
   - Cloud Speech-to-Text API ユーザー
4. JSONキーをダウンロード
5. ダウンロードしたJSONファイルを`backend/credentials.json`として保存

## 2. Supabase セットアップ

### 2.1 プロジェクト作成

1. [Supabase](https://supabase.com/) にアクセス
2. 新しいプロジェクトを作成
3. データベースパスワードを設定（メモしておく）

### 2.2 データベーススキーマ作成

1. Supabase ダッシュボード > SQL Editor
2. `docs/supabase-schema.sql`の内容をコピー＆実行
3. テーブルが正しく作成されたことを確認

### 2.3 ストレージバケット作成

1. Supabase ダッシュボード > Storage
2. 新しいバケット「applicant-documents」を作成
3. 公開設定: Private（認証ユーザーのみ）

### 2.4 API情報取得

1. Supabase ダッシュボード > Settings > API
2. 以下をメモ：
   - Project URL
   - `anon` public key

## 3. バックエンドセットアップ

### 3.1 環境変数設定

```bash
cd backend
cp .env.example .env
```

`.env`ファイルを編集：

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json

# 評価設定
DEFAULT_SKILL_RATIO=0.2
DEFAULT_MINDSET_RATIO=0.8

# セキュリティ
SECRET_KEY=your_random_secret_key_here
```

`SECRET_KEY`の生成：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3.2 依存関係インストール

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3.3 サーバー起動

```bash
uvicorn app.main:app --reload
```

サーバーが起動したら、以下にアクセス：

- API: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## 4. フロントエンドセットアップ

### 4.1 依存関係インストール

```bash
cd frontend
npm install
```

### 4.2 追加パッケージインストール

```bash
npm install @supabase/supabase-js
npm install react-router-dom
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install axios
npm install recharts
```

### 4.3 環境変数設定

`frontend/.env`ファイルを作成：

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your_anon_key
VITE_API_URL=http://localhost:8000
```

### 4.4 開発サーバー起動

```bash
npm run dev
```

フロントエンドが起動したら、以下にアクセス：
http://localhost:5173

## 5. 動作確認

### 5.1 バックエンド動作確認

1. http://localhost:8000/docs にアクセス
2. `/health` エンドポイントをテスト
3. `/api/applicants/` で応募者一覧を取得（空配列が返る）

### 5.2 フロントエンド動作確認

1. http://localhost:5173 にアクセス
2. 画面が正しく表示されることを確認

### 5.3 統合テスト

1. フロントエンドから応募者を新規作成
2. PDFアップロード（テスト用PDFを用意）
3. OCR処理実行
4. AI評価実行
5. 面接質問生成

## トラブルシューティング

### Google Cloud認証エラー

- `GOOGLE_APPLICATION_CREDENTIALS`のパスが正しいか確認
- サービスアカウントに必要な権限があるか確認
- APIが有効化されているか確認

### Supabase接続エラー

- URLとキーが正しいか確認
- RLSポリシーが正しく設定されているか確認
- ネットワーク接続を確認

### ポート競合エラー

バックエンドのポートを変更：
```bash
uvicorn app.main:app --reload --port 8001
```

フロントエンドのポートを変更：
```bash
npm run dev -- --port 3000
```

## 本番環境デプロイ

### バックエンド（例: Render, Railway）

1. リポジトリをGitHubにプッシュ
2. Renderでサービスを作成
3. 環境変数を設定
4. デプロイ

### フロントエンド（例: Vercel, Netlify）

1. リポジトリをGitHubにプッシュ
2. Vercelでプロジェクトをインポート
3. 環境変数を設定
4. デプロイ

### 重要な本番環境設定

1. **Supabase RLSポリシー更新**
   - 開発用ポリシーを削除
   - 適切な認証・認可ポリシーを設定

2. **CORS設定**
   - `backend/app/main.py`でallow_originsを本番URLに変更

3. **環境変数**
   - SECRET_KEYを強力なものに変更
   - 本番環境のURLを設定

4. **Google Cloud**
   - 本番環境IPを許可リストに追加
   - クォータ設定を確認
