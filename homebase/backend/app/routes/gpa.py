from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Semester, Course
from ..schemas import (
    SemesterCreate, SemesterRead, CourseCreate, CourseRead,
    CumulativeGPA, SemesterGPA,
)
from ..services.gpa_service import calculate_semester_gpa, calculate_cumulative_gpa
from ..ml.engine import MLEngine

router = APIRouter(prefix="/gpa", tags=["gpa"])

GRADE_POINTS = {
    "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}


# ── Semesters ──────────────────────────────────────────────────────────────

@router.get("/semesters", response_model=List[SemesterRead])
def list_semesters(db: Session = Depends(get_db)):
    return db.query(Semester).order_by(Semester.created_at.asc()).all()


@router.post("/semesters", response_model=SemesterRead, status_code=201)
def create_semester(payload: SemesterCreate, db: Session = Depends(get_db)):
    sem = Semester(**payload.model_dump())
    db.add(sem)
    db.commit()
    db.refresh(sem)
    return sem


@router.delete("/semesters/{sem_id}", status_code=204)
def delete_semester(sem_id: int, db: Session = Depends(get_db)):
    sem = db.get(Semester, sem_id)
    if not sem:
        raise HTTPException(404, "Semester not found")
    db.delete(sem)
    db.commit()


# ── Courses ────────────────────────────────────────────────────────────────

@router.post("/semesters/{sem_id}/courses", response_model=CourseRead, status_code=201)
def add_course(sem_id: int, payload: CourseCreate, db: Session = Depends(get_db)):
    if not db.get(Semester, sem_id):
        raise HTTPException(404, "Semester not found")
    course = Course(semester_id=sem_id, **payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.patch("/courses/{course_id}", response_model=CourseRead)
def update_course(course_id: int, payload: CourseCreate, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    for field, value in payload.model_dump().items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    db.delete(course)
    db.commit()


# ── Computed GPA ───────────────────────────────────────────────────────────

@router.get("/cumulative", response_model=CumulativeGPA)
def cumulative_gpa(db: Session = Depends(get_db)):
    return calculate_cumulative_gpa(db)


@router.get("/trend")
def gpa_trend(db: Session = Depends(get_db)):
    """ML-powered GPA trend analysis with optional next-semester prediction."""
    engine = MLEngine(db)
    return engine.gpa_trend()
