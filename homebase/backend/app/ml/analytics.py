"""
Analytics: workload report, GPA trend, study velocity.

Current implementation: pure statistical analysis with numpy/pandas.
ML upgrade path:
    - GPA prediction: linear regression on historical semester GPAs.
    - Workload clustering: k-means to identify "crunch weeks".
    - Study session recommender: collaborative filtering across users.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import List, Optional
from collections import Counter
from sqlalchemy.orm import Session

from ..models import Task, Semester, TaskStatusEnum
from ..schemas import WorkloadReport, GPATrend
from ..services.gpa_service import calculate_semester_gpa, grade_to_points


def workload_report(db: Session) -> WorkloadReport:
    tasks = db.query(Task).filter(Task.status != TaskStatusEnum.done).all()
    today = date.today()
    week_end = today + timedelta(days=7)

    overdue     = sum(1 for t in tasks if t.due_date and t.due_date < today)
    due_week    = sum(1 for t in tasks if t.due_date and today <= t.due_date <= week_end)

    all_tasks   = db.query(Task).all()
    done_count  = sum(1 for t in all_tasks if t.status == TaskStatusEnum.done)
    total       = len(all_tasks)
    completion_rate = round(done_count / total, 3) if total else 0.0

    # Busiest day: day with most tasks due in next 14 days
    upcoming = [t for t in tasks if t.due_date and today <= t.due_date <= today + timedelta(days=14)]
    day_counts = Counter(t.due_date.strftime("%A") for t in upcoming if t.due_date)
    busiest_day = day_counts.most_common(1)[0][0] if day_counts else None

    # Recommended focus: major with most overdue + high-priority tasks
    major_urgency: Counter = Counter()
    for t in tasks:
        if t.due_date and t.due_date < today:
            major_urgency[t.major.value] += 3
        if t.priority and t.priority.value == "high":
            major_urgency[t.major.value] += 2
    recommended_focus = (
        f"{major_urgency.most_common(1)[0][0].upper()} assignments"
        if major_urgency else None
    )

    return WorkloadReport(
        overdue_tasks=overdue,
        due_this_week=due_week,
        completion_rate=completion_rate,
        busiest_day=busiest_day,
        recommended_focus=recommended_focus,
    )


def gpa_trend(db: Session) -> GPATrend:
    semesters = db.query(Semester).order_by(Semester.created_at.asc()).all()
    if not semesters:
        return GPATrend(semesters=[], gpas=[], predicted_next=None, trend="stable")

    sem_names = [s.name for s in semesters]
    sem_gpas  = [calculate_semester_gpa(s).gpa for s in semesters]

    # Trend direction
    trend = "stable"
    if len(sem_gpas) >= 2:
        delta = sem_gpas[-1] - sem_gpas[0]
        if delta > 0.1:
            trend = "improving"
        elif delta < -0.1:
            trend = "declining"

    # Simple linear extrapolation (→ replace with sklearn LinearRegression)
    predicted_next: Optional[float] = None
    if len(sem_gpas) >= 2:
        try:
            n = len(sem_gpas)
            x_mean = (n - 1) / 2.0
            y_mean = sum(sem_gpas) / n
            numerator   = sum((i - x_mean) * (g - y_mean) for i, g in enumerate(sem_gpas))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            slope = numerator / denominator if denominator else 0.0
            predicted_next = round(min(4.0, max(0.0, sem_gpas[-1] + slope)), 3)
        except ZeroDivisionError:
            pass

    return GPATrend(
        semesters=sem_names,
        gpas=[round(g, 3) for g in sem_gpas],
        predicted_next=predicted_next,
        trend=trend,
    )
