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
               body="Join us for our first meeting of the semester! Free pizza, officer elections, and project pitches. All EE/CpE students welcome.",
               major=MajorEnum.ee, post_type=PostTypeEnum.club,
               event_date=date(2026,11,10), event_time="18:00", location="ESB 202"),
        Update(title="Guest Speaker: Dr. Kim on Quantum Computing",
               body="Dr. Lisa Kim from IBM Research presents on the future of quantum hardware and its impact on CS. Q&A to follow.",
               major=MajorEnum.cs, post_type=PostTypeEnum.speaker,
               event_date=date(2026,11,12), event_time="17:00", location="MSBIC Auditorium"),
        Update(title="CpE Senior Design — Final Documentation Due",
               body="Final documentation, demo video, and poster submission due Friday at 11:59 PM. Submit all files via eCampus under EE 490.",
               major=MajorEnum.cpe, post_type=PostTypeEnum.deadline,
               event_date=date(2026,11,15), event_time="23:59", location="eCampus"),
        Update(title="WVU Cybersecurity Club — CTF Prep Session",
               body="Practice challenges to prep for CPTC regionals. Topics: web exploitation, reverse engineering, forensics. All levels welcome.",
               major=MajorEnum.cybe, post_type=PostTypeEnum.club,
               event_date=date(2026,11,8), event_time="19:00", location="COMPS 317"),
        Update(title="ACM — IBM Hackathon Team Formation Night",
               body="Looking for teammates for the IBM Hackathon? Come pitch your idea or join an existing team. Snacks provided.",
               major=MajorEnum.cs, post_type=PostTypeEnum.event,
               event_date=date(2026,11,9), event_time="15:30", location="ESB 120"),
        Update(title="LCSEE Career Fair — Spring 2027 Registration Open",
               body="Register your résumé on Handshake before Nov 20. Over 40 companies attending including Lockheed, Northrop, and Leidos.",
               major=MajorEnum.all, post_type=PostTypeEnum.event,
               event_date=date(2026,11,20), event_time="10:00", location="Mountainlair Ballroom"),
        Update(title="CS 101 — Drop-In Tutoring Starts This Week",
               body="Free peer tutoring for CS 101 (Intro to Programming). No appointment needed. Mondays & Wednesdays 5–7 PM.",
               major=MajorEnum.cs, post_type=PostTypeEnum.event,
               event_date=date(2026,11,7), event_time="17:00", location="ESB 321"),
        Update(title="EE Power Systems Lab — Equipment Reservation Open",
               body="Lab slots for EE 341 power experiments are now bookable through the LCSEE portal. Reserve at least 48 hrs in advance.",
               major=MajorEnum.ee, post_type=PostTypeEnum.event,
               event_date=date(2026,11,11), event_time="08:00", location="ESB Power Lab"),
    ])


