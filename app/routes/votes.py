from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
from ..database import get_db
from ..models.vote import Vote
from ..models.question_round import QuestionRound
from ..models.token import Token
from ..schemas.vote import VoteCreate, VoteOut
from ..routes.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("/", response_model=VoteOut)
def cast_vote(
    vote_in: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    # Check duplicate vote
    existing = db.query(Vote).filter(
        Vote.users_id == user_id,
        Vote.question_rounds_id == vote_in.question_rounds_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already voted in this round")

    # Lock round row
    round_obj = (
        db.query(QuestionRound)
        .filter(QuestionRound.id == vote_in.question_rounds_id)
        .with_for_update()
        .first()
    )
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")

    # Current vote counts
    votes_p1 = db.query(func.count(Vote.id)).filter(
        Vote.question_rounds_id == round_obj.id,
        Vote.products_id == round_obj.product1_id
    ).scalar()
    votes_p2 = db.query(func.count(Vote.id)).filter(
        Vote.question_rounds_id == round_obj.id,
        Vote.products_id == round_obj.product2_id
    ).scalar()
    total_votes = votes_p1 + votes_p2

    if round_obj.is_locked or total_votes >= round_obj.max_votes:
        raise HTTPException(status_code=400, detail="Round is locked")

    # Validate product
    if vote_in.products_id not in [round_obj.product1_id, round_obj.product2_id]:
        raise HTTPException(status_code=400, detail="Product not part of this round")

    # Insert vote
    new_vote = Vote(
        users_id=user_id,
        question_rounds_id=vote_in.question_rounds_id,
        products_id=vote_in.products_id
    )
    db.add(new_vote)

    # --- Participation token ---
    existing_token = db.query(Token).filter(
        Token.users_id == user_id,
        Token.question_rounds_id == vote_in.question_rounds_id,
        Token.token_type == 'P'
    ).first()

    if not existing_token:
        # Generate next P token sequence for today
        today_str = datetime.utcnow().strftime("%Y%m%d")
        last_token = (
            db.query(Token)
            .filter(Token.token_type == 'P')
            .filter(Token.token_id.like(f"P{today_str}%"))
            .order_by(Token.token_id.desc())
            .first()
        )
        last_seq = int(last_token.token_id[-4:]) if last_token else 0
        last_seq += 1
        token_id = f"P{today_str}{last_seq:04d}"

        token = Token(
            token_id=token_id,
            users_id=user_id,
            question_rounds_id=vote_in.question_rounds_id,
            product_id=vote_in.products_id,
            token_type='P',
            source='vote'
        )
        db.add(token)

    db.flush()  # make vote visible for counts

    # Recalculate vote counts
    votes_p1 = db.query(func.count(Vote.id)).filter(
        Vote.question_rounds_id == round_obj.id,
        Vote.products_id == round_obj.product1_id
    ).scalar()
    votes_p2 = db.query(func.count(Vote.id)).filter(
        Vote.question_rounds_id == round_obj.id,
        Vote.products_id == round_obj.product2_id
    ).scalar()
    total_votes = votes_p1 + votes_p2

    # Lock round if max votes reached
    if total_votes >= round_obj.max_votes:
        round_obj.is_locked = True
        if votes_p1 > votes_p2:
            round_obj.winner_product_id = round_obj.product1_id
        elif votes_p2 > votes_p1:
            round_obj.winner_product_id = round_obj.product2_id
        else:
            round_obj.is_draw = True

        # --- Winning tokens ---
        if not round_obj.is_draw and round_obj.winner_product_id:
            winning_votes = db.query(Vote).filter(
                Vote.question_rounds_id == round_obj.id,
                Vote.products_id == round_obj.winner_product_id
            ).all()

            # Get last W token seq for today
            today_str = datetime.utcnow().strftime("%Y%m%d")
            last_token = (
                db.query(Token)
                .filter(Token.token_type == 'W')
                .filter(Token.token_id.like(f"W{today_str}%"))
                .order_by(Token.token_id.desc())
                .first()
            )
            last_seq = int(last_token.token_id[-4:]) if last_token else 0

            for v in winning_votes:
                exists = db.query(Token).filter(
                    Token.users_id == v.users_id,
                    Token.question_rounds_id == round_obj.id,
                    Token.token_type == 'W'
                ).first()
                if not exists:
                    last_seq += 1
                    token_id = f"W{today_str}{last_seq:04d}"
                    token = Token(
                        token_id=token_id,
                        users_id=v.users_id,
                        question_rounds_id=round_obj.id,
                        product_id=v.products_id,
                        token_type='W',
                        source='round_win'
                    )
                    db.add(token)

    db.commit()
    db.refresh(new_vote)
    return new_vote
