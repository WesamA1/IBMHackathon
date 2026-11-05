# WVU LCSEE Home Base — Backend

FastAPI + SQLite backend for the LCSEE student portal. Provides a fully versioned REST API at `/api/v1/` that the frontend HTML pages consume via `api.js`.

## Quick Start

```bash
cd homebase/backend
./start.sh --reload      # auto-restarts on code changes
```

Server starts at **http://localhost:8000**  
Interactive API docs: **http://localhost:8000/api/docs**

## Architecture

```
backend/
├── app/
│   ├── main.py          # FastAPI app, CORS, lifespan (DB init + seed)
│   ├── config.py        # Pydantic Settings (reads .env)
│   ├── database.py      # SQLAlchemy engine, SessionLocal, Base
│   ├── seed.py          # First-run sample data
│   ├── models/          # SQLAlchemy ORM table definitions
│   ├── schemas/         # Pydantic v2 request/response models
│   ├── routes/          # One router per domain
│   │   ├── updates.py
│   │   ├── flashcards.py
│   │   ├── tasks.py
│   │   ├── events.py
│   │   ├── gpa.py
│   │   └── resources.py
│   ├── services/
│   │   └── gpa_service.py   # Pure GPA calculation logic
│   └── ml/
│       ├── engine.py        # MLEngine dispatcher
│       ├── features.py      # Feature extraction (card & task vectors)
│       ├── recommender.py   # Flashcard urgency recommender (SM-2 + rule-based)
│       └── analytics.py     # Workload report, GPA trend analysis
├── requirements.txt
├── .env.example
└── start.sh
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/updates` | List announcements (filter: major, post_type, search) |
| POST | `/api/v1/updates` | Create announcement |
| DELETE | `/api/v1/updates/{id}` | Delete announcement |
| POST | `/api/v1/updates/{id}/view` | Record view (ML engagement signal) |
| GET | `/api/v1/flashcards/decks` | List all decks with cards |
| POST | `/api/v1/flashcards/decks` | Create deck |
| POST | `/api/v1/flashcards/decks/{id}/cards` | Add card to deck |
| POST | `/api/v1/flashcards/cards/{id}/review` | Record study result (SM-2 scheduling) |
| GET | `/api/v1/flashcards/decks/{id}/recommend` | ML-ranked card recommendations |
| GET | `/api/v1/tasks` | List tasks (filter: status, priority, major, search) |
| POST | `/api/v1/tasks` | Create task |
| PATCH | `/api/v1/tasks/{id}` | Update task / move between columns |
| GET | `/api/v1/tasks/workload-report` | ML workload analysis |
| GET | `/api/v1/events/expand?start=&end=` | Events with repeat expansion |
| POST | `/api/v1/events` | Create event |
| GET | `/api/v1/gpa/semesters` | List semesters with courses |
| POST | `/api/v1/gpa/semesters` | Create semester |
| POST | `/api/v1/gpa/semesters/{id}/courses` | Add course |
| GET | `/api/v1/gpa/cumulative` | Calculated cumulative GPA |
| GET | `/api/v1/gpa/trend` | GPA trend + predicted next semester |
| GET | `/api/v1/resources` | List resources (filter: major, res_type) |
| POST | `/api/v1/resources/{id}/click` | Record click (ML popularity signal) |

## ML Layer

The `app/ml/` package is structured for progressive ML upgrades:

- **Now**: Rule-based scoring (SM-2 spaced repetition, urgency heuristics, linear regression for GPA trends)
- **Next**: Drop sklearn `GradientBoostingRegressor` / `LinearRegression` into `recommender.py` and `analytics.py` — the feature vectors are already built in `features.py`
- **Future**: Collaborative filtering across users, NLP-based study recommendation from course names

### Upgrading to a trained model

```python
# In ml/recommender.py, replace _score_rule with:
import joblib
model = joblib.load("models/card_ranker.pkl")
scores = model.predict([f.to_vector() for f in features])
```

## Configuration

Copy `.env.example` → `.env` and edit:

```
DATABASE_URL=sqlite:///./homebase.db   # swap for postgresql://... in production
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

## Database

SQLite by default — zero setup. Swap `DATABASE_URL` for a PostgreSQL URL and the same code works unchanged (SQLAlchemy handles the difference).

Tables are created automatically on first startup. The `seed.py` module inserts sample data if each table is empty — safe to run repeatedly.
