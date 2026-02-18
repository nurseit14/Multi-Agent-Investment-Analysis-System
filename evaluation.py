# evaluation.py

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    depth_score: int
    consistency_score: int
    risk_coverage_score: int
    usefulness_score: int
    comments: str


def build_evaluation_chain():
    """
    В этой версии вместо LLM используется простая эвристика:
    - считаем длину текста,
    - проверяем наличие ключевых слов: risk, recommendation, BUY/HOLD/SELL и т.п.
    """

    KEYWORDS_RISK = ["risk", "volatility", "downside"]
    KEYWORDS_RECO = ["recommendation", "BUY", "HOLD", "SELL"]
    KEYWORDS_ANALYSIS = ["technical", "fundamental"]

    class EvalChain:
        def invoke(self, inputs):
            report: str = inputs.get("report", "")
            text_lower = report.lower()
            length = len(report)

            depth = 1
            if length > 1200:
                depth = 5
            elif length > 900:
                depth = 4
            elif length > 600:
                depth = 3
            elif length > 300:
                depth = 2

            def score_for_keywords(kw_list):
                hits = sum(1 for k in kw_list if k.lower() in text_lower)
                return min(5, 1 + hits * 2)

            risk_score = score_for_keywords(KEYWORDS_RISK)
            reco_score = score_for_keywords(KEYWORDS_RECO)
            analysis_score = score_for_keywords(KEYWORDS_ANALYSIS)

            comments = (
                f"Depth based on length: {depth}/5. "
                f"Risk coverage: {risk_score}/5. "
                f"Recommendation mentions: {reco_score}/5. "
                f"Technical+fundamental mentions: {analysis_score}/5."
            )

            return EvaluationResult(
                depth_score=depth,
                consistency_score=analysis_score,
                risk_coverage_score=risk_score,
                usefulness_score=reco_score,
                comments=comments,
            )

    return EvalChain()