"""
MLEngine — central dispatcher.

Wraps all ML/analytics services. Routes call engine.method() so that:
  - The service layer stays decoupled from route handlers.
  - Swapping implementations (rule-based → trained model) is localised here.
  - Future: load sklearn/pytorch models at startup via lifespan, store on engine.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from ..schemas import FlashcardRecommendation, WorkloadReport, GPATrend
from . import recommender, analytics


class MLEngine:
    def __init__(self, db: Session):
        self.db = db
        # Future: self.card_ranker = load_model("models/card_ranker.pkl")

    def recommend_cards(self, deck_id: int, limit: int = 10) -> list[FlashcardRecommendation]:
        return recommender.recommend_cards(self.db, deck_id, limit)

    def workload_report(self) -> WorkloadReport:
        return analytics.workload_report(self.db)

    def gpa_trend(self) -> GPATrend:
        return analytics.gpa_trend(self.db)
