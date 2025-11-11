from datetime import datetime, time, timedelta
from fastapi import APIRouter
from sqlalchemy import text
from ..database import SessionLocal
import pytz  # ✅ To ensure we use Indian Standard Time (IST)

router = APIRouter(prefix="/lottery", tags=["Lottery Results"])

@router.get("/current-winners")
def get_current_lottery_winners():
    db = SessionLocal()

    # ✅ Always use IST timezone to avoid server UTC mismatch
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    today = now.date()

    show_time = time(12, 0)  # ✅ Show result after 8:00 PM next day

    # 🕒 Before 8:00 PM → show yesterday’s result
    if now.time() < show_time:
        show_date = today - timedelta(days=1)
    else:
        show_date = today

    # 🟢 Participant winner (based on created_at::date)
    participant = db.execute(text("""
        SELECT w.*, u.username, u.profile_image
        FROM participant_lottery_winner w
        JOIN users u ON u.id = w.users_id
        WHERE w.created_at::date = :show_date
        ORDER BY w.id DESC
        LIMIT 1
    """), {"show_date": show_date}).mappings().first()

    # 🟢 Winning token winner (based on created_at::date)
    winning = db.execute(text("""
        SELECT w.*, u.username, u.profile_image
        FROM lottery_winner w
        JOIN users u ON u.id = w.users_id
        WHERE w.created_at::date = :show_date
        ORDER BY w.id DESC
        LIMIT 1
    """), {"show_date": show_date}).mappings().first()

    db.close()

    return {
        "date_shown": show_date,
        "participant": participant,
        "winning": winning,
    }
