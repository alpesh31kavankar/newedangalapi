from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.question_round import QuestionRound
from ..schemas.question_round import QuestionRoundCreate, QuestionRoundOut
from datetime import datetime

router = APIRouter(prefix="/rounds", tags=["rounds"])

# -----------------------------
# Create a new question round
# -----------------------------
@router.post("/", response_model=QuestionRoundOut)
def create_round(round_in: QuestionRoundCreate, db: Session = Depends(get_db)):
    if round_in.product1_id == round_in.product2_id:
        raise HTTPException(status_code=400, detail="Products must be different")
    
    new_round = QuestionRound(**round_in.dict())
    db.add(new_round)
    db.commit()
    db.refresh(new_round)
    return new_round

# -------------------------------------------
# Get all rounds for a specific category
# Use query parameter to avoid path conflicts
# -------------------------------------------
@router.get("/by-category", response_model=list[QuestionRoundOut])
def get_rounds_by_category(category_id: int, db: Session = Depends(get_db)):
    rounds = (
        db.query(QuestionRound)
        .filter(QuestionRound.categories_id == category_id)
        .order_by(QuestionRound.release_time.desc())
        .all()
    )
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds found for this category")
    return rounds

# -----------------------------
# Get all rounds
# -----------------------------
@router.get("/", response_model=list[QuestionRoundOut])
def get_rounds(db: Session = Depends(get_db)):
    return db.query(QuestionRound).all()

# -----------------------------
# Get a single round by ID
# -----------------------------
@router.get("/id/{round_id}", response_model=QuestionRoundOut)
def get_round(round_id: int, db: Session = Depends(get_db)):
    round_obj = db.query(QuestionRound).filter(QuestionRound.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    return round_obj
