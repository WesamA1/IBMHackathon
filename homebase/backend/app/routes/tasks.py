from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models import Task, TaskStatusEnum, TaskPriorityEnum, MajorEnum
from ..schemas import TaskCreate, TaskUpdate, TaskRead
from ..ml.engine import MLEngine

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskRead])
def list_tasks(
    status:   Optional[TaskStatusEnum]   = Query(None),
    priority: Optional[TaskPriorityEnum] = Query(None),
    major:    Optional[MajorEnum]        = Query(None),
    search:   Optional[str]              = Query(None),
    db:       Session                    = Depends(get_db),
):
    q = db.query(Task)
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == priority)
    if major:
        q = q.filter(Task.major == major)
    if search:
        q = q.filter(Task.title.ilike(f"%{search}%") | Task.course.ilike(f"%{search}%"))
    return q.order_by(Task.created_at.desc()).all()


@router.post("", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    data = payload.model_dump(exclude_unset=True)

    # Track completion timestamp for ML velocity analysis
    if "status" in data and data["status"] == TaskStatusEnum.done and task.status != TaskStatusEnum.done:
        data["completed_at"] = datetime.utcnow()
    elif "status" in data and data["status"] != TaskStatusEnum.done:
        data["completed_at"] = None

    for field, value in data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()


@router.get("/workload-report")
def workload_report(db: Session = Depends(get_db)):
    """ML-powered workload analysis: overdue, velocity, busiest day."""
    engine = MLEngine(db)
    return engine.workload_report()
