from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import pytz
import random
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.token import Token
from app.models.spin_history import SpinHistory
from app.schemas.spin_schema import SpinRequest, SpinHistoryOut  # ✅ imported schema
from ..routes.auth import get_current_user  # auth dependency

router = APIRouter(prefix="/spin", tags=["Spin & Win"])


# ---------------------------
# Token generation helpers
# ---------------------------
def generate_token_id_next(token_type: str, last_seq: int) -> tuple[str, int]:
    """Generate the next sequential token ID for today's date."""
    today_str = datetime.utcnow().strftime("%Y%m%d")
    next_seq = last_seq + 1
    return f"{token_type}{today_str}{next_seq:04d}", next_seq


def get_last_token_seq(db: Session, token_type: str) -> int:
    """Get the last sequence number for today for a given token type."""
    last_token = (
        db.query(Token)
        .filter(
            Token.token_type == token_type,
            Token.token_id.like(f"{token_type}{datetime.utcnow().strftime('%Y%m%d')}%")
        )
        .order_by(Token.token_id.desc())
        .first()
    )
    return int(last_token.token_id[-4:]) if last_token else 0


# ---------------------------
# POST: Spin endpoint
# ---------------------------
@router.post("/play", response_model=dict)
def spin_wheel(
    data: SpinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Spin the wheel for the current user."""
    prize_type = data.prize_type
    prize_value = data.prize_value

    # Convert to IST (for date comparison)
    ist = pytz.timezone("Asia/Kolkata")
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(ist)
    today_date = now_local.date()

    # ✅ Get the last spin for this user
    last_spin = (
        db.query(SpinHistory)
        .filter(SpinHistory.user_id == current_user.id)
        .order_by(SpinHistory.created_at.desc())
        .first()
    )

    # ✅ Allow spin if:
    # - user hasn't spun today, OR
    # - last spin today was "extra"
    if last_spin:
        last_spin_date = last_spin.created_at.astimezone(ist).date()
        if last_spin_date == today_date and last_spin.prize_type != "extra":
            raise HTTPException(status_code=400, detail="You have already spun today.")

    # 🎲 If prize_type == 'auto', decide randomly
    if prize_type == "auto":
        choices = [
            ("ticket", 1),
            ("ticket", 2),
            ("ticket", 3),
            ("extra", 0),
            ("lose", 0),
            ("lose", 0),
        ]
        prize_type, prize_value = random.choice(choices)

    token_ids = []

    # ✅ Always record the spin
    spin_record = SpinHistory(
        user_id=current_user.id,
        prize_type=prize_type,
        prize_value=prize_value,
    )
    db.add(spin_record)

    try:
        if prize_type == "ticket" and prize_value > 0:
            last_seq = get_last_token_seq(db, "W")
            for _ in range(prize_value):
                token_id, last_seq = generate_token_id_next("W", last_seq)
                token = Token(
                    token_id=token_id,
                    users_id=current_user.id,
                    token_type="W",
                    source="spin",
                )
                db.add(token)
                token_ids.append(token_id)

            db.commit()
            return {
                "status": "win",
                "tickets": prize_value,
                "token_ids": token_ids,
            }

        elif prize_type == "extra":
            db.commit()
            return {
                "status": "extra_spin",
                "message": "🎉 You got an extra spin! Spin again.",
            }

        else:
            db.commit()
            return {
                "status": "lose",
                "message": "Better luck next time!",
            }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Spin failed: {str(e)}")


# ---------------------------
# GET: User's spin history
# ---------------------------
@router.get("/history", response_model=List[SpinHistoryOut])
def spin_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return user's complete spin history (most recent first)."""
    spins = (
        db.query(SpinHistory)
        .filter(SpinHistory.user_id == current_user.id)
        .order_by(SpinHistory.created_at.desc())
        .all()
    )
    return spins
