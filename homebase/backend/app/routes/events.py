from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from ..database import get_db
from ..models import Event, RepeatEnum
from ..schemas import EventCreate, EventRead

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=List[EventRead])
def list_events(
    start: Optional[date] = Query(None, description="Inclusive start date"),
    end:   Optional[date] = Query(None, description="Inclusive end date"),
    db:    Session         = Depends(get_db),
):
    """
    Returns all stored events. Repeating events are expanded client-side
    or via /expand endpoint.
    """
    q = db.query(Event)
    if start:
        q = q.filter(Event.event_date >= start)
    if end:
        q = q.filter(Event.event_date <= end)
    return q.order_by(Event.event_date.asc()).all()


@router.get("/expand", response_model=List[EventRead])
def expand_events(
    start: date = Query(...),
    end:   date = Query(...),
    db:    Session = Depends(get_db),
):
    """
    Expands repeating events between start and end dates.
    Returns virtual EventRead objects (same id = base event id).
    """
    base_events = db.query(Event).all()
    result = []
    current = start
    while current <= end:
        for ev in base_events:
            matches = ev.event_date == current
            if not matches and ev.repeat == RepeatEnum.weekly:
                matches = ev.event_date <= current and current.weekday() == ev.event_date.weekday()
            if not matches and ev.repeat == RepeatEnum.daily:
                matches = ev.event_date <= current
            if matches:
                # Yield a copy with overridden date
                result.append(EventRead(
                    id=ev.id,
                    name=ev.name,
                    event_date=current,
                    start_time=ev.start_time,
                    end_time=ev.end_time,
                    event_type=ev.event_type,
                    location=ev.location,
                    repeat=ev.repeat,
                    created_at=ev.created_at,
                ))
        current += timedelta(days=1)
    return result


@router.post("", response_model=EventRead, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    ev = Event(**payload.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.patch("/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventCreate, db: Session = Depends(get_db)):
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(404, "Event not found")
    for field, value in payload.model_dump().items():
        setattr(ev, field, value)
    db.commit()
    db.refresh(ev)
    return ev


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(404, "Event not found")
    db.delete(ev)
    db.commit()
