from google.cloud import aiplatform
from google.auth import default
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from typing import Dict, Any, List
from app.models.applicant import ApplicantData, EvaluationResult, SkillEvaluation, MindsetEvaluation
from app.utils.config import settings
import json
import os

class AIEvaluationService:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials

        # Vertex AI初期化
        vertexai.init(project=settings.google_cloud_project_id, location="us-central1")
        self.model = GenerativeModel("gemini-1.5-flash")

    async def evaluate_applicant(
        self,
        applicant_data: ApplicantData,
        skill_ratio: float = None,
        mindset_ratio: float = None
    ) -> EvaluationResult:
        """応募者データを評価"""

        if skill_ratio is None:
            skill_ratio = settings.default_skill_ratio
        if mindset_ratio is None:
            mindset_ratio = settings.default_mindset_ratio

        # プロンプト構築
        prompt = self._build_evaluation_prompt(applicant_data, skill_ratio, mindset_ratio)

        try:
            # Gemini APIで評価
            response = self.model.generate_content(prompt)
            result_text = response.text

            # JSONパース
            evaluation_data = self._parse_evaluation_response(result_text)

            # EvaluationResultオブジェクトに変換
            evaluation = EvaluationResult(
                skill_evaluations=[
                    SkillEvaluation(**skill) for skill in evaluation_data.get("skill_evaluations", [])
                ],
                mindset_evaluations=[
                    MindsetEvaluation(**mindset) for mindset in evaluation_data.get("mindset_evaluations", [])
                ],
                skill_score=evaluation_data.get("skill_score", 0.0),
                mindset_score=evaluation_data.get("mindset_score", 0.0),
                total_score=evaluation_data.get("total_score", 0.0),
                skill_ratio=skill_ratio,
                mindset_ratio=mindset_ratio,
                summary=evaluation_data.get("summary", ""),
                strengths=evaluation_data.get("strengths", []),
                concerns=evaluation_data.get("concerns", [])
            )

            return evaluation

        except Exception as e:
            print(f"評価エラー: {str(e)}")
            # エラー時はデフォルト評価を返す
            return EvaluationResult(
                skill_score=5.0,
                mindset_score=5.0,
                total_score=5.0,
                skill_ratio=skill_ratio,
                mindset_ratio=mindset_ratio,
                summary=f"評価処理中にエラーが発生しました: {str(e)}"
            )

    def _build_evaluation_prompt(
        self,
        applicant_data: ApplicantData,
        skill_ratio: float,
        mindset_ratio: float
    ) -> str:
        """評価プロンプトを構築"""

        return f"""
あなたは採用評価の専門家です。以下の応募者データを分析し、スキルとマインドセットの両面から評価してください。

【評価比率】
- スキル評価: {skill_ratio * 100}%
- マインドセット評価: {mindset_ratio * 100}%

【応募者データ】
名前: {applicant_data.name}
メール: {applicant_data.email}

学歴:
{json.dumps(applicant_data.education, ensure_ascii=False, indent=2)}

職歴:
{json.dumps(applicant_data.work_experience, ensure_ascii=False, indent=2)}

技術スキル: {', '.join(applicant_data.technical_skills)}
ソフトスキル: {', '.join(applicant_data.soft_skills)}
資格: {', '.join(applicant_data.certifications)}

志望動機:
{applicant_data.motivation}

キャリア目標:
{applicant_data.career_goals}

【評価基準】

＜スキル評価＞（各項目を0-10点で評価）
1. 技術力: 専門知識・技術スキルの深さと広さ
2. 経験: 実務経験の質と量
3. 資格・学歴: 専門性を示す資格や学位

＜マインドセット評価＞（各項目を0-10点で評価）
1. 成長志向: 学習意欲、自己成長への意識
2. 主体性: 自ら考え行動する姿勢、問題解決能力
3. 協調性: チームワーク、コミュニケーション能力
4. 価値観適合: 組織文化やビジョンとの整合性
5. 情熱・モチベーション: 仕事への熱意、志望動機の強さ

【出力形式】
以下のJSON形式で評価結果を出力してください：

{{
  "skill_evaluations": [
    {{"category": "技術力", "score": 0.0, "evidence": ["根拠1", "根拠2"]}},
    {{"category": "経験", "score": 0.0, "evidence": ["根拠1"]}},
    {{"category": "資格・学歴", "score": 0.0, "evidence": ["根拠1"]}}
  ],
  "mindset_evaluations": [
    {{"category": "成長志向", "score": 0.0, "evidence": ["根拠1", "根拠2"]}},
    {{"category": "主体性", "score": 0.0, "evidence": ["根拠1"]}},
    {{"category": "協調性", "score": 0.0, "evidence": ["根拠1"]}},
    {{"category": "価値観適合", "score": 0.0, "evidence": ["根拠1"]}},
    {{"category": "情熱・モチベーション", "score": 0.0, "evidence": ["根拠1"]}}
  ],
  "skill_score": 0.0,
  "mindset_score": 0.0,
  "total_score": 0.0,
  "summary": "総合評価のサマリー（2-3文）",
  "strengths": ["強み1", "強み2", "強み3"],
  "concerns": ["懸念点1", "懸念点2"]
}}

※ skill_score、mindset_scoreは各カテゴリーの平均点
※ total_scoreは (skill_score × {skill_ratio}) + (mindset_score × {mindset_ratio})
"""

    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Geminiからの応答をパース"""
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

            return json.loads(response_text)
        except Exception as e:
            print(f"JSONパースエラー: {str(e)}")
            print(f"Response: {response_text}")
            return {}
