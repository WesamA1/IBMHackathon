"""
Flashcard recommender.

Current implementation: rule-based urgency scoring (SM-2 derived).
Drop-in replacement path:
    1. Collect (card_features, rating) pairs over time.
    2. Train a gradient-boosted ranker (e.g. sklearn GradientBoostingRegressor).
    3. Serialise to model.pkl.
    4. Load here and replace _score_rule with model.predict(vectors).
"""
from __future__ import annotations
from datetime import date
from typing import List
from sqlalchemy.orm import Session

from ..models import Card, Deck
from ..schemas import FlashcardRecommendation
from .features import CardFeatures


def _score_rule(f: CardFeatures) -> float:
    """
    Heuristic urgency score (0–1).
    New cards get a medium-high score to encourage first exposure.
    Overdue cards score proportionally higher.
    Low-accuracy cards are prioritised over high-accuracy ones.
    """
    if f.is_new:
        return 0.65
    overdue_boost = min(0.4, f.days_overdue * 0.05)
    accuracy_penalty = f.accuracy * 0.3
    base = 0.5 + overdue_boost - accuracy_penalty
    return round(min(1.0, max(0.0, base)), 4)


def _reason(f: CardFeatures) -> str:
    if f.is_new:
        return "new card"
    if f.days_overdue > 0:
        return f"overdue by {f.days_overdue}d"
    if f.accuracy < 0.5:
        return "low accuracy"
    return "scheduled review"


def recommend_cards(
    db: Session,
    deck_id: int,
    limit: int = 10,
) -> List[FlashcardRecommendation]:
    cards = db.query(Card).filter(Card.deck_id == deck_id).all()
    if not cards:
        return []

    features = [
        CardFeatures(
            card_id=c.id,
            deck_id=c.deck_id,
            question=c.question,
            times_seen=c.times_seen,
            times_correct=c.times_correct,
            ease_factor=c.ease_factor,
            interval_days=c.interval_days,
            next_review_date=c.next_review_date,
        )
        for c in cards
    ]

    scored = sorted(features, key=_score_rule, reverse=True)[:limit]

    return [
        FlashcardRecommendation(
            card_id=f.card_id,
            deck_id=f.deck_id,
            question=f.question,
            score=_score_rule(f),
            reason=_reason(f),
        )
        for f in scored
    ]
