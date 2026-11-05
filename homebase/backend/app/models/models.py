"""
SQLAlchemy ORM models — one class per table.
All tables include created_at / updated_at for ML feature extraction.
"""
from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, Date, DateTime,
    ForeignKey, Enum as SAEnum, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
import enum


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class MajorEnum(str, enum.Enum):
    cs   = "cs"
    ee   = "ee"
    cpe  = "cpe"
    cybe = "cybe"
    all  = "all"


class PostTypeEnum(str, enum.Enum):
    club     = "club"
    speaker  = "speaker"
    event    = "event"
    deadline = "deadline"


class TaskStatusEnum(str, enum.Enum):
    todo       = "todo"
    inprogress = "inprogress"
    done       = "done"


class TaskPriorityEnum(str, enum.Enum):
    low    = "low"
    medium = "medium"
    high   = "high"


class EventTypeEnum(str, enum.Enum):
    cls      = "class"
    deadline = "deadline"
    exam     = "exam"
    meeting  = "meeting"
    personal = "personal"


class RepeatEnum(str, enum.Enum):
    none   = "none"
    weekly = "weekly"
    daily  = "daily"


class ResourceTypeEnum(str, enum.Enum):
    link    = "link"
    doc     = "doc"
    tool    = "tool"
    contact = "contact"
    video   = "video"


# ─────────────────────────────────────────────
# Updates / Announcements
# ─────────────────────────────────────────────

class Update(Base):
    __tablename__ = "updates"

    id:          Mapped[int]             = mapped_column(Integer, primary_key=True, index=True)
    title:       Mapped[str]             = mapped_column(String(200), nullable=False)
    body:        Mapped[Optional[str]]   = mapped_column(Text)
    major:       Mapped[MajorEnum]       = mapped_column(SAEnum(MajorEnum), default=MajorEnum.all)
    post_type:   Mapped[PostTypeEnum]    = mapped_column(SAEnum(PostTypeEnum), default=PostTypeEnum.event)
    event_date:  Mapped[Optional[date]]  = mapped_column(Date)
    event_time:  Mapped[Optional[str]]   = mapped_column(String(10))   # "HH:MM"
    location:    Mapped[Optional[str]]   = mapped_column(String(200))
    created_at:  Mapped[datetime]        = mapped_column(DateTime, server_default=func.now())
    updated_at:  Mapped[datetime]        = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    view_count:  Mapped[int]             = mapped_column(Integer, default=0)  # for ML engagement


# ─────────────────────────────────────────────
# Flashcard Decks + Cards
# ─────────────────────────────────────────────

class Deck(Base):
    __tablename__ = "decks"

    id:         Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    name:       Mapped[str]           = mapped_column(String(200), nullable=False)
    icon:       Mapped[Optional[str]] = mapped_column(String(8))
    major:      Mapped[MajorEnum]     = mapped_column(SAEnum(MajorEnum), default=MajorEnum.cs)
    created_at: Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]      = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    cards: Mapped[List["Card"]] = relationship("Card", back_populates="deck", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    deck_id:      Mapped[int]           = mapped_column(ForeignKey("decks.id"), nullable=False, index=True)
    question:     Mapped[str]           = mapped_column(Text, nullable=False)
    answer:       Mapped[str]           = mapped_column(Text, nullable=False)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())

    # ML review-scheduling fields (spaced repetition ready)
    times_seen:       Mapped[int]   = mapped_column(Integer, default=0)
    times_correct:    Mapped[int]   = mapped_column(Integer, default=0)
    ease_factor:      Mapped[float] = mapped_column(Float, default=2.5)   # SM-2 algorithm
    interval_days:    Mapped[int]   = mapped_column(Integer, default=1)
    next_review_date: Mapped[Optional[date]] = mapped_column(Date)

    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")


# ─────────────────────────────────────────────
# Tasks (Kanban)
# ─────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id:         Mapped[int]                = mapped_column(Integer, primary_key=True, index=True)
    title:      Mapped[str]               = mapped_column(String(300), nullable=False)
    notes:      Mapped[Optional[str]]     = mapped_column(Text)
    major:      Mapped[MajorEnum]         = mapped_column(SAEnum(MajorEnum), default=MajorEnum.cs)
    priority:   Mapped[TaskPriorityEnum]  = mapped_column(SAEnum(TaskPriorityEnum), default=TaskPriorityEnum.medium)
    status:     Mapped[TaskStatusEnum]    = mapped_column(SAEnum(TaskStatusEnum), default=TaskStatusEnum.todo)
    due_date:   Mapped[Optional[date]]    = mapped_column(Date)
    course:     Mapped[Optional[str]]     = mapped_column(String(100))
    created_at: Mapped[datetime]          = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]          = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)   # for ML velocity tracking


# ─────────────────────────────────────────────
# Planner Events
# ─────────────────────────────────────────────

class Event(Base):
    __tablename__ = "events"

    id:          Mapped[int]               = mapped_column(Integer, primary_key=True, index=True)
    name:        Mapped[str]               = mapped_column(String(300), nullable=False)
    event_date:  Mapped[date]              = mapped_column(Date, nullable=False, index=True)
    start_time:  Mapped[Optional[str]]     = mapped_column(String(10))
    end_time:    Mapped[Optional[str]]     = mapped_column(String(10))
    event_type:  Mapped[EventTypeEnum]     = mapped_column(SAEnum(EventTypeEnum), default=EventTypeEnum.personal)
    location:    Mapped[Optional[str]]     = mapped_column(String(200))
    repeat:      Mapped[RepeatEnum]        = mapped_column(SAEnum(RepeatEnum), default=RepeatEnum.none)
    created_at:  Mapped[datetime]          = mapped_column(DateTime, server_default=func.now())


# ─────────────────────────────────────────────
# GPA — Semesters + Courses
# ─────────────────────────────────────────────

class Semester(Base):
    __tablename__ = "semesters"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    name:       Mapped[str]      = mapped_column(String(100), nullable=False)   # "Fall 2026"
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    courses: Mapped[List["Course"]] = relationship("Course", back_populates="semester", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    semester_id: Mapped[int]           = mapped_column(ForeignKey("semesters.id"), nullable=False, index=True)
    name:        Mapped[str]           = mapped_column(String(200), nullable=False)
    grade:       Mapped[str]           = mapped_column(String(4))     # "A", "B+", etc.
    credits:     Mapped[int]           = mapped_column(Integer, default=3)
    created_at:  Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())

    semester: Mapped["Semester"] = relationship("Semester", back_populates="courses")


# ─────────────────────────────────────────────
# Resources
# ─────────────────────────────────────────────

class Resource(Base):
    __tablename__ = "resources"

    id:          Mapped[int]                  = mapped_column(Integer, primary_key=True, index=True)
    title:       Mapped[str]                  = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]]        = mapped_column(Text)
    url:         Mapped[Optional[str]]        = mapped_column(String(500))
    major:       Mapped[MajorEnum]            = mapped_column(SAEnum(MajorEnum), default=MajorEnum.all)
    res_type:    Mapped[ResourceTypeEnum]     = mapped_column(SAEnum(ResourceTypeEnum), default=ResourceTypeEnum.link)
    icon:        Mapped[Optional[str]]        = mapped_column(String(8))
    created_at:  Mapped[datetime]             = mapped_column(DateTime, server_default=func.now())
    click_count: Mapped[int]                  = mapped_column(Integer, default=0)  # for ML popularity ranking
