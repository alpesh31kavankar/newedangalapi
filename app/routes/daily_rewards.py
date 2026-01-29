from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import pytz
from sqlalchemy import func      
from app.database import get_db
from app.models.user import User
from app.models.ticket_reward import TicketReward
from app.models.daily_ticket_claim import DailyTicketClaim
from app.models.token import Token
from ..routes.auth import get_current_user  # Your auth dependency
IST = pytz.timezone("Asia/Kolkata")  # ✅ ADD

router = APIRouter(prefix="/daily-rewards", tags=["Daily Rewards"])

# ---------------------------
# Token generation functions
# ---------------------------
# def generate_token_id_next(token_type: str, last_seq: int) -> tuple[str, int]:
#     today_str = datetime.utcnow().strftime("%Y%m%d")
#     next_seq = last_seq + 1
#     return f"{token_type}{today_str}{next_seq:04d}", next_seq

def generate_token_id_next(token_type: str, last_seq: int) -> tuple[str, int]:
    today_str = datetime.now(IST).strftime("%Y%m%d")  # ✅ CHANGED
    next_seq = last_seq + 1
    return f"{token_type}{today_str}{next_seq:04d}", next_seq


def get_last_token_seq(db: Session, token_type: str) -> int:
    last_token = (
        db.query(Token)
        .filter(
            Token.token_type == token_type,
            # Token.token_id.like(f"{token_type}{datetime.utcnow().strftime('%Y%m%d')}%")
            Token.token_id.like(
                f"{token_type}{datetime.now(IST).strftime('%Y%m%d')}%"
            )
        )
        .order_by(Token.token_id.desc())
        .first()
    )
    return int(last_token.token_id[-4:]) if last_token else 0


# ---------------------------
# POST: Claim Daily Reward
# ---------------------------
@router.post("/claim-daily-reward")
def claim_daily_reward(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Convert to IST
    now_utc = datetime.now(timezone.utc)
    ist = pytz.timezone("Asia/Kolkata")
    now_local = now_utc.astimezone(ist)
    today_date = now_local.date()

    # Block 8 PM - 12 AM
    if 22 <= now_local.hour < 24:
        raise HTTPException(status_code=403, detail="Cannot claim between 10 PM - 12 AM")

    # Check if user already collected today
    already_collected = (
        db.query(DailyTicketClaim)
        .filter(DailyTicketClaim.user_id == current_user.id)
        .filter(DailyTicketClaim.collected_date == today_date)
        .first()
    )

    if already_collected:
        raise HTTPException(status_code=400, detail="Already collected today's reward")

    # Determine next day number
    claimed_count = db.query(DailyTicketClaim).filter_by(user_id=current_user.id).count()
    day_number = claimed_count + 1

    if day_number > 50:
        raise HTTPException(status_code=400, detail="Daily reward program completed")

    # Fetch today’s reward
    reward = db.query(TicketReward).filter_by(day_number=day_number, active=True).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    # Generate tokens
    last_seq = get_last_token_seq(db, "W")
    token_codes = []

    for _ in range(reward.tickets):
        token_id, last_seq = generate_token_id_next("W", last_seq)
        token = Token(
            token_id=token_id,
            users_id=current_user.id,
            token_type="W",
            source="daily_lucky_draw",
        )
        db.add(token)
        token_codes.append(token_id)

    # Save daily claim (UTC in DB)
    claim = DailyTicketClaim(
        user_id=current_user.id,
        reward_id=reward.id,
        collected_date=today_date
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)

    # Convert collected_at to IST for return
    collected_at_ist = claim.collected_at.astimezone(ist).isoformat()

    return {
        "day_number": day_number,
        "tickets_earned": reward.tickets,
        "token_codes": token_codes,
        "collected_at": collected_at_ist,
    }


# ---------------------------
# GET: Fetch Daily Claim History
# ---------------------------
@router.get("/history")
def get_daily_claims(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    ist = pytz.timezone("Asia/Kolkata")
    today_date = datetime.now(timezone.utc).astimezone(ist).date()

    # Fetch all rewards
    rewards = db.query(TicketReward).order_by(TicketReward.day_number).all()

    # Fetch user claims
    claims = (
        db.query(DailyTicketClaim)
        .filter_by(user_id=current_user.id)
        .order_by(DailyTicketClaim.collected_at)
        .all()
    )

    claimed_map = {c.reward_id: c for c in claims}

    # Last collected date (UTC → IST)
    last_claim = claims[-1] if claims else None
    last_collected_date = (
        last_claim.collected_at.astimezone(ist).date()
        if last_claim else None
    )

    # Did user collect today?
    collected_today = (last_collected_date == today_date)

    claimed_count = len(claims)
    next_day_number = claimed_count + 1

    result = []

    for reward in rewards:
        claim = claimed_map.get(reward.id)
        collected = bool(claim)

        # Unlock rules
        if collected:
            unlocked = True

        elif reward.day_number == next_day_number:
            unlocked = not collected_today

        else:
            unlocked = False

        result.append({
            "day": reward.day_number,
            "tickets": reward.tickets,
            "collected": collected,
            "collected_at": (
                claim.collected_at.astimezone(ist).isoformat()
                if claim else None
            ),
            "locked": not unlocked
        })

    return result
