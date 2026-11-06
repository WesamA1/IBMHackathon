"""
Pydantic v2 schemas — request/response models.
Separate Read / Create / Update shapes for each domain.
"""
from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from ..models import (
    MajorEnum, PostTypeEnum, TaskStatusEnum, TaskPriorityEnum,
    EventTypeEnum, RepeatEnum, ResourceTypeEnum,
)


# ─────────────────────────────────────────────
# Updates
# ─────────────────────────────────────────────

class UpdateBase(BaseModel):
    title:      str             = Field(..., max_length=200)
    body:       Optional[str]   = None
    major:      MajorEnum       = MajorEnum.all
    post_type:  PostTypeEnum    = PostTypeEnum.event
    event_date: Optional[date]  = None
    event_time: Optional[str]   = None
    location:   Optional[str]   = None

class UpdateCreate(UpdateBase):
    pass

class UpdateRead(UpdateBase):
    model_config = ConfigDict(from_attributes=True)
    id:         int
    created_at: datetime
    view_count: int


# ─────────────────────────────────────────────
# Decks + Cards
# ─────────────────────────────────────────────

class CardBase(BaseModel):
    question: str
    answer:   str

class CardCreate(CardBase):
    pass

class CardRead(CardBase):
    model_config = ConfigDict(from_attributes=True)
    id:               int
    times_seen:       int
    times_correct:    int
    ease_factor:      float
    interval_days:    int
    next_review_date: Optional[date]

class CardReview(BaseModel):
    """Payload when a user rates a card during study."""
    correct: bool
    rating:  int = Field(3, ge=1, le=5)   # 1=blackout → 5=perfect (SM-2)

class DeckBase(BaseModel):
    name:  str = Field(..., max_length=200)
    icon:  Optional[str] = None
    major: MajorEnum = MajorEnum.cs

class DeckCreate(DeckBase):
    pass

class DeckRead(DeckBase):
    model_config = ConfigDict(from_attributes=True)
    id:         int
    created_at: datetime
    cards:      List[CardRead] = []


# ─────────────────────────────────────────────
# Tasks
# ─────────────────────────────────────────────

class TaskBase(BaseModel):
    title:    str              = Field(..., max_length=300)
    notes:    Optional[str]   = None
    major:    MajorEnum       = MajorEnum.cs
    priority: TaskPriorityEnum = TaskPriorityEnum.medium
    status:   TaskStatusEnum   = TaskStatusEnum.todo
    due_date: Optional[date]  = None
    course:   Optional[str]   = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title:    Optional[str]             = None
    notes:    Optional[str]             = None
    major:    Optional[MajorEnum]       = None
    priority: Optional[TaskPriorityEnum]= None
    status:   Optional[TaskStatusEnum]  = None
    due_date: Optional[date]            = None
    course:   Optional[str]             = None

class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id:           int
    created_at:   datetime
    updated_at:   datetime
    completed_at: Optional[datetime]


# ─────────────────────────────────────────────
# Events
# ─────────────────────────────────────────────

class EventBase(BaseModel):
    name:        str             = Field(..., max_length=300)
    event_date:  date
    start_time:  Optional[str]  = None
    end_time:    Optional[str]  = None
    event_type:  EventTypeEnum  = EventTypeEnum.personal
    location:    Optional[str]  = None
    repeat:      RepeatEnum     = RepeatEnum.none

class EventCreate(EventBase):
    pass

class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id:         int
    created_at: datetime


# ─────────────────────────────────────────────
# GPA
# ─────────────────────────────────────────────

class CourseBase(BaseModel):
    name:    str = Field(..., max_length=200)
    grade:   str = Field(..., max_length=4)
    credits: int = Field(3, ge=1, le=6)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name:    Optional[str] = None
    grade:   Optional[str] = Field(None, max_length=4)
    credits: Optional[int] = Field(None, ge=1, le=6)

class CourseRead(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class SemesterBase(BaseModel):
    name: str = Field(..., max_length=100)

class SemesterCreate(SemesterBase):
    pass

class SemesterRead(SemesterBase):
    model_config = ConfigDict(from_attributes=True)
    id:         int
    created_at: datetime
    courses:    List[CourseRead] = []

class SemesterGPA(BaseModel):
    semester_id:   int
    semester_name: str
    gpa:           float
    credits:       int
    points:        float

class CumulativeGPA(BaseModel):
    cumulative_gpa:    float
    total_credits:     int
    total_points:      float
    semester_count:    int
    semesters:         List[SemesterGPA]


# ─────────────────────────────────────────────
# Resources
# ─────────────────────────────────────────────

class ResourceBase(BaseModel):
    title:       str                   = Field(..., max_length=300)
    description: Optional[str]        = None
    url:         Optional[str]        = None
    major:       MajorEnum            = MajorEnum.all
    res_type:    ResourceTypeEnum     = ResourceTypeEnum.link
    icon:        Optional[str]        = None

class ResourceCreate(ResourceBase):
    pass

class ResourceRead(ResourceBase):
    model_config = ConfigDict(from_attributes=True)
    id:          int
    created_at:  datetime
    click_count: int


# ─────────────────────────────────────────────
# ML / Analytics responses
# ─────────────────────────────────────────────

class FlashcardRecommendation(BaseModel):
    card_id:    int
    deck_id:    int
    question:   str
    score:      float   # urgency 0–1
    reason:     str     # "overdue", "low accuracy", "new"

class WorkloadReport(BaseModel):
    overdue_tasks:     int
    due_this_week:     int
    completion_rate:   float
    busiest_day:       Optional[str]
    recommended_focus: Optional[str]   # e.g. "CS assignments"

class GPATrend(BaseModel):
    semesters: List[str]
    gpas:      List[float]
    predicted_next: Optional[float]
    trend:          str   # "improving", "stable", "declining"
