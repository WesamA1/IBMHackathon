"""
Seed the database with sample data on first run.
Checks if each table is empty before inserting — idempotent.
"""
from datetime import date
from .database import SessionLocal
from .models import (
    Update, Deck, Card, Task, Event, Semester, Course, Resource,
    MajorEnum, PostTypeEnum, TaskStatusEnum, TaskPriorityEnum,
    EventTypeEnum, RepeatEnum, ResourceTypeEnum,
)


def seed_db() -> None:
    db = SessionLocal()
    try:
        _seed_updates(db)
        _seed_flashcards(db)
        _seed_tasks(db)
        _seed_events(db)
        _seed_gpa(db)
        _seed_resources(db)
        db.commit()
    finally:
        db.close()


def _seed_updates(db):
    if db.query(Update).count():
        return
    db.add_all([
        Update(title="IEEE Student Branch — Fall Kickoff",
               body="Join us for our first meeting of the semester! Free pizza, officer elections, and project pitches.",
               major=MajorEnum.ee, post_type=PostTypeEnum.club,
               event_date=date(2026,11,10), event_time="18:00", location="ESB 202"),
        Update(title="Guest Speaker: Dr. Kim on Quantum Computing",
               body="Dr. Lisa Kim from IBM Research will present on the future of quantum hardware.",
               major=MajorEnum.cs, post_type=PostTypeEnum.speaker,
               event_date=date(2026,11,12), event_time="17:00", location="MSBIC Auditorium"),
        Update(title="CpE Senior Design Project Deadline",
               body="Final documentation and demo videos due Friday 11:59 PM. Submit via eCampus.",
               major=MajorEnum.cpe, post_type=PostTypeEnum.deadline,
               event_date=date(2026,11,15), event_time="23:59", location="eCampus"),
        Update(title="WVU Cybersecurity Club — CTF Prep Session",
               body="Practice CTF challenges to prep for CPTC. All skill levels welcome.",
               major=MajorEnum.cybe, post_type=PostTypeEnum.club,
               event_date=date(2026,11,8), event_time="19:00", location="COMPS 317"),
        Update(title="ACM — Hackathon Team Formation",
               body="Looking to form teams for the IBM Hackathon? Come find teammates!",
               major=MajorEnum.cs, post_type=PostTypeEnum.event,
               event_date=date(2026,11,9), event_time="15:30", location="ESB 120"),
    ])


def _seed_flashcards(db):
    if db.query(Deck).count():
        return
    d1 = Deck(name="Digital Logic", icon="⚡", major=MajorEnum.ee)
    d2 = Deck(name="Data Structures", icon="🌲", major=MajorEnum.cs)
    db.add_all([d1, d2])
    db.flush()
    db.add_all([
        Card(deck_id=d1.id, question="What is a flip-flop?",
             answer="A sequential circuit element that stores one bit of state."),
        Card(deck_id=d1.id, question="What does a full adder do?",
             answer="Adds three input bits and produces a sum and carry-out."),
        Card(deck_id=d1.id, question="Define Karnaugh Map",
             answer="A visual method for simplifying Boolean algebra expressions."),
        Card(deck_id=d2.id, question="Big-O of binary search?",
             answer="O(log n)"),
        Card(deck_id=d2.id, question="Difference between stack and queue?",
             answer="Stack is LIFO; Queue is FIFO."),
    ])


def _seed_tasks(db):
    if db.query(Task).count():
        return
    db.add_all([
        Task(title="Complete Senior Design Proposal", notes="Needs circuit diagram",
             major=MajorEnum.cpe, priority=TaskPriorityEnum.high, status=TaskStatusEnum.inprogress,
             due_date=date(2026,11,10), course="EE 490"),
        Task(title="Operating Systems — Assignment 3", notes="Process scheduling",
             major=MajorEnum.cs, priority=TaskPriorityEnum.high, status=TaskStatusEnum.todo,
             due_date=date(2026,11,12), course="CS 450"),
        Task(title="Read Ch. 7 — Network Security",
             major=MajorEnum.cybe, priority=TaskPriorityEnum.medium, status=TaskStatusEnum.todo,
             due_date=date(2026,11,15), course="CYBE 301"),
        Task(title="Lab 5 Pre-Lab", notes="Oscilloscope setup",
             major=MajorEnum.ee, priority=TaskPriorityEnum.medium, status=TaskStatusEnum.todo,
             due_date=date(2026,11,8), course="EE 201"),
        Task(title="Study for Digital Logic Quiz", notes="KMaps, FFs",
             major=MajorEnum.cpe, priority=TaskPriorityEnum.low, status=TaskStatusEnum.done,
             due_date=date(2026,11,5)),
    ])


def _seed_events(db):
    if db.query(Event).count():
        return
    db.add_all([
        Event(name="EE 201 — Lab Section", event_date=date(2026,11,6),
              start_time="14:00", end_time="16:50",
              event_type=EventTypeEnum.cls, location="ESB 110", repeat=RepeatEnum.weekly),
        Event(name="CS 450 Assignment Due", event_date=date(2026,11,12),
              start_time="23:59", event_type=EventTypeEnum.deadline, location="eCampus"),
        Event(name="Senior Design Meeting", event_date=date(2026,11,10),
              start_time="11:00", end_time="11:50",
              event_type=EventTypeEnum.meeting, location="ESB 202"),
        Event(name="CpE 465 Midterm", event_date=date(2026,11,18),
              start_time="09:00", end_time="10:15",
              event_type=EventTypeEnum.exam, location="ESB 100"),
    ])


def _seed_gpa(db):
    if db.query(Semester).count():
        return
    s = Semester(name="Fall 2026")
    db.add(s)
    db.flush()
    db.add_all([
        Course(semester_id=s.id, name="CS 460 — Algorithms",       grade="B+", credits=3),
        Course(semester_id=s.id, name="EE 221 — Circuit Analysis",  grade="A-", credits=4),
        Course(semester_id=s.id, name="MATH 261 — Multivariable",   grade="B",  credits=4),
        Course(semester_id=s.id, name="CS 410 — Software Eng.",     grade="A",  credits=3),
    ])


def _seed_resources(db):
    if db.query(Resource).count():
        return
    db.add_all([
        Resource(title="WVU eCampus", description="Course management system.",
                 url="https://ecampus.wvu.edu", major=MajorEnum.all, res_type=ResourceTypeEnum.link, icon="🏫"),
        Resource(title="WVU Library Databases", description="IEEE Xplore, ACM DL, and more.",
                 url="https://libraries.wvu.edu", major=MajorEnum.all, res_type=ResourceTypeEnum.link, icon="📚"),
        Resource(title="Big-O Cheat Sheet", description="Quick reference for algorithm complexities.",
                 url="https://www.bigocheatsheet.com", major=MajorEnum.cs, res_type=ResourceTypeEnum.doc, icon="🌲"),
        Resource(title="Falstad Circuit Simulator", description="In-browser interactive circuit simulator.",
                 url="https://www.falstad.com/circuit", major=MajorEnum.ee, res_type=ResourceTypeEnum.tool, icon="🔧"),
        Resource(title="RISC-V Spec", description="Official RISC-V ISA specification.",
                 url="https://riscv.org/technical/specifications", major=MajorEnum.cpe, res_type=ResourceTypeEnum.doc, icon="⚙️"),
        Resource(title="TryHackMe", description="Hands-on cybersecurity training.",
                 url="https://tryhackme.com", major=MajorEnum.cybe, res_type=ResourceTypeEnum.tool, icon="🧪"),
    ])
