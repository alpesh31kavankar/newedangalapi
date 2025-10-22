from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import pytz

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


# -----------------------------------------------------
# 🔹 Helper functions for token generation
# -----------------------------------------------------
def generate_token_id_next(token_type: str, last_seq: int) -> tuple[str, int]:
    """Generates next token id like W202510190001"""
    today_str = datetime.utcnow().strftime("%Y%m%d")
    next_seq = last_seq + 1
    return f"{token_type}{today_str}{next_seq:04d}", next_seq


def get_last_token_seq(db: Session, token_type: str) -> int:
    """Finds last token number for today"""
    today_str = datetime.utcnow().strftime("%Y%m%d")
    last_token = (
        db.query(models.Token)
        .filter(
            models.Token.token_type == token_type,
            models.Token.token_id.like(f"{token_type}{today_str}%")
        )
        .order_by(models.Token.token_id.desc())
        .first()
    )
    return int(last_token.token_id[-4:]) if last_token else 0


# -----------------------------------------------------
# ✅ GET: Current Month Leaderboard
# -----------------------------------------------------
@router.get("/", response_model=list[schemas.LeaderboardResponse])
def get_leaderboard(db: Session = Depends(get_db)):
    """Fetch current month leaderboard with user info"""
    month = datetime.now().strftime("%Y-%m")

    leaderboard = (
        db.query(models.Leaderboard)
        .filter(models.Leaderboard.month == month)
        .order_by(models.Leaderboard.score.desc())
        .all()
    )

    # Assign ranks manually
    for idx, record in enumerate(leaderboard, start=1):
        record.rank = idx  # not saved in DB, just for response
        _ = record.user  # load user relationship

    return leaderboard


# -----------------------------------------------------
# ✅ POST: Update score (on vote)
# -----------------------------------------------------
@router.post("/update", response_model=schemas.LeaderboardResponse)
def update_score(entry: schemas.LeaderboardCreate, db: Session = Depends(get_db)):
    """Update leaderboard score when user performs action"""
    month = entry.month
    user_id = entry.user_id

    record = (
        db.query(models.Leaderboard)
        .filter(models.Leaderboard.user_id == user_id, models.Leaderboard.month == month)
        .first()
    )

    if not record:
        record = models.Leaderboard(
            user_id=user_id,
            month=month,
            score=entry.score
        )
        db.add(record)
    else:
        record.score += entry.score

    db.commit()
    db.refresh(record)
    _ = record.user
    record.rank = None  # Not calculated here

    return record


# -----------------------------------------------------
# ✅ POST: Claim Monthly Reward (Generate 2 Tokens)
# -----------------------------------------------------
@router.post("/claim/{user_id}")
def claim_monthly_reward(user_id: int, db: Session = Depends(get_db)):
    """Claim monthly leaderboard reward (only on last day of the month)"""
    # Convert UTC → IST
    now_utc = datetime.now(timezone.utc)
    ist = pytz.timezone("Asia/Kolkata")
    now_local = now_utc.astimezone(ist)

    month = now_local.strftime("%Y-%m")

    # Check if it's last day of month
    next_month = now_local.replace(day=28) + timedelta(days=4)
    last_day = (next_month - timedelta(days=next_month.day)).day
    if now_local.day != last_day:
        raise HTTPException(status_code=403, detail="Reward can only be claimed on the last day of the month.")

    # Find leaderboard record
    record = (
        db.query(models.Leaderboard)
        .filter(models.Leaderboard.user_id == user_id, models.Leaderboard.month == month)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="User not found in leaderboard")

    if record.claimed:
        raise HTTPException(status_code=400, detail="Reward already claimed")

    # Generate 2 tokens of type 'W' for monthly_reward
    last_seq = get_last_token_seq(db, "W")
    token_codes = []
    for _ in range(2):
        token_id, last_seq = generate_token_id_next("W", last_seq)
        token = models.Token(
            token_id=token_id,
            users_id=user_id,
            token_type="W",
            source="monthly_reward"
        )
        db.add(token)
        token_codes.append(token_id)

    # Mark reward claimed
    record.claimed = True
    db.commit()

    return {
        "message": "Monthly reward claimed successfully 🎉",
        "tokens_generated": token_codes,
        "month": month
    }
