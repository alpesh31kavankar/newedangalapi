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

router = APIRouter(prefix="/daily-rewards", tags=["Daily Rewards"])

# ---------------------------
# Token generation functions
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
    if 20 <= now_local.hour < 24:
        raise HTTPException(status_code=403, detail="Cannot claim between 8 PM - 12 AM")

    # ✅ Check if user already collected today
    already_collected = (
        db.query(DailyTicketClaim)
        .filter(DailyTicketClaim.user_id == current_user.id)
        .filter(func.date(DailyTicketClaim.collected_at) == today_date)
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

    # Get last W token sequence
    last_seq = get_last_token_seq(db, "W")

    # Generate tokens
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

    # Record claim
    claim = DailyTicketClaim(
        user_id=current_user.id,
        reward_id=reward.id,
        collected_date=today_date,  # make sure model has this column
    )
    db.add(claim)
    db.commit()

    return {
        "day_number": day_number,
        "tickets_earned": reward.tickets,
        "token_codes": token_codes,
        "collected_at": claim.collected_at.isoformat(),
    }

# ---------------------------
# GET: Fetch user's daily claim history
# ---------------------------
@router.get("/history")
def get_daily_claims(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Convert to IST
    now_utc = datetime.now(timezone.utc)
    ist = pytz.timezone("Asia/Kolkata")
    today_date = now_utc.astimezone(ist).date()

    # Get all rewards
    rewards = db.query(TicketReward).order_by(TicketReward.day_number).all()

    # Get user's claimed days
    claims = db.query(DailyTicketClaim).filter_by(user_id=current_user.id).all()
    claimed_map = {c.reward_id: c for c in claims}

    # Count how many days user has already collected
    claimed_count = len(claims)
    next_day_number = claimed_count + 1

    result = []
    for reward in rewards:
        claim = claimed_map.get(reward.id)
        collected = bool(claim)

        # 🔓 Unlock rule
        # - Already collected → unlocked (collected = True)
        # - Next uncollected day = unlocked (today's available)
        # - Others → locked
        unlocked = (
            collected or
            (reward.day_number == next_day_number)
        )

        result.append({
            "day": reward.day_number,
            "tickets": reward.tickets,
            "collected": collected,
            "collected_at": claim.collected_at.isoformat() if claim else None,
            "locked": not unlocked
        })

    return result


