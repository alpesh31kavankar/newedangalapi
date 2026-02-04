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
from sqlalchemy import distinct
from datetime import date, timedelta, datetime,time
import pytz
IST = pytz.timezone("Asia/Kolkata")


router = APIRouter(prefix="/votes", tags=["votes"])

@router.get("/my", tags=["votes"])
def get_my_votes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id
    
    voted_rounds = db.query(Vote.question_rounds_id).filter(
        Vote.users_id == user_id
    ).all()

    # Convert SQL result → normal list
    return [v[0] for v in voted_rounds]

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
        # today_str = datetime.utcnow().strftime("%Y%m%d")
        today_str = datetime.now(IST).strftime("%Y%m%d")  # ✅ CHANGED
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
            # today_str = datetime.utcnow().strftime("%Y%m%d")
            today_str = datetime.now(IST).strftime("%Y%m%d")  # ✅ CHANGED
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


@router.get("/active-users", tags=["votes"])
def get_active_users(db: Session = Depends(get_db)):

    IST = pytz.timezone("Asia/Kolkata")

    # 1️⃣ IST dates
    today_ist = datetime.now(IST).date()
    yesterday_ist = today_ist - timedelta(days=1)

    # 2️⃣ IST → UTC ranges
    today_start_ist = IST.localize(datetime.combine(today_ist, time.min))
    today_end_ist = today_start_ist + timedelta(days=1)

    yesterday_start_ist = IST.localize(datetime.combine(yesterday_ist, time.min))
    yesterday_end_ist = yesterday_start_ist + timedelta(days=1)

    today_start_utc = today_start_ist.astimezone(pytz.UTC)
    today_end_utc = today_end_ist.astimezone(pytz.UTC)

    yesterday_start_utc = yesterday_start_ist.astimezone(pytz.UTC)
    yesterday_end_utc = yesterday_end_ist.astimezone(pytz.UTC)

    # 3️⃣ Queries
    today_count = db.query(
        func.count(distinct(Vote.users_id))
    ).filter(
        Vote.created_at >= today_start_utc,
        Vote.created_at < today_end_utc
    ).scalar()

    yesterday_count = db.query(
        func.count(distinct(Vote.users_id))
    ).filter(
        Vote.created_at >= yesterday_start_utc,
        Vote.created_at < yesterday_end_utc
    ).scalar()

    return {
        "today": today_count,
        "yesterday": yesterday_count
    }


@router.get("/stats/today", tags=["stats"])
def today_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    IST = pytz.timezone("Asia/Kolkata")

    # -----------------------------
    # 1️⃣ IST date
    # -----------------------------
    today_ist = datetime.now(IST).date()

    # -----------------------------
    # 2️⃣ IST → UTC range
    # -----------------------------
    today_start_ist = IST.localize(
        datetime.combine(today_ist, time.min)
    )
    today_end_ist = today_start_ist + timedelta(days=1)

    today_start_utc = today_start_ist.astimezone(pytz.UTC)
    today_end_utc = today_end_ist.astimezone(pytz.UTC)

    # -----------------------------
    # 3️⃣ Joined
    # -----------------------------
    joined = db.query(Vote).filter(
        Vote.users_id == current_user.id,
        Vote.created_at >= today_start_utc,
        Vote.created_at < today_end_utc
    ).count()

    # -----------------------------
    # 4️⃣ Results (won / lost / tie)
    # -----------------------------
    rounds = (
        db.query(
            QuestionRound.id,
            Vote.products_id,
            QuestionRound.winner_product_id,
            QuestionRound.is_draw
        )
        .join(Vote, Vote.question_rounds_id == QuestionRound.id)
        .filter(
            Vote.users_id == current_user.id,
            QuestionRound.is_locked == True,
            QuestionRound.updated_at >= today_start_utc,
            QuestionRound.updated_at < today_end_utc
        )
        .distinct(QuestionRound.id)
        .all()
    )

    won = lost = tie = 0

    for r in rounds:
        if r.is_draw:
            tie += 1
        elif r.products_id == r.winner_product_id:
            won += 1
        else:
            lost += 1

    results_out = won + lost + tie

    return {
        "joined": joined,
        "resultsOut": results_out,
        "won": won,
        "lost": lost,
        "tie": tie
    }

# @router.get("/active-users", tags=["votes"])
# def get_active_users(
#     db: Session = Depends(get_db)
# ):
#     today = date.today()
#     yesterday = today - timedelta(days=1)

#     today_count = db.query(
#         func.count(distinct(Vote.users_id))
#     ).filter(
#         Vote.created_at >= today,
#         Vote.created_at < today + timedelta(days=1)
#     ).scalar()

#     yesterday_count = db.query(
#         func.count(distinct(Vote.users_id))
#     ).filter(
#         Vote.created_at >= yesterday,
#         Vote.created_at < today
#     ).scalar()

#     return {
#         "today": today_count,
#         "yesterday": yesterday_count
#     }