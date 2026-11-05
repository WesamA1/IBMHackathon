from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Resource, MajorEnum, ResourceTypeEnum
from ..schemas import ResourceCreate, ResourceRead

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/", response_model=List[ResourceRead])
def list_resources(
    major:    Optional[MajorEnum]         = Query(None),
    res_type: Optional[ResourceTypeEnum]  = Query(None),
    db:       Session                     = Depends(get_db),
):
    q = db.query(Resource)
    if major:
        q = q.filter(Resource.major == major)
    if res_type:
        q = q.filter(Resource.res_type == res_type)
    return q.order_by(Resource.click_count.desc(), Resource.created_at.desc()).all()


@router.post("/", response_model=ResourceRead, status_code=201)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    res = Resource(**payload.model_dump())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@router.delete("/{resource_id}", status_code=204)
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    res = db.get(Resource, resource_id)
    if not res:
        raise HTTPException(404, "Resource not found")
    db.delete(res)
    db.commit()


@router.post("/{resource_id}/click", response_model=ResourceRead)
def record_click(resource_id: int, db: Session = Depends(get_db)):
    """Increments click_count for ML popularity ranking."""
    res = db.get(Resource, resource_id)
    if not res:
        raise HTTPException(404, "Resource not found")
    res.click_count += 1
    db.commit()
    db.refresh(res)
    return res
