from datetime import datetime
from sqlalchemy import func
from app.database import get_db
from app.models import Leaderboard, Token
from apscheduler.schedulers.background import BackgroundScheduler

def update_monthly_leaderboard():
    db = next(get_db())
    month = datetime.now().strftime("%Y-%m")

    # 1️⃣ Calculate scores from votes
    scores = (
        db.query(Token.users_id, func.count(Token.token_id).label("votes"))
        .filter(Token.source == "vote")
        .filter(func.to_char(Token.created_at, "YYYY-MM") == month)
        .group_by(Token.users_id)
        .all()
    )

    # 2️⃣ Update leaderboard table
    for user_id, votes in scores:
        score = votes * 5
        record = db.query(Leaderboard).filter_by(user_id=user_id, month=month).first()
        if not record:
            record = Leaderboard(user_id=user_id, month=month, score=score)
            db.add(record)
        else:
            record.score = score

    # 3️⃣ Update ranks
    all_records = db.query(Leaderboard).filter_by(month=month).order_by(Leaderboard.score.desc()).all()
    for i, rec in enumerate(all_records):
        rec.rank = i + 1

    db.commit()
    print(f"[CRON] ✅ Leaderboard updated for {month} at {datetime.now()}")

def start_leaderboard_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_monthly_leaderboard, "interval", minutes=1)
    scheduler.start()
    print("[CRON] 🕒 Leaderboard updater started (every 1 min)")