def _seed_flashcards(db):
    if db.query(Deck).count():
        return

    d1 = Deck(name="Digital Logic (EE/CpE)", icon="⚡", major=MajorEnum.ee)
    d2 = Deck(name="Data Structures & Algorithms", icon="🌲", major=MajorEnum.cs)
    d3 = Deck(name="Operating Systems", icon="🖥️", major=MajorEnum.cs)
    d4 = Deck(name="Network Security Fundamentals", icon="🔐", major=MajorEnum.cybe)
    d5 = Deck(name="Circuit Analysis (EE 221)", icon="🔌", major=MajorEnum.ee)
    db.add_all([d1, d2, d3, d4, d5])
    db.flush()

    db.add_all([
        # Digital Logic
        Card(deck_id=d1.id, question="What is a flip-flop?",
             answer="A sequential circuit element that stores one bit of state, triggered by a clock edge."),
        Card(deck_id=d1.id, question="What does a full adder do?",
             answer="Adds three 1-bit inputs (A, B, Cin) and produces a Sum and Carry-out."),
        Card(deck_id=d1.id, question="Define Karnaugh Map (K-Map)",
             answer="A visual grid method for minimizing Boolean expressions by grouping adjacent 1s."),
        Card(deck_id=d1.id, question="What is the difference between combinational and sequential logic?",
             answer="Combinational output depends only on current inputs; sequential output depends on inputs AND stored state."),
        Card(deck_id=d1.id, question="What is setup time in a flip-flop?",
             answer="The minimum time the data input must be stable BEFORE the clock edge for reliable capture."),

        # Data Structures
        Card(deck_id=d2.id, question="Big-O of binary search on a sorted array?",
             answer="O(log n) time, O(1) space (iterative)."),
        Card(deck_id=d2.id, question="Difference between a stack and a queue?",
             answer="Stack = LIFO (Last In First Out); Queue = FIFO (First In First Out)."),
        Card(deck_id=d2.id, question="What is a hash collision?",
             answer="When two different keys map to the same hash table index. Resolved by chaining or open addressing."),
        Card(deck_id=d2.id, question="Time complexity of inserting into a balanced BST?",
             answer="O(log n) — the tree height is kept at log n after rotations."),
        Card(deck_id=d2.id, question="What is dynamic programming?",
             answer="An optimization technique that solves complex problems by breaking them into overlapping subproblems and caching results (memoization)."),

        # Operating Systems
        Card(deck_id=d3.id, question="What is a process vs. a thread?",
             answer="A process is an independent program with its own memory space; a thread is a lightweight unit of execution within a process sharing the same memory."),
        Card(deck_id=d3.id, question="What is a deadlock?",
             answer="A state where two or more processes are each waiting for a resource held by the other, causing all to block forever."),
        Card(deck_id=d3.id, question="What are the four conditions for deadlock (Coffman conditions)?",
             answer="Mutual exclusion, Hold and wait, No preemption, Circular wait."),
        Card(deck_id=d3.id, question="What is virtual memory?",
             answer="An abstraction that gives each process the illusion of a large private address space, backed by disk when RAM is full (paging/swapping)."),
        Card(deck_id=d3.id, question="What does the OS scheduler's shortest job first (SJF) algorithm do?",
             answer="Picks the process with the smallest estimated burst time next, minimizing average waiting time but can cause starvation."),

        # Network Security
        Card(deck_id=d4.id, question="What is the difference between symmetric and asymmetric encryption?",
             answer="Symmetric uses the same key to encrypt and decrypt (fast, e.g. AES). Asymmetric uses a public/private key pair (slower, e.g. RSA)."),
        Card(deck_id=d4.id, question="What is a SQL injection attack?",
             answer="An attack where malicious SQL code is inserted into an input field to manipulate or dump a database."),
        Card(deck_id=d4.id, question="What is the CIA Triad?",
             answer="Confidentiality, Integrity, Availability — the three core principles of information security."),
        Card(deck_id=d4.id, question="What is a man-in-the-middle (MITM) attack?",
             answer="An attacker secretly intercepts and possibly alters communication between two parties who believe they are communicating directly."),
        Card(deck_id=d4.id, question="What is the purpose of a firewall?",
             answer="To filter incoming and outgoing network traffic based on defined security rules, blocking unauthorized access."),

        # Circuit Analysis
        Card(deck_id=d5.id, question="State Ohm's Law",
             answer="V = IR — voltage equals current times resistance."),
        Card(deck_id=d5.id, question="What is Kirchhoff's Voltage Law (KVL)?",
             answer="The sum of all voltages around any closed loop in a circuit equals zero."),
        Card(deck_id=d5.id, question="What is Kirchhoff's Current Law (KCL)?",
             answer="The sum of currents entering a node equals the sum of currents leaving it."),
        Card(deck_id=d5.id, question="What is a Thevenin equivalent circuit?",
             answer="Any linear circuit seen from two terminals can be replaced by a single voltage source (Vth) in series with a resistance (Rth)."),
        Card(deck_id=d5.id, question="What is the impedance of a capacitor at DC (0 Hz)?",
             answer="Infinite — a capacitor blocks DC current completely (Zc = 1/jωC → ∞ as ω→0)."),
    ])


