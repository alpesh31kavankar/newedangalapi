from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Date
from datetime import date
from ..database import get_db
from ..models.question_round import QuestionRound
from ..models.vote import Vote
from ..models.token import Token
from ..models.user import User
from ..models.product import Product
from ..models.category import Category
from ..models.question import Question
from ..schemas.round_result import LockedRoundOut
from ..routes.auth import get_current_user

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
