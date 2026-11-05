from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..models import Deck, Card
from ..schemas import DeckCreate, DeckRead, CardCreate, CardRead, CardReview
from ..ml.engine import MLEngine

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