def _seed_tasks(db):
    if db.query(Task).count():
        return
    db.add_all([
        # In Progress
        Task(title="Senior Design — Complete Circuit Schematic", notes="Use KiCad. Need to finalize power rail design before Friday review.",
             major=MajorEnum.cpe, priority=TaskPriorityEnum.high, status=TaskStatusEnum.inprogress,
             due_date=date(2026,11,10), course="EE 490"),
        Task(title="CS 450 — OS Assignment 3: Process Scheduling",
             notes="Implement FCFS, SJF, and Round Robin schedulers in C. Submit on eCampus.",
             major=MajorEnum.cs, priority=TaskPriorityEnum.high, status=TaskStatusEnum.inprogress,
             due_date=date(2026,11,12), course="CS 450"),

        # To Do
        Task(title="CYBE 301 — Read Ch. 7: Network Security Protocols",
             notes="Focus on TLS handshake and IPSec for quiz on Thursday.",
             major=MajorEnum.cybe, priority=TaskPriorityEnum.medium, status=TaskStatusEnum.todo,
             due_date=date(2026,11,13), course="CYBE 301"),
        Task(title="EE 201 — Lab 5 Pre-Lab Report",
             notes="Oscilloscope calibration steps + expected waveforms for RC circuit.",
             major=MajorEnum.ee, priority=TaskPriorityEnum.medium, status=TaskStatusEnum.todo,
             due_date=date(2026,11,8), course="EE 201"),
        Task(title="MATH 261 — Problem Set 9 (Partial Derivatives)",
             notes="Problems 1–15 odd. Check office hours schedule — Dr. Patel, MWF 10-11.",
             major=MajorEnum.cs, priority=TaskPriorityEnum.medium, status=TaskStatusEnum.todo,
             due_date=date(2026,11,14), course="MATH 261"),
        Task(title="CS 460 — Algorithm Analysis HW 4",
             notes="Dynamic programming problems. Coin change, LCS, and knapsack.",
             major=MajorEnum.cs, priority=TaskPriorityEnum.high, status=TaskStatusEnum.todo,
             due_date=date(2026,11,11), course="CS 460"),
        Task(title="Register for Spring 2027 Classes",
             notes="Enrollment opens Nov 18. Need: CS 481 (Compilers), EE 331, and a Tech Elective.",
             major=MajorEnum.all, priority=TaskPriorityEnum.high, status=TaskStatusEnum.todo,
             due_date=date(2026,11,18)),
        Task(title="Submit LCSEE Career Fair Resume on Handshake",
             notes="Tailor for embedded/software roles. Get reviewed at Career Services first.",
             major=MajorEnum.all, priority=TaskPriorityEnum.medium, status=TaskStatusEnum.todo,
             due_date=date(2026,11,20)),
        Task(title="CpE 465 — Study for Midterm 2",
             notes="Chapters 4–7: pipelining, hazards, cache memory. Use past exams on eCampus.",
             major=MajorEnum.cpe, priority=TaskPriorityEnum.high, status=TaskStatusEnum.todo,
             due_date=date(2026,11,17), course="CpE 465"),

        # Done
        Task(title="Study for Digital Logic Quiz 3",
             notes="K-Maps, flip-flops, state machines — got it ✓",
             major=MajorEnum.cpe, priority=TaskPriorityEnum.low, status=TaskStatusEnum.done,
             due_date=date(2026,11,5), course="EE 340"),
        Task(title="EE 221 — Lab Report 4 Submitted",
             major=MajorEnum.ee, priority=TaskPriorityEnum.medium, status=TaskStatusEnum.done,
             due_date=date(2026,11,4), course="EE 221"),
    ])


