from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import pytz
from app.database import get_db
from app.models.user import User
from app.models.token import Token
from ..routes.auth import get_current_user  # Your auth dependency

router = APIRouter(prefix="/spin", tags=["Spin & Win"])

# ---------------------------
# Pydantic Model for Request
# ---------------------------
class SpinRequest(BaseModel):
    prize_type: str
    prize_value: int = 0


# ---------------------------
# Token generation helpers
# ---------------------------
def generate_token_id_next(token_type: str, last_seq: int) -> tuple[str, int]:
    today_str = datetime.utcnow().strftime("%Y%m%d")
    next_seq = last_seq + 1
    return f"{token_type}{today_str}{next_seq:04d}", next_seq


def get_last_token_seq(db: Session, token_type: str) -> int:
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
@router.post("/play")
def spin_wheel(
    data: SpinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    prize_type: 'ticket', 'extra', or 'lose'
    prize_value: number of tickets (if prize_type='ticket')
    """

    prize_type = data.prize_type
    prize_value = data.prize_value

    # Convert to IST
    now_utc = datetime.now(timezone.utc)
    ist = pytz.timezone("Asia/Kolkata")
    now_local = now_utc.astimezone(ist)
    today_date = now_local.date()

    # ✅ Check if user already spun today (ignore extra spin here)
    last_spin = (
        db.query(Token)
        .filter(Token.users_id == current_user.id, Token.source == 'spin')
        .order_by(Token.created_at.desc())
        .first()
    )
    if last_spin:
        last_spin_date = last_spin.created_at.astimezone(ist).date()
        if last_spin_date == today_date:
            raise HTTPException(status_code=400, detail="Already spun today")

    token_ids = []

    if prize_type == 'ticket' and prize_value > 0:
        # Generate tickets
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
            "token_ids": token_ids
        }

    elif prize_type == 'extra':
        # Extra spin → just return success
        return {
            "status": "extra_spin",
            "message": "You got an extra spin! Spin again."
        }

    else:
        # Lost case
        return {
            "status": "lose",
            "message": "Better luck next time!"
        }


# ---------------------------
# GET: User's spin history
# ---------------------------
@router.get("/history")
def spin_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    spins = (
        db.query(Token)
        .filter(Token.users_id == current_user.id, Token.source == 'spin')
        .order_by(Token.created_at.desc())
        .all()
    )
    result = []
    for t in spins:
        result.append({
            "token_id": t.token_id,
            "type": t.token_type,
            "created_at": t.created_at.isoformat()
        })
    return result
