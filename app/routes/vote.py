from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.vote import Vote
from ..models.question_round import QuestionRound
from ..models.token import Token
from ..schemas.vote import VoteCreate, VoteOut
from datetime import datetime

router = APIRouter(prefix="/votes", tags=["votes"])

# Simple sequence generators for token IDs (simulate BIGSERIAL)
participation_seq = 1
winning_seq = 1

def generate_participation_token():
    global participation_seq
    token = f"P{datetime.utcnow().strftime('%Y%m%d')}{str(participation_seq).zfill(6)}"
    participation_seq += 1
    return token

def generate_winning_token():
    global winning_seq
    token = f"W{datetime.utcnow().strftime('%Y%m%d')}{str(winning_seq).zfill(6)}"
    winning_seq += 1
    return token

# Cast vote
@router.post("/", response_model=VoteOut)
def cast_vote(vote_in: VoteCreate, db: Session = Depends(get_db)):
    # Check if user already voted for this round
    existing = db.query(Vote).filter(
        Vote.users_id == vote_in.users_id,
        Vote.question_rounds_id == vote_in.question_rounds_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already voted in this round")

    # Fetch round details
    round_obj = db.query(QuestionRound).filter(QuestionRound.id == vote_in.question_rounds_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    if round_obj.is_locked:
        raise HTTPException(status_code=400, detail="Round is locked")

    # Check product belongs to round
    if vote_in.products_id not in [round_obj.product1_id, round_obj.product2_id]:
        raise HTTPException(status_code=400, detail="Product not part of this round")

    # Create vote
    new_vote = Vote(**vote_in.dict())
    db.add(new_vote)

    # Update vote count
    if vote_in.products_id == round_obj.product1_id:
        round_obj.votes_product1 += 1
    else:
        round_obj.votes_product2 += 1

    # Issue participation token if not exists
    existing_token = db.query(Token).filter(
        Token.users_id == vote_in.users_id,
        Token.question_rounds_id == vote_in.question_rounds_id,
        Token.token_type == 'participation'
    ).first()
    if not existing_token:
        token = Token(
            tokens_id=generate_participation_token(),
            users_id=vote_in.users_id,
            question_rounds_id=vote_in.question_rounds_id,
            product_id=vote_in.products_id,
            token_type='participation',
            source='vote'
        )
        db.add(token)

    # Check if round reached max votes
    total_votes = round_obj.votes_product1 + round_obj.votes_product2
    if total_votes >= round_obj.max_votes:
        round_obj.is_locked = True
        if round_obj.votes_product1 > round_obj.votes_product2:
            round_obj.winner_product_id = round_obj.product1_id
        elif round_obj.votes_product2 > round_obj.votes_product1:
            round_obj.winner_product_id = round_obj.product2_id
        else:
            round_obj.is_draw = True

        # Issue winning tokens if not draw
        if not round_obj.is_draw and round_obj.winner_product_id:
            winning_votes = db.query(Vote).filter(
                Vote.question_rounds_id == round_obj.id,
                Vote.products_id == round_obj.winner_product_id
            ).all()
            for v in winning_votes:
                exists = db.query(Token).filter(
                    Token.users_id == v.users_id,
                    Token.question_rounds_id == round_obj.id,
                    Token.token_type == 'winning'
                ).first()
                if not exists:
                    token = Token(
                        tokens_id=generate_winning_token(),
                        users_id=v.users_id,
                        question_rounds_id=round_obj.id,
                        product_id=v.products_id,
                        token_type='winning',
                        source='round_win'
                    )
                    db.add(token)

    db.commit()
    db.refresh(new_vote)
    return new_vote
