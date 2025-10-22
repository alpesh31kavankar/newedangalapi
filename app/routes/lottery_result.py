# app/routers/lottery_result.py
from datetime import datetime, time, timedelta
from fastapi import APIRouter
from sqlalchemy import text
from ..database import SessionLocal

router = APIRouter(prefix="/lottery", tags=["Lottery Results"])

@router.get("/current-winners")
def get_current_lottery_winners():
    db = SessionLocal()
    now = datetime.now()
    today = now.date()
    draw_time = time(20, 30)  # 8:30 PM

    # 🕒 If time is before 8:30 PM, show yesterday’s winner
    if now.time() < draw_time:
        show_date = today - timedelta(days=1)
    else:
        show_date = today

    # 🟢 Participant winner (by created_at::date)
    participant = db.execute(text("""
        SELECT w.*, u.username, u.profile_image
        FROM participant_lottery_winner w
        JOIN users u ON u.id = w.users_id
        WHERE w.created_at::date = :show_date
        ORDER BY w.id DESC
        LIMIT 1
    """), {"show_date": show_date}).mappings().first()

    # 🟢 Winning token winner (by created_at::date)
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
