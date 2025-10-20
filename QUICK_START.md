# クイックスタートガイド

## 🎉 アプリケーションが起動しました！

現在、以下のURLでアクセスできます：

- **バックエンドAPI**: http://localhost:8001
- **APIドキュメント**: http://localhost:8001/docs
- **フロントエンド**: http://localhost:3001

## 📋 現在の状態

### ✅ 完了したこと

1. プロジェクト構造の作成
2. バックエンド（FastAPI）のインストール
3. フロントエンド（React + Vite）のインストール
4. バックエンドサーバーの起動
5. フロントエンドサーバーの起動

### ⚠️ 次に必要な設定

フル機能を使用するには、以下の設定が必要です：

#### 1. Google Cloud設定

1. **Google Cloud プロジェクト作成**
   - https://console.cloud.google.com/ にアクセス
   - 新しいプロジェクトを作成

2. **APIの有効化**
   ```bash
   gcloud services enable vision.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable calendar-json.googleapis.com
   ```

3. **サービスアカウント作成**
   - IAM > サービスアカウント > 作成
   - 権限を付与：
     - Cloud Vision API ユーザー
     - Vertex AI ユーザー
     - Cloud Calendar API ユーザー
   - JSONキーをダウンロード
   - `backend/credentials.json` として保存

4. **環境変数を更新**
   `backend/.env` を編集：
   ```env
   GOOGLE_CLOUD_PROJECT_ID=実際のプロジェクトID
   GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
   ```

#### 2. Supabase設定

1. **Supabaseプロジェクト作成**
   - https://supabase.com/ にアクセス
   - 新しいプロジェクトを作成

2. **データベーススキーマ作成**
   - Supabase ダッシュボード > SQL Editor
   - `docs/supabase-schema.sql` の内容を実行

3. **ストレージバケット作成**
   - Storage > New Bucket
   - 名前: `applicant-documents`
   - 公開設定: Private

4. **環境変数を更新**
   `backend/.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key
   ```

   `frontend/.env`:
   ```env
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_KEY=your_anon_key
   VITE_API_URL=http://localhost:8001
   ```

#### 3. フル機能版の起動

設定完了後、フル機能版を起動：

```bash
# バックエンド（既存のサーバーを停止してから）
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 🚀 現在の起動コマンド

### バックエンド（シンプル版）
```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8001 --reload
```

### フロントエンド
```bash
cd frontend
npm run dev
```

## 📚 主な機能

### 実装済み

1. **PDF OCR処理** - Google Vision API
2. **AI評価エンジン** - スキル＋マインドセット分析（Gemini）
3. **評価比率調整** - スライダーでスキル/マインド比率変更
4. **面接質問生成** - マインドセット重視の質問自動生成
5. **バッチ処理** - CSV一括アップロード・評価
6. **Google Calendar連携** - 面接スケジュール自動化

### UIコンポーネント

- ダッシュボード
- 応募者一覧（フィルタリング・検索機能付き）
- 応募者詳細・評価画面
- バッチアップロード画面

## 🔍 動作確認

### 1. バックエンドAPI
http://localhost:8001 にアクセス

レスポンス例：
```json
{
  "message": "採用書類選考API",
  "version": "1.0.0",
  "docs": "/docs",
  "note": "Google Cloud認証情報を設定してフル機能を使用してください"
}
```

### 2. APIドキュメント
http://localhost:8001/docs でSwagger UIを確認

### 3. フロントエンド
http://localhost:3001 でReactアプリにアクセス

## 📖 詳細ドキュメント

- `docs/setup-guide.md` - 詳細なセットアップ手順
- `docs/api-usage-guide.md` - API使用方法
- `docs/development-guide.md` - 開発ガイド
- `README.md` - プロジェクト概要

## 🛠️ トラブルシューティング

### ポート競合
他のアプリケーションが既に8001または3001ポートを使用している場合：

バックエンド:
```bash
uvicorn app.main_simple:app --port 8002 --reload
```

フロントエンド:
```bash
npm run dev -- --port 3002
```

### サーバー停止方法
バックグラウンドで起動している場合、ターミナルで `Ctrl+C` を押す

### 再起動
設定変更後は両方のサーバーを再起動してください

## 💡 次のステップ

1. Google Cloud認証情報を設定
2. Supabaseプロジェクトを作成
3. データベーススキーマを実行
4. フル機能版でアプリを起動
5. テストデータで動作確認

## 📞 サポート

問題が発生した場合：
1. `docs/setup-guide.md` を確認
2. エラーメッセージを確認
3. 環境変数が正しく設定されているか確認
