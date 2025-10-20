# 開発ガイド

## プロジェクト構造

```
recruitment-app/
├── backend/                    # FastAPI バックエンド
│   ├── app/
│   │   ├── main.py            # アプリケーションエントリーポイント
│   │   ├── api/               # APIルート
│   │   │   ├── applicants.py  # 応募者CRUD
│   │   │   ├── evaluation.py  # 評価API
│   │   │   ├── interview.py   # 面接API
│   │   │   ├── batch.py       # バッチ処理
│   │   │   └── calendar.py    # カレンダー連携
│   │   ├── models/            # データモデル
│   │   │   └── applicant.py   # 応募者モデル
│   │   ├── services/          # ビジネスロジック
│   │   │   ├── ocr_service.py           # OCR処理
│   │   │   ├── ai_evaluation_service.py # AI評価
│   │   │   ├── interview_service.py     # 面接質問生成
│   │   │   └── calendar_service.py      # カレンダー操作
│   │   └── utils/             # ユーティリティ
│   │       ├── config.py      # 設定管理
│   │       └── supabase_client.py # Supabase接続
│   ├── requirements.txt       # Python依存関係
│   └── .env.example          # 環境変数テンプレート
│
├── frontend/                  # React フロントエンド
│   ├── src/
│   │   ├── App.jsx           # メインアプリ
│   │   ├── lib/              # ライブラリ
│   │   │   ├── api.js        # APIクライアント
│   │   │   └── supabase.js   # Supabaseクライアント
│   │   ├── pages/            # ページコンポーネント
│   │   │   ├── Dashboard.jsx        # ダッシュボード
│   │   │   ├── ApplicantsList.jsx   # 応募者一覧
│   │   │   ├── ApplicantDetail.jsx  # 応募者詳細
│   │   │   └── BatchUpload.jsx      # バッチ処理
│   │   └── components/       # 共通コンポーネント
│   │       └── Layout.jsx    # レイアウト
│   ├── package.json          # npm依存関係
│   └── .env                  # 環境変数
│
└── docs/                      # ドキュメント
    ├── setup-guide.md         # セットアップガイド
    ├── api-usage-guide.md     # API使用ガイド
    ├── supabase-schema.sql    # DBスキーマ
    └── development-guide.md   # 開発ガイド（本ドキュメント）
```

## 開発フロー

### 1. 新機能の追加

#### バックエンド

1. **モデル定義**（必要な場合）
   - `backend/app/models/`にPydanticモデルを追加

2. **サービス作成**
   - `backend/app/services/`にビジネスロジックを実装

3. **APIルート追加**
   - `backend/app/api/`に新しいルートを作成
   - `main.py`にルートを登録

4. **テスト**
   - http://localhost:8000/docs でSwagger UIでテスト

#### フロントエンド

1. **APIクライアント更新**
   - `frontend/src/lib/api.js`に新しいAPI関数を追加

2. **コンポーネント作成**
   - `frontend/src/pages/`または`frontend/src/components/`に追加

3. **ルーティング**
   - `App.jsx`にルートを追加

### 2. データベーススキーマ変更

1. **スキーマ更新**
   - `docs/supabase-schema.sql`を更新

2. **Supabase適用**
   - Supabase SQL Editorで実行

3. **モデル更新**
   - `backend/app/models/applicant.py`を更新

### 3. デバッグ

#### バックエンド

```bash
# ログ確認
uvicorn app.main:app --reload --log-level debug

# Python デバッガー
import pdb; pdb.set_trace()
```

#### フロントエンド

```bash
# ブラウザのDevTools Console
console.log()

# React DevTools
```

## コーディング規約

### Python（バックエンド）

- **スタイル**: PEP 8準拠
- **型ヒント**: 関数の引数と戻り値に型ヒントを使用
- **ドキュメント**: docstringでドキュメント化

```python
async def evaluate_applicant(
    self,
    applicant_data: ApplicantData,
    skill_ratio: float = None,
    mindset_ratio: float = None
) -> EvaluationResult:
    """
    応募者データを評価

    Args:
        applicant_data: 応募者データ
        skill_ratio: スキル評価比率
        mindset_ratio: マインドセット評価比率

    Returns:
        評価結果
    """
    pass
```