def _seed_events(db):
    if db.query(Event).count():
        return
    db.add_all([
        # Recurring classes
        Event(name="EE 201 — Circuits Lab", event_date=date(2026,11,6),
              start_time="14:00", end_time="16:50",
              event_type=EventTypeEnum.cls, location="ESB 110", repeat=RepeatEnum.weekly),
        Event(name="CS 450 — Operating Systems Lecture", event_date=date(2026,11,6),
              start_time="09:30", end_time="10:45",
              event_type=EventTypeEnum.cls, location="ESB 1001", repeat=RepeatEnum.weekly),
        Event(name="CpE 465 — Computer Architecture", event_date=date(2026,11,7),
              start_time="11:00", end_time="12:15",
              event_type=EventTypeEnum.cls, location="ESB 1001", repeat=RepeatEnum.weekly),
        Event(name="MATH 261 — Multivariable Calculus", event_date=date(2026,11,7),
              start_time="08:00", end_time="08:50",
              event_type=EventTypeEnum.cls, location="Armstrong Hall 121", repeat=RepeatEnum.daily),
        Event(name="CYBE 301 — Intro to Network Security", event_date=date(2026,11,10),
              start_time="14:00", end_time="15:15",
              event_type=EventTypeEnum.cls, location="COMPS 317", repeat=RepeatEnum.weekly),

        # Deadlines
        Event(name="CS 450 — Assignment 3 Due", event_date=date(2026,11,12),
              start_time="23:59", event_type=EventTypeEnum.deadline, location="eCampus"),
        Event(name="EE 201 — Lab 5 Pre-Lab Due", event_date=date(2026,11,8),
              start_time="23:59", event_type=EventTypeEnum.deadline, location="eCampus"),
        Event(name="Spring 2027 Class Registration Opens", event_date=date(2026,11,18),
              start_time="07:00", event_type=EventTypeEnum.deadline, location="MyAccess Portal"),

        # Exams
        Event(name="CpE 465 — Midterm 2", event_date=date(2026,11,18),
              start_time="09:00", end_time="10:15",
              event_type=EventTypeEnum.exam, location="ESB 100"),
        Event(name="CYBE 301 — Quiz 3: Network Protocols", event_date=date(2026,11,13),
              start_time="14:00", end_time="14:30",
              event_type=EventTypeEnum.exam, location="COMPS 317"),

        # Meetings
        Event(name="Senior Design Team Meeting", event_date=date(2026,11,10),
              start_time="11:00", end_time="11:50",
              event_type=EventTypeEnum.meeting, location="ESB 202"),
        Event(name="CS 460 Study Group — Esports Lounge", event_date=date(2026,11,9),
              start_time="19:00", end_time="21:00",
              event_type=EventTypeEnum.meeting, location="Evansdale Crossing"),
    ])


def _seed_gpa(db):
    if db.query(Semester).count():
        return
    # Spring 2026
    s1 = Semester(name="Spring 2026")
    db.add(s1)
    db.flush()
    db.add_all([
        Course(semester_id=s1.id, name="CS 310 — Intro to Systems",    grade="A",  credits=3),
        Course(semester_id=s1.id, name="EE 221 — Circuit Analysis I",  grade="B+", credits=4),
        Course(semester_id=s1.id, name="MATH 251 — Calculus II",       grade="B",  credits=4),
        Course(semester_id=s1.id, name="CS 220 — Discrete Math",       grade="A-", credits=3),
        Course(semester_id=s1.id, name="ENGL 101 — Composition",       grade="A",  credits=3),
    ])
    # Fall 2026
    s2 = Semester(name="Fall 2026")
    db.add(s2)
    db.flush()
    db.add_all([
        Course(semester_id=s2.id, name="CS 460 — Algorithms",          grade="B+", credits=3),
        Course(semester_id=s2.id, name="CS 450 — Operating Systems",   grade="A-", credits=3),
        Course(semester_id=s2.id, name="EE 340 — Digital Logic",       grade="A",  credits=3),
        Course(semester_id=s2.id, name="MATH 261 — Multivariable Calc",grade="B",  credits=4),
        Course(semester_id=s2.id, name="CS 410 — Software Engineering", grade="A", credits=3),
    ])


