from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Update, MajorEnum, PostTypeEnum
from ..schemas import UpdateCreate, UpdateRead

router = APIRouter(prefix="/updates", tags=["updates"])


@router.get("/", response_model=List[UpdateRead])
def list_updates(
    major:     Optional[MajorEnum]    = Query(None),
    post_type: Optional[PostTypeEnum] = Query(None),
    search:    Optional[str]          = Query(None),
    db:        Session                = Depends(get_db),
):
    q = db.query(Update)
    if major:
        q = q.filter(Update.major == major)
    if post_type:
        q = q.filter(Update.post_type == post_type)
    if search:
        like = f"%{search}%"
        q = q.filter(Update.title.ilike(like) | Update.body.ilike(like))
    return q.order_by(Update.created_at.desc()).all()


@router.post("/", response_model=UpdateRead, status_code=201)
def create_update(payload: UpdateCreate, db: Session = Depends(get_db)):
    obj = Update(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{update_id}", status_code=204)
def delete_update(update_id: int, db: Session = Depends(get_db)):
    obj = db.get(Update, update_id)
    if not obj:
        raise HTTPException(404, "Update not found")
    db.delete(obj)
    db.commit()


@router.post("/{update_id}/view", response_model=UpdateRead)
def increment_view(update_id: int, db: Session = Depends(get_db)):
    """Called by frontend when a post is expanded — feeds engagement ML."""
    obj = db.get(Update, update_id)
    if not obj:
        raise HTTPException(404, "Update not found")
    obj.view_count += 1
    db.commit()
    db.refresh(obj)
    return obj
