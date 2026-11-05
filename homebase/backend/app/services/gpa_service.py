"""
Pure GPA calculation logic — no ORM dependency.
Keeps business logic separate from routes for easy unit testing.
"""
from sqlalchemy.orm import Session
from ..models import Semester, Course
from ..schemas import CumulativeGPA, SemesterGPA

GRADE_POINTS: dict[str, float] = {
    "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}


def grade_to_points(grade: str) -> float | None:
    """Returns None for W/I/P (non-credit-affecting grades)."""
    return GRADE_POINTS.get(grade.strip().upper())


def calculate_semester_gpa(semester: Semester) -> SemesterGPA:
    total_pts = 0.0
    total_creds = 0
    for course in semester.courses:
        pts = grade_to_points(course.grade)
        if pts is not None:
            total_pts   += pts * course.credits
            total_creds += course.credits
    gpa = total_pts / total_creds if total_creds else 0.0
    return SemesterGPA(
        semester_id=semester.id,
        semester_name=semester.name,
        gpa=round(gpa, 3),
        credits=total_creds,
        points=round(total_pts, 3),
    )


def calculate_cumulative_gpa(db: Session) -> CumulativeGPA:
    semesters = db.query(Semester).order_by(Semester.created_at.asc()).all()
    sem_gpas = [calculate_semester_gpa(s) for s in semesters]
    total_pts   = sum(s.points  for s in sem_gpas)
    total_creds = sum(s.credits for s in sem_gpas)
    cum_gpa = total_pts / total_creds if total_creds else 0.0
    return CumulativeGPA(
        cumulative_gpa=round(cum_gpa, 3),
        total_credits=total_creds,
        total_points=round(total_pts, 3),
        semester_count=len(semesters),
        semesters=sem_gpas,
    )
