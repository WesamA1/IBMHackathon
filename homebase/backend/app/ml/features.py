"""
Feature extraction for ML models.

All feature vectors are built here so that:
  1. Rule-based logic uses the same features as trained models.
  2. Swapping in sklearn/pytorch is a single-line change in engine.py.
"""
from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class CardFeatures:
    card_id:        int
    deck_id:        int
    question:       str
    times_seen:     int
    times_correct:  int
    ease_factor:    float
    interval_days:  int
    next_review_date: Optional[date]

    @property
    def accuracy(self) -> float:
        return self.times_correct / self.times_seen if self.times_seen else 0.0

    @property
    def days_overdue(self) -> int:
        if not self.next_review_date:
            return 0
        delta = (date.today() - self.next_review_date).days
        return max(0, delta)

    @property
    def is_new(self) -> bool:
        return self.times_seen == 0

    def to_vector(self) -> list[float]:
        """Numerical feature vector for sklearn pipeline."""
        return [
            float(self.times_seen),
            float(self.times_correct),
            self.accuracy,
            self.ease_factor,
            float(self.interval_days),
            float(self.days_overdue),
            1.0 if self.is_new else 0.0,
        ]


@dataclass
class TaskFeatures:
    task_id:     int
    title:       str
    major:       str
    priority:    str
    status:      str
    due_date:    Optional[date]
    created_at:  datetime
    completed_at: Optional[datetime]

    PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}

    @property
    def days_until_due(self) -> Optional[int]:
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days

    @property
    def is_overdue(self) -> bool:
        d = self.days_until_due
        return d is not None and d < 0 and self.status != "done"

    @property
    def urgency_score(self) -> float:
        """0–1 urgency; higher = more urgent."""
        base = self.PRIORITY_WEIGHT.get(self.priority, 2) / 3.0
        if self.is_overdue:
            return min(1.0, base + 0.4)
        d = self.days_until_due
        if d is not None and 0 <= d <= 3:
            return min(1.0, base + 0.25)
        return base

    def to_vector(self) -> list[float]:
        d = self.days_until_due
        return [
            self.PRIORITY_WEIGHT.get(self.priority, 2),
            float(d) if d is not None else 999.0,
            1.0 if self.is_overdue else 0.0,
            float((datetime.utcnow() - self.created_at).days),
        ]
