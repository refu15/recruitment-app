# API使用ガイド

## 概要

採用書類選考APIの使用方法を説明します。

## 認証

現在、開発環境ではSupabaseの RLS（Row Level Security）を開発モードに設定しています。
本番環境では適切な認証・認可を実装してください。

## エンドポイント一覧

### 1. 応募者管理 (/api/applicants)

#### 応募者一覧取得
```http
GET /api/applicants/
Query Parameters:
  - status: ApplicationStatus (optional)
  - limit: int = 100
  - offset: int = 0

Response:
[
  {
    "id": "uuid",
    "name": "山田太郎",
    "email": "taro@example.com",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z",
    ...
  }
]
```

#### 応募者詳細取得
```http
GET /api/applicants/{applicant_id}

Response:
{
  "id": "uuid",
  "name": "山田太郎",
  "email": "taro@example.com",
  "applicant_data": {...},
  "evaluation": {...},
  ...
}
```

#### 応募者作成
```http
POST /api/applicants/
Body:
{
  "name": "山田太郎",
  "email": "taro@example.com",
  "phone": "090-1234-5678",
  "resume_url": "optional",
  "cover_letter": "optional"
}
```

#### 履歴書アップロード
```http
POST /api/applicants/{applicant_id}/upload-resume
Content-Type: multipart/form-data
Body: file (PDF)

Response:
{
  "message": "Resume uploaded successfully",
  "url": "https://..."
}
```

### 2. 評価 (/api/evaluation)

#### データ抽出（OCR）
```http
POST /api/evaluation/extract-data
Body:
{
  "applicant_id": "uuid",
  "resume_url": "path/to/resume.pdf"
}

Response:
{
  "message": "Data extracted successfully",
  "applicant_data": {...},
  "ocr_confidence": 0.95
}
```

#### AI評価実行
```http
POST /api/evaluation/evaluate
Body:
{
  "applicant_id": "uuid",
  "skill_ratio": 0.2,  // optional
  "mindset_ratio": 0.8  // optional
}

Response:
{
  "message": "Evaluation completed successfully",
  "evaluation": {
    "skill_score": 7.5,
    "mindset_score": 8.2,
    "total_score": 8.06,
    "summary": "...",
    "strengths": [...],
    "concerns": [...]
  }
}
```

#### 評価比率更新
```http
POST /api/evaluation/{applicant_id}/update-ratio
Body:
{
  "skill_ratio": 0.3,
  "mindset_ratio": 0.7
}

Response:
{
  "message": "Evaluation ratio updated successfully",
  "evaluation": {...}
}
```

### 3. 面接 (/api/interview)

#### 面接質問生成
```http
POST /api/interview/generate-questions
Body:
{
  "applicant_id": "uuid",
  "question_count": 10
}

Response:
{
  "message": "Interview questions generated successfully",
  "questions": [
    "質問1...",
    "質問2...",
    ...
  ]
}
```

#### 質問取得
```http
GET /api/interview/{applicant_id}/questions

Response:
{
  "questions": [...]
}
```

### 4. バッチ処理 (/api/batch)

#### CSVアップロード
```http
POST /api/batch/upload-csv
Content-Type: multipart/form-data
Body:
  - file: CSV file
  - skill_ratio: 0.2
  - mindset_ratio: 0.8

Response:
{
  "total_count": 10,
  "success_count": 9,
  "error_count": 1,
  "results": [
    {
      "name": "山田太郎",
      "email": "taro@example.com",
      "status": "success",
      "total_score": 8.5
    },
    ...
  ]
}
```

#### 結果エクスポート
```http
GET /api/batch/export-results
Query Parameters:
  - status: string (optional)
  - min_score: float (optional)

Response:
{
  "count": 50,
  "data": [
    {
      "ID": "uuid",
      "名前": "山田太郎",
      "総合スコア": 8.5,
      ...
    }
  ]
}
```

### 5. Google Calendar連携 (/api/calendar)

#### 面接スケジュール作成
```http
POST /api/calendar/create-interview
Body:
{
  "applicant_id": "uuid",
  "start_time": "2024-01-15T10:00:00",
  "duration_minutes": 60,
  "description": "一次面接"
}

Response:
{
  "message": "Interview scheduled successfully",
  "event_id": "calendar_event_id",
  "event_link": "https://calendar.google.com/...",
  "start_time": "2024-01-15T10:00:00",
  "end_time": "2024-01-15T11:00:00"
}
```

#### 空き時間検索
```http
POST /api/calendar/find-available-slots
Body:
{
  "start_date": "2024-01-15T00:00:00",
  "end_date": "2024-01-20T00:00:00",
  "duration_minutes": 60
}

Response:
{
  "count": 15,
  "slots": [
    {
      "start": "2024-01-15T10:00:00",
      "end": "2024-01-15T11:00:00",
      "duration_minutes": 60
    },
    ...
  ]
}
```

#### 面接更新
```http
PATCH /api/calendar/update-interview
Body:
{
  "event_id": "calendar_event_id",
  "start_time": "2024-01-15T14:00:00",
  "duration_minutes": 90
}
```

#### 面接キャンセル
```http
DELETE /api/calendar/cancel-interview/{event_id}
```

## 典型的なワークフロー

### 1. 新規応募者の処理

1. **応募者作成**
   ```
   POST /api/applicants/
   ```

2. **履歴書アップロード**
   ```
   POST /api/applicants/{id}/upload-resume
   ```

3. **データ抽出（OCR）**
   ```
   POST /api/evaluation/extract-data
   ```

4. **AI評価実行**
   ```
   POST /api/evaluation/evaluate
   ```

5. **面接質問生成**
   ```
   POST /api/interview/generate-questions
   ```

6. **面接スケジュール作成**
   ```
   POST /api/calendar/create-interview
   ```

### 2. バッチ処理

1. **CSVアップロード**
   ```
   POST /api/batch/upload-csv
   ```

2. **結果確認**
   ```
   GET /api/batch/export-results
   ```

### 3. 評価比率の調整

1. **評価比率更新**
   ```
   POST /api/evaluation/{applicant_id}/update-ratio
   ```
   - これにより、既存の評価が新しい比率で再計算されます

## エラーハンドリング

すべてのエンドポイントは、エラー発生時に適切なHTTPステータスコードとエラーメッセージを返します。

```json
{
  "detail": "エラーメッセージ"
}
```

一般的なステータスコード：
- 200: 成功
- 201: 作成成功
- 400: リクエストエラー
- 404: リソースが見つからない
- 500: サーバーエラー

## レート制限

Google Cloud APIには以下のクォータ制限があります：
- Vision API: 1000リクエスト/月（無料枠）
- Vertex AI (Gemini): 従量課金
- Calendar API: 1,000,000リクエスト/日

大量の処理を行う場合は、適切なエラーハンドリングとリトライ処理を実装してください。
