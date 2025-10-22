from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.question_round import QuestionRound
from ..schemas.question_round import QuestionRoundCreate, QuestionRoundOut
from datetime import datetime , timezone, timedelta
from ..models.question import Question
from ..models.category import Category
from ..models.product import Product
from ..models.question_round import QuestionRound
from ..models.vote import Vote
from ..models.token import Token
from ..models.user import User
from ..routes.auth import get_current_user 

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


from ..models.vote import Vote

@router.get("/category/{category_id}")
def get_rounds_by_category(category_id: int, db: Session = Depends(get_db)):
    rounds = (
        db.query(QuestionRound)
        .filter(QuestionRound.categories_id == category_id)
        .filter(QuestionRound.is_locked == False) 
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

        # ✅ live counts from votes table
        votes_product1 = db.query(Vote).filter(
            Vote.question_rounds_id == r.id,
            Vote.products_id == r.product1_id
        ).count()

        votes_product2 = db.query(Vote).filter(
            Vote.question_rounds_id == r.id,
            Vote.products_id == r.product2_id
        ).count()

        result.append({
            "round_id": r.id,
            "release_time": r.release_time,
            "category_name": category.category_name,
            "category_image": category.image_url,
            "question_text": question.question_text if question else "",
            "votes_product1": votes_product1,
            "votes_product2": votes_product2,
            "votes_so_far": votes_product1 + votes_product2,
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

@router.get("/question-round/{round_id}")
def get_question_round(round_id: int, db: Session = Depends(get_db)):
    round = db.query(QuestionRound).filter(QuestionRound.id == round_id).first()
    if not round:
        raise HTTPException(status_code=404, detail="Round not found")

    question = db.query(Question).filter(Question.id == round.questions_id).first()
    product1 = db.query(Product).filter(Product.id == round.product1_id).first()
    product2 = db.query(Product).filter(Product.id == round.product2_id).first()

    return {
        "id": round.id,
        "question_text": question.question_text if question else "",
        "votes_product1": round.votes_product1,
        "votes_product2": round.votes_product2,
        "max_votes": round.max_votes,
        "product1": {
            "id": product1.id,
            "name": product1.name,
            "image_url": product1.image_url,
            "nationality": product1.nationality,
            "detail": product1.details,
        } if product1 else {},
        "product2": {
            "id": product2.id,
            "name": product2.name,
            "image_url": product2.image_url,
            "nationality": product2.nationality,
            "detail": product2.details,
        } if product2 else {},
    }

@router.get("/all-rounds")
def get_all_rounds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch all rounds (latest first)
    rounds = db.query(QuestionRound).order_by(QuestionRound.release_time.desc()).all()
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds found")

    result = []

    for r in rounds:
        category = db.query(Category).filter(Category.id == r.categories_id).first()
        question = db.query(Question).filter(Question.id == r.questions_id).first()
        product1 = db.query(Product).filter(Product.id == r.product1_id).first()
        product2 = db.query(Product).filter(Product.id == r.product2_id).first()

        # Vote counts for each product
        votes_product1 = db.query(Vote).filter(
            Vote.question_rounds_id == r.id,
            Vote.products_id == r.product1_id
        ).count()
        votes_product2 = db.query(Vote).filter(
            Vote.question_rounds_id == r.id,
            Vote.products_id == r.product2_id
        ).count()

        # Current user vote
        user_vote = db.query(Vote).filter(
            Vote.question_rounds_id == r.id,
            Vote.users_id == current_user.id
        ).first()
        user_voted_product = None
        if user_vote:
            voted_product = db.query(Product).filter(Product.id == user_vote.products_id).first()
            if voted_product:
                user_voted_product = {
                    "id": voted_product.id,
                    "name": voted_product.name,
                    "image_url": voted_product.image_url
                }

        # Check if current user won
        win_token = db.query(Token).filter(
            Token.users_id == current_user.id,
            Token.question_rounds_id == r.id,
            Token.token_id.like("W%")
        ).first()
        user_win = None
        if win_token:
            winning_product = db.query(Product).filter(Product.id == win_token.product_id).first()
            if winning_product:
                user_win = {
                    "id": winning_product.id,
                    "product_name": winning_product.name,
                    "product_image": winning_product.image_url
                }

        # Determine winner side if round is locked
        winning_side = None
        if r.is_locked:
            if votes_product1 > votes_product2:
                winning_side = "product1"
            elif votes_product2 > votes_product1:
                winning_side = "product2"
            else:
                winning_side = "tie"

        # --------------------------
        # Collect all participants from votes
        # --------------------------
        participants = []
        votes = db.query(Vote).filter(Vote.question_rounds_id == r.id).all()
        for v in votes:
            user = db.query(User).filter(User.id == v.users_id).first()
            if user:
                avatar_url = (
                    f"http://127.0.0.1:8000/uploads/profile_images/{user.profile_image}"
                    if user.profile_image else
                    "http://127.0.0.1:8000/assets/default_avatar.png"
                )
                participants.append({
                    "id": user.id,
                    "name": user.username,
                    "avatar": avatar_url,
                    "votedTo": v.products_id
                })

        # --------------------------
        # Append round info
        # --------------------------
        result.append({
            "round_id": r.id,
            "release_time": r.release_time,
            "is_locked": r.is_locked,
            "category_name": category.category_name if category else "",
            "category_image": category.image_url if category else "",
            "question_text": question.question_text if question else "",
            "product1": {
                "id": product1.id if product1 else None,
                "name": product1.name if product1 else "",
                "image_url": product1.image_url if product1 else "",
                "votes": votes_product1
            },
            "product2": {
                "id": product2.id if product2 else None,
                "name": product2.name if product2 else "",
                "image_url": product2.image_url if product2 else "",
                "votes": votes_product2
            },
            "total_votes": votes_product1 + votes_product2,
            "max_votes": r.max_votes,
            "user_voted_product": user_voted_product,
            "user_win": user_win,
            "winning_side": winning_side,
            "participants": participants  # ✅ all participants with avatar and votedTo
        })

    return result
