from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel
from typing import List, Dict, Any
from app.models.applicant import EvaluationResult, ApplicantData
from app.utils.config import settings
import json
import os

class InterviewService:
    def __init__(self):
        self.model = None
        if settings.google_cloud_project_id and settings.google_application_credentials:
            try:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
                vertexai.init(project=settings.google_cloud_project_id, location="us-central1")
                self.model = GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                print(f"Vertex AIの初期化に失敗しました: {e}")
                self.model = None

    async def generate_interview_questions(
        self,
        applicant_data: ApplicantData,
        evaluation: EvaluationResult,
        question_count: int = 10
    ) -> List[str]:
        """
        マインドセット重視の一次面接質問を生成

        Args:
            applicant_data: 応募者データ
            evaluation: 評価結果
            question_count: 生成する質問数

        Returns:
            面接質問のリスト
        """
        if not self.model:
            print("Vertex AIが初期化されていないため、デフォルトの質問を返します。")
            return self._get_default_questions()

        prompt = self._build_interview_prompt(applicant_data, evaluation, question_count)

        try:
            response = self.model.generate_content(prompt)
            questions = self._parse_questions_response(response.text)
            return questions[:question_count]  # 指定数に制限

        except Exception as e:
            print(f"質問生成エラー: {str(e)}")
            return self._get_default_questions()

    def _build_interview_prompt(
        self,
        applicant_data: ApplicantData,
        evaluation: EvaluationResult,
        question_count: int
    ) -> str:
        """面接質問生成プロンプトを構築"""

        # マインドセット評価が低い項目を特定
        low_mindset_areas = [
            m.category for m in evaluation.mindset_evaluations
            if m.score < 7.0
        ]

        # 強みと懸念点をまとめる
        strengths_text = "\n".join([f"- {s}" for s in evaluation.strengths])
        concerns_text = "\n".join([f"- {c}" for c in evaluation.concerns])
        low_areas_text = "\n".join([f"- {area}" for area in low_mindset_areas]) if low_mindset_areas else "なし"

        return f"""
あなたは採用面接の専門家です。以下の応募者に対して、マインドセットを深掘りする一次面接質問を{question_count}個生成してください。

【応募者情報】
名前: {applicant_data.name}
志望動機: {applicant_data.motivation}
キャリア目標: {applicant_data.career_goals}

【評価結果サマリー】
{evaluation.summary}

【強み】
{strengths_text}

【懸念点】
{concerns_text}

【マインドセット評価が低い項目】
{low_areas_text}

【質問作成の指針】
1. **マインドセット重視**: スキルよりも、成長志向・主体性・協調性・価値観を探る質問を中心に
2. **具体的な行動を引き出す**: STAR法（状況・課題・行動・結果）で具体例を聞く
3. **懸念点の確認**: 評価で懸念された点を深掘りする質問を含める
4. **低評価項目のフォロー**: マインドセット評価が低かった項目を確認
5. **志望動機の深掘り**: 表面的な回答ではなく、真の動機や価値観を探る

【質問カテゴリの配分目安】
- 成長志向・学習意欲: 30%
- 主体性・問題解決: 25%
- 協調性・チームワーク: 20%
- 価値観・動機: 15%
- ストレス耐性・適応力: 10%

【出力形式】
以下のJSON形式で質問を出力してください：

{{
  "questions": [
    {{
      "question": "質問文",
      "category": "カテゴリ（成長志向/主体性/協調性/価値観/その他）",
      "intent": "この質問で何を確認したいか（1文）"
    }}
  ]
}}

【質問の例】
- 「これまでで最も困難だったプロジェクトについて教えてください。どのような課題があり、どう乗り越えましたか?」（主体性）
- 「過去に自分の意見がチームの意見と対立した経験はありますか? どのように対処しましたか?」（協調性）
- 「昨年1年間で新しく学んだスキルや知識は何ですか? それをどのように習得しましたか?」（成長志向）
- 「弊社を志望する理由を、キャリアビジョンと絡めて教えてください」（価値観）
"""

    def _parse_questions_response(self, response_text: str) -> List[str]:
        """Geminiからの応答をパースして質問リストに変換"""
        try:
            # JSONブロックを抽出
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            data = json.loads(response_text)

            # 質問のみを抽出（カテゴリやintentは除外）
            questions = [q["question"] for q in data.get("questions", [])]
            return questions

        except Exception as e:
            print(f"質問パースエラー: {str(e)}")
            return self._get_default_questions()

    def _get_default_questions(self) -> List[str]:
        """デフォルトの面接質問"""
        return [
            "これまでのキャリアで最も困難だった経験と、それをどう乗り越えたかを教えてください。",
            "チームで働く際に、意見の対立が生じた経験はありますか? その時どのように対処しましたか?",
            "昨年1年間で新しく学んだスキルや知識は何ですか?",
            "失敗から学んだ重要な教訓について教えてください。",
            "弊社を志望する理由を、あなたのキャリアビジョンと関連付けて説明してください。",
            "5年後、10年後のキャリアをどのように考えていますか?",
            "自分の強みと弱みを3つずつ挙げ、弱みをどう改善しようとしているか教えてください。",
            "プレッシャーがかかる状況下で、どのようにモチベーションを維持しますか?",
            "これまでで最も誇りに思うプロジェクトや成果は何ですか?",
            "仕事において最も大切にしている価値観は何ですか?"
        ]