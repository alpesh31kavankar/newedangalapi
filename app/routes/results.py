from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Date
from app import models   
from datetime import date
from ..database import get_db
from ..models.question_round import QuestionRound
from ..models.vote import Vote
from ..models.token import Token
from ..models.user import User
from ..models.product import Product
from ..models.category import Category
from ..models.question import Question
from ..schemas.round_result import LockedRoundOut,LockedRoundAllOut,ParticipantResult
from ..routes.auth import get_current_user
from typing import List

router = APIRouter(prefix="/results", tags=["results"])

@router.get("/today-locked", response_model=list[LockedRoundOut])
def get_todays_locked_rounds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()

    # Fetch all today's locked rounds
    rounds = db.query(QuestionRound).filter(
        QuestionRound.is_locked == True,
        QuestionRound.release_time.cast(Date) == today
    ).all()

    results = []
    for r in rounds:
        # Participant count
        participant_count = db.query(Vote).filter(Vote.question_rounds_id == r.id).count()

        # Products info
        product1 = db.query(Product).filter(Product.id == r.product1_id).first()
        product2 = db.query(Product).filter(Product.id == r.product2_id).first()
        category = db.query(Category).filter(Category.id == r.categories_id).first()
        question = db.query(Question).filter(Question.id == r.questions_id).first()

        # Check if current user voted
        user_token = db.query(Token).filter(
            Token.question_rounds_id == r.id,
            Token.users_id == current_user.id,
            Token.token_type == 'P'
        ).first()

        # Did user win?
        is_winner = False
        token_claimed = False
        winning_token_id = None 
        if r.winner_product_id:
            winning_token = db.query(Token).filter(
                Token.question_rounds_id == r.id,
                Token.users_id == current_user.id,
                Token.token_type == 'W'
            ).first()
            if winning_token:
                is_winner = True
                winning_token_id = winning_token.token_id
                token_claimed = winning_token.source == 'claim'

 # ✅ Add revealed here
        revealed = token_claimed or (user_token and not is_winner)

        results.append(
            LockedRoundOut(
                question_round_id=r.id,
                category_image=category.image_url if category else "",
                question_text=question.question_text if question else "",
                product1_name=product1.name if product1 else "",
                product1_image=product1.image_url if product1 else "",
                product2_name=product2.name if product2 else "",
                product2_image=product2.image_url if product2 else "",
                participant_count=participant_count,
                max_votes=r.max_votes,
                is_locked=r.is_locked,
                user_token_id=user_token.token_id if user_token else None,
                is_winner=is_winner,
                winning_token_id=winning_token_id,
                token_claimed=token_claimed,
                revealed=revealed 
            )
        )

    return results


@router.get("/today-locked-all")
def get_todays_locked_rounds_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    rounds = (
        db.query(QuestionRound)
        .filter(QuestionRound.is_locked == True)
        .filter(QuestionRound.created_at.cast(Date) == today)
        .all()
    )

    if not rounds:
        raise HTTPException(status_code=404, detail="No locked rounds found today")

    results = []

    for r in rounds:
        category = db.query(Category).filter(Category.id == r.categories_id).first()
        product1 = db.query(Product).filter(Product.id == r.product1_id).first()
        product2 = db.query(Product).filter(Product.id == r.product2_id).first()
        question = db.query(Question).filter(Question.id == r.questions_id).first()

        product1_votes = r.votes_product1 or 0
        product2_votes = r.votes_product2 or 0
        total_votes = product1_votes + product2_votes

        # Winner logic
        if r.is_draw:
            winner_name = "Draw"
        elif r.winner_product_id == r.product1_id:
            winner_name = product1.name if product1 else ""
        elif r.winner_product_id == r.product2_id:
            winner_name = product2.name if product2 else ""
        else:
            winner_name = ""

        results.append({
            "id": r.id,
            "question": question.question_text if question else "",
            "category": category.image_url if category else "",
            "products": [
                {
                    "id": "p1",
                    "name": product1.name if product1 else "",
                    "image": product1.image_url if product1 else "",
                    "category": category.image_url if category else "",
                    "votes": product1_votes
                },
                {
                    "id": "p2",
                    "name": product2.name if product2 else "",
                    "image": product2.image_url if product2 else "",
                    "category": category.image_url if category else "",
                    "votes": product2_votes
                }
            ],
            "joined": total_votes,
            "maxParticipants": r.max_votes,
            # 👇 Hide initially
            "revealed": False,
            "winnerName": winner_name,
            "totalVotes": total_votes
        })

    return results


@router.get("/round-detail/{round_id}")
def get_round_detail(round_id: int, db: Session = Depends(get_db)):
    # 🔹 Fetch round
    round_data = db.query(QuestionRound).filter(QuestionRound.id == round_id).first()
    if not round_data:
        raise HTTPException(status_code=404, detail="Round not found")

    # 🔹 Fetch related data (products, question, category)
    product1 = db.query(Product).filter(Product.id == round_data.product1_id).first()
    product2 = db.query(Product).filter(Product.id == round_data.product2_id).first()
    question = db.query(Question).filter(Question.id == round_data.questions_id).first()
    category = db.query(Category).filter(Category.id == round_data.categories_id).first()

    # 🔹 Fetch all votes for this round
    votes = db.query(Vote).filter(Vote.question_rounds_id == round_id).all()

    # 🔹 Count votes based on products_id
    product1_votes = sum(1 for v in votes if v.products_id == round_data.product1_id)
    product2_votes = sum(1 for v in votes if v.products_id == round_data.product2_id)
    total_votes = product1_votes + product2_votes

    # 🔹 Determine winner
    winner_product_id = None
    if product1_votes > product2_votes:
        winner_product_id = round_data.product1_id
    elif product2_votes > product1_votes:
        winner_product_id = round_data.product2_id

    # 🔹 Prepare participants list
    participants = []
    for v in votes:
        user = db.query(User).filter(User.id == v.users_id).first()
        voted_product_name = product1.name if v.products_id == round_data.product1_id else product2.name
        status = "Win" if winner_product_id == v.products_id else "Lost"
        participants.append({
            "user_name": user.username if user else "Unknown",
            "voted_to": voted_product_name,
            "status": status
        })

    # 🔹 Build and return response
    return {
        "question_round_id": round_data.id,
        "category_image": category.image_url if category else None,
        "question_text": question.question_text if question else None,
        "product1_name": product1.name if product1 else None,
        "product1_image": product1.image_url if product1 else None,
        "product2_name": product2.name if product2 else None,
        "product2_image": product2.image_url if product2 else None,
        "product1_votes": product1_votes,
        "product2_votes": product2_votes,
        "total_votes": total_votes,
        "winner_product": (
            product1.name if winner_product_id == round_data.product1_id
            else product2.name if winner_product_id == round_data.product2_id
            else None
        ),
        "participant_count": len(participants),
        "participants": participants,
        "is_locked": round_data.is_locked,
        "revealed": True
    }