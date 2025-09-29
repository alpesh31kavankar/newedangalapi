from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.question_round import QuestionRound
from ..schemas.question_round import QuestionRoundCreate, QuestionRoundOut
from datetime import datetime , timezone, timedelta
from ..models.question import Question
from ..models.category import Category

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

# @router.get("/category/{category_id}", response_model=list[QuestionRoundOut])
# def get_rounds_by_category(category_id: int, db: Session = Depends(get_db)):
#     rounds = (
#         db.query(QuestionRound)
#         .filter(QuestionRound.categories_id == category_id)
#         .order_by(QuestionRound.release_time.desc())
#         .all()
#     )
#     if not rounds:
#         raise HTTPException(status_code=404, detail="No rounds found for this category")
#     return rounds


# @router.get("/category/{category_id}")
# def get_rounds_by_category(category_id: int, db: Session = Depends(get_db)):
#     rounds = (
#         db.query(QuestionRound)
#         .filter(QuestionRound.categories_id == category_id)
#         .order_by(QuestionRound.release_time.desc())
#         .all()
#     )
#     if not rounds:
#         raise HTTPException(status_code=404, detail="No rounds found for this category")

#     result = []
#     for r in rounds:
#         category = db.query(Category).filter(Category.id == r.categories_id).first()
#         question = db.query(Question).filter(Question.id == r.questions_id).first()

#         total_votes = r.votes_product1 + r.votes_product2

#         result.append({
#             "round_id": r.id,
#             "release_time": r.release_time,
#             "category_name": category.category_name,
#             "category_image": category.image_url,
#             "question_text": question.question_text,
#            "votes_so_far": r.votes_product1 + r.votes_product2,
#             "max_votes": r.max_votes
#         })

#     return result



@router.get("/category/{category_id}")
def get_rounds_by_category(category_id: int, db: Session = Depends(get_db)):
    rounds = (
        db.query(QuestionRound)
        .filter(QuestionRound.categories_id == category_id)
        .order_by(QuestionRound.release_time.desc())
        .all()
    )
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds found for this category")

    # Get category (for interval + info)
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Latest round = first in ordered list
    latest_round = rounds[0]

    # Calculate next round time
    next_round_time = latest_round.release_time + timedelta(minutes=category.round_interval_minutes)

    # Current UTC time
    now = datetime.now(timezone.utc)

    # Remaining seconds until next round
    remaining_seconds = max(0, int((next_round_time - now).total_seconds()))

    result = []
    for r in rounds:
        question = db.query(Question).filter(Question.id == r.questions_id).first()
        result.append({
            "round_id": r.id,
            "release_time": r.release_time,
            "category_name": category.category_name,
            "category_image": category.image_url,
            "question_text": question.question_text,
            "votes_so_far": (r.votes_product1 or 0) + (r.votes_product2 or 0),
            "max_votes": r.max_votes
        })

    return {
        "category_id": category.id,
        "category_name": category.category_name,
        "category_image": category.image_url,
        "round_interval_minutes": category.round_interval_minutes,
        "next_round_time": next_round_time.isoformat(),
        "remaining_seconds": remaining_seconds,
        "rounds": result
    }



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
