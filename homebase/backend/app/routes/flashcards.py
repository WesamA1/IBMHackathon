from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..database import get_db
from ..models import Deck, Card, MajorEnum
from ..schemas import DeckCreate, DeckRead, CardCreate, CardRead, CardReview
from ..ml.engine import MLEngine
from ..services.flashcard_generator import generate_flashcards
from ..config import get_settings
from pydantic import BaseModel

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


# ── Decks ──────────────────────────────────────────────────────────────────

@router.get("/decks", response_model=List[DeckRead])
def list_decks(db: Session = Depends(get_db)):
    return db.query(Deck).order_by(Deck.updated_at.desc()).all()


@router.post("/decks", response_model=DeckRead, status_code=201)
def create_deck(payload: DeckCreate, db: Session = Depends(get_db)):
    deck = Deck(**payload.model_dump())
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


@router.get("/decks/{deck_id}", response_model=DeckRead)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(404, "Deck not found")
    return deck


@router.delete("/decks/{deck_id}", status_code=204)
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(404, "Deck not found")
    db.delete(deck)
    db.commit()


# ── Cards ──────────────────────────────────────────────────────────────────

@router.post("/decks/{deck_id}/cards", response_model=CardRead, status_code=201)
def add_card(deck_id: int, payload: CardCreate, db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(404, "Deck not found")
    card = Card(deck_id=deck_id, **payload.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: int, db: Session = Depends(get_db)):
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(404, "Card not found")
    db.delete(card)
    db.commit()


@router.post("/cards/{card_id}/review", response_model=CardRead)
def review_card(card_id: int, payload: CardReview, db: Session = Depends(get_db)):
    """
    Record a study result and update spaced-repetition scheduling.
    Uses SM-2 algorithm; ready to swap for an ML-trained scheduler.
    """
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(404, "Card not found")

    card.times_seen += 1
    if payload.correct:
        card.times_correct += 1

    # SM-2 update
    rating = payload.rating  # 1–5
    if rating < 3:
        card.interval_days = 1
        card.ease_factor = max(1.3, card.ease_factor - 0.2)
    else:
        if card.times_seen == 1:
            card.interval_days = 1
        elif card.times_seen == 2:
            card.interval_days = 6
        else:
            card.interval_days = round(card.interval_days * card.ease_factor)
        card.ease_factor = max(1.3, card.ease_factor + 0.1 - (5 - rating) * 0.08)

    card.next_review_date = date.today().__class__.fromordinal(
        date.today().toordinal() + card.interval_days
    )
    db.commit()
    db.refresh(card)
    return card


@router.get("/decks/{deck_id}/recommend")
def recommend_cards(deck_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Return cards sorted by ML urgency score (due date + accuracy)."""
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(404, "Deck not found")
    engine = MLEngine(db)
    return engine.recommend_cards(deck_id=deck_id, limit=limit)


# ── Notes → Flashcards generation ─────────────────────────────────────────

class GenerateResult(BaseModel):
    deck_id:       int
    deck_name:     str
    cards_created: int


def _extract_text_from_pdf(data: bytes) -> str:
    """Pull plain text from all pages of a PDF."""
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages).strip()
    if not text:
        raise HTTPException(422, "PDF appears to have no extractable text (scanned image PDFs are not supported).")
    return text


def _run_generate(notes: str, deck_name: str, major: MajorEnum,
                  deck_id: Optional[int], db: Session) -> GenerateResult:
    """Shared logic used by both the JSON and multipart endpoints."""
    if not notes.strip():
        raise HTTPException(422, "notes cannot be empty")

    if deck_id is not None:
        deck = db.get(Deck, deck_id)
        if not deck:
            raise HTTPException(404, "Deck not found")
    else:
        deck = Deck(name=deck_name, icon="🤖", major=major)
        db.add(deck)
        db.flush()

    try:
        card_dicts = generate_flashcards(notes)
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(503, str(exc))
    except Exception as exc:
        db.rollback()
        raise HTTPException(502, f"Flashcard generation failed: {exc}")

    for item in card_dicts:
        db.add(Card(deck_id=deck.id, question=item["question"], answer=item["answer"]))

    db.commit()
    db.refresh(deck)
    return GenerateResult(deck_id=deck.id, deck_name=deck.name, cards_created=len(card_dicts))


# ── JSON endpoint (plain text notes) ──────────────────────────────────────

class GenerateRequest(BaseModel):
    notes:     str
    deck_id:   int | None = None
    deck_name: str = "Generated Deck"
    major:     MajorEnum = MajorEnum.cs


@router.post("/generate", response_model=GenerateResult, status_code=201)
def generate_from_notes(payload: GenerateRequest, db: Session = Depends(get_db)):
    """Generate flashcards from pasted text notes."""
    return _run_generate(payload.notes, payload.deck_name, payload.major, payload.deck_id, db)


# ── Multipart endpoint (PDF upload) ───────────────────────────────────────

@router.post("/generate/pdf", response_model=GenerateResult, status_code=201)
async def generate_from_pdf(
    file:      UploadFile  = File(..., description="PDF file"),
    deck_name: str         = Form("Generated Deck"),
    major:     MajorEnum   = Form(MajorEnum.cs),
    deck_id:   Optional[int] = Form(None),
    db:        Session     = Depends(get_db),
):
    """Generate flashcards from an uploaded PDF."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(422, "Only PDF files are supported.")
    data = await file.read()
    notes = _extract_text_from_pdf(data)
    return _run_generate(notes, deck_name, major, deck_id, db)