def _seed_resources(db):
    if db.query(Resource).count():
        return
    db.add_all([
        # All majors
        Resource(title="WVU eCampus", description="Course management: assignments, grades, Zoom links.",
                 url="https://ecampus.wvu.edu", major=MajorEnum.all, res_type=ResourceTypeEnum.link, icon="🏫"),
        Resource(title="WVU Library Databases", description="IEEE Xplore, ACM Digital Library, and 100+ research databases.",
                 url="https://libraries.wvu.edu", major=MajorEnum.all, res_type=ResourceTypeEnum.link, icon="📚"),
        Resource(title="WVU Career Services (Handshake)", description="Job postings, career fair registration, resume reviews.",
                 url="https://wvu.joinhandshake.com", major=MajorEnum.all, res_type=ResourceTypeEnum.contact, icon="💼"),
        Resource(title="WVU IT Help Desk", description="Software licenses, VPN, MFA, campus Wi-Fi support.",
                 url="https://it.wvu.edu", major=MajorEnum.all, res_type=ResourceTypeEnum.contact, icon="🛠"),
        Resource(title="LCSEE Advising Office", description="Degree audits, course substitutions, graduation check. ESB 2nd floor.",
                 url="https://lcsee.wvu.edu/advising", major=MajorEnum.all, res_type=ResourceTypeEnum.contact, icon="🎓"),
        Resource(title="WVU Starfish", description="Early alert system — schedule tutoring and advisor appointments.",
                 url="https://starfish.wvu.edu", major=MajorEnum.all, res_type=ResourceTypeEnum.link, icon="⭐"),

        # CS
        Resource(title="Big-O Cheat Sheet", description="Quick reference for common algorithm time and space complexities.",
                 url="https://www.bigocheatsheet.com", major=MajorEnum.cs, res_type=ResourceTypeEnum.doc, icon="🌲"),
        Resource(title="GitHub Student Developer Pack", description="Free Copilot, JetBrains, DigitalOcean credits, and more with .edu email.",
                 url="https://education.github.com/pack", major=MajorEnum.cs, res_type=ResourceTypeEnum.tool, icon="🐙"),
        Resource(title="CS50 — Harvard OpenCourseWare", description="Free video lectures and problem sets for CS fundamentals.",
                 url="https://cs50.harvard.edu", major=MajorEnum.cs, res_type=ResourceTypeEnum.video, icon="🎬"),
        Resource(title="Visualgo — Algorithm Visualizer", description="Step-by-step animations of sorting, graph, and DP algorithms.",
                 url="https://visualgo.net", major=MajorEnum.cs, res_type=ResourceTypeEnum.tool, icon="📊"),

        # EE
        Resource(title="Falstad Circuit Simulator", description="Free in-browser circuit simulator for AC/DC analysis.",
                 url="https://www.falstad.com/circuit", major=MajorEnum.ee, res_type=ResourceTypeEnum.tool, icon="🔧"),
        Resource(title="All About Circuits", description="Free textbook + community: DC, AC, semiconductors, and more.",
                 url="https://www.allaboutcircuits.com", major=MajorEnum.ee, res_type=ResourceTypeEnum.link, icon="⚡"),
        Resource(title="IEEE Xplore", description="Access IEEE journal articles, conference papers, and standards.",
                 url="https://ieeexplore.ieee.org", major=MajorEnum.ee, res_type=ResourceTypeEnum.link, icon="📡"),
        Resource(title="LTspice (Analog Devices)", description="Free SPICE circuit simulation software. Download and run locally.",
                 url="https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html",
                 major=MajorEnum.ee, res_type=ResourceTypeEnum.tool, icon="📐"),

        # CpE
        Resource(title="RISC-V ISA Specification", description="Official RISC-V unprivileged and privileged ISA specs.",
                 url="https://riscv.org/technical/specifications", major=MajorEnum.cpe, res_type=ResourceTypeEnum.doc, icon="⚙️"),
        Resource(title="Logisim Evolution", description="Free digital logic circuit design and simulation tool for CpE labs.",
                 url="https://github.com/logisim-evolution/logisim-evolution", major=MajorEnum.cpe, res_type=ResourceTypeEnum.tool, icon="🔌"),
        Resource(title="Compiler Explorer (Godbolt)", description="See what assembly your C/C++ compiles to in real time.",
                 url="https://godbolt.org", major=MajorEnum.cpe, res_type=ResourceTypeEnum.tool, icon="🔍"),

        # CYBE
        Resource(title="TryHackMe", description="Guided hands-on cybersecurity rooms for all skill levels.",
                 url="https://tryhackme.com", major=MajorEnum.cybe, res_type=ResourceTypeEnum.tool, icon="🧪"),
        Resource(title="OverTheWire Wargames", description="Practice Linux commands and CTF skills with progressive challenges.",
                 url="https://overthewire.org/wargames", major=MajorEnum.cybe, res_type=ResourceTypeEnum.tool, icon="🔐"),
        Resource(title="NIST Cybersecurity Framework", description="Official NIST CSF 2.0 — used in CYBE 301 and professional cert exams.",
                 url="https://www.nist.gov/cyberframework", major=MajorEnum.cybe, res_type=ResourceTypeEnum.doc, icon="🛡"),
    ])
