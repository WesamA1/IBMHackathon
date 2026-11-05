from .updates import router as updates_router
from .flashcards import router as flashcards_router
from .tasks import router as tasks_router
from .events import router as events_router
from .gpa import router as gpa_router
from .resources import router as resources_router

__all__ = [
    "updates_router",
    "flashcards_router",
    "tasks_router",
    "events_router",
    "gpa_router",
    "resources_router",
]