### JavaScript/React（フロントエンド）

- **スタイル**: ESLint設定に準拠
- **命名**: キャメルケース（変数・関数）、パスカルケース（コンポーネント）
- **コンポーネント**: 関数コンポーネント + Hooks

```javascript
export default function ApplicantDetail() {
  const [applicant, setApplicant] = useState(null)

  useEffect(() => {
    loadApplicant()
  }, [])

  return (
    <Box>
      {/* JSX */}
    </Box>
  )
}
```

## 環境変数管理

### バックエンド (.env)

```env
# Supabase
SUPABASE_URL=
SUPABASE_KEY=

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=

# 評価設定
DEFAULT_SKILL_RATIO=0.2
DEFAULT_MINDSET_RATIO=0.8
```

### フロントエンド (.env)

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_KEY=
VITE_API_URL=http://localhost:8000
```

## テスト

### バックエンドテスト

```bash
# 単体テスト（今後実装）
pytest tests/

# API統合テスト
# Swagger UI: http://localhost:8000/docs
```

### フロントエンドテスト

```bash
# 単体テスト（今後実装）
npm test

# E2Eテスト（今後実装）
npm run test:e2e
```

## デプロイ

### バックエンド

推奨プラットフォーム:
- **Render**: 簡単なデプロイ、無料プランあり
- **Railway**: コンテナベース、自動スケーリング
- **Google Cloud Run**: サーバーレス、Google Cloud統合

### フロントエンド

推奨プラットフォーム:
- **Vercel**: Viteプロジェクトに最適
- **Netlify**: 簡単なデプロイ、CDN統合
- **Cloudflare Pages**: 高速CDN

## トラブルシューティング

### よくある問題

1. **Google Cloud API認証エラー**
   - 環境変数が正しく設定されているか確認
   - サービスアカウントの権限を確認

2. **CORS エラー**
   - `backend/app/main.py`のallow_originsを確認
   - フロントエンドのURLが正しいか確認

3. **Supabase接続エラー**
   - URLとキーが正しいか確認
   - RLSポリシーを確認

4. **パッケージインストールエラー**
   ```bash
   # バックエンド
   pip install --upgrade pip
   pip install -r requirements.txt

   # フロントエンド
   rm -rf node_modules package-lock.json
   npm install
   ```

## パフォーマンス最適化

### バックエンド

1. **データベースクエリ最適化**
   - 必要なカラムのみ選択
   - インデックスを適切に設定

2. **API レスポンス圧縮**
   ```python
   from fastapi.middleware.gzip import GZipMiddleware
   app.add_middleware(GZipMiddleware)
   ```

3. **キャッシング**
   - Redis等を導入して頻繁にアクセスされるデータをキャッシュ

### フロントエンド

1. **コード分割**
   - React.lazy()で遅延ロード

2. **画像最適化**
   - 適切なフォーマット（WebP等）
   - サイズ最適化

3. **バンドルサイズ削減**
   ```bash
   npm run build
   npm run preview
   ```

## セキュリティ

### 重要な対策

1. **環境変数の保護**
   - `.env`ファイルをgitignoreに追加
   - 本番環境の秘密鍵を強固に

2. **入力バリデーション**
   - Pydanticでバックエンドの入力を検証
   - フロントエンドでも検証

3. **認証・認可**
   - 本番環境ではSupabase Authを使用
   - JWTトークン検証

4. **SQL インジェクション対策**
   - ORMを使用（Supabase クライアント）
   - 直接SQL実行を避ける

5. **レート制限**
   - APIに適切なレート制限を設定

## 次のステップ

1. **テストの実装**
   - 単体テスト
   - 統合テスト
   - E2Eテスト

2. **CI/CD パイプライン**
   - GitHub Actions
   - 自動デプロイ

3. **監視・ログ**
   - Sentry（エラートラッキング）
   - Google Cloud Logging

4. **追加機能**
   - ユーザー認証
   - ロール管理
   - 通知システム
   - レポート生成
