# from datetime import datetime
# from sqlalchemy import func
# from app.database import get_db
# from app.models import Leaderboard, Token
# from apscheduler.schedulers.background import BackgroundScheduler

# def update_monthly_leaderboard():
#     db = next(get_db())
#     month = datetime.now().strftime("%Y-%m")

#     # 1️⃣ Calculate scores from votes
#     scores = (
#         db.query(Token.users_id, func.count(Token.token_id).label("votes"))
#         .filter(Token.source == "vote")
#         .filter(func.to_char(Token.created_at, "YYYY-MM") == month)
#         .group_by(Token.users_id)
#         .all()
#     )

#     # 2️⃣ Update leaderboard table
#     for user_id, votes in scores:
#         score = votes * 5
#         record = db.query(Leaderboard).filter_by(user_id=user_id, month=month).first()
#         if not record:
#             record = Leaderboard(user_id=user_id, month=month, score=score)
#             db.add(record)
#         else:
#             record.score = score

#     # 3️⃣ Update ranks
#     all_records = db.query(Leaderboard).filter_by(month=month).order_by(Leaderboard.score.desc()).all()
#     for i, rec in enumerate(all_records):
#         rec.rank = i + 1

#     db.commit()
#     print(f"[CRON] ✅ Leaderboard updated for {month} at {datetime.now()}")



# from datetime import datetime, timedelta, time
# import pytz
# from sqlalchemy import func, text
# from app.database import get_db
# from app.models import Leaderboard, Token
# from apscheduler.schedulers.background import BackgroundScheduler

# IST = pytz.timezone("Asia/Kolkata")
# FREEZE_TIME = time(10, 0)  # 10:00 AM IST
# LOCK_ID = 778899

# def update_monthly_leaderboard():
#     db = next(get_db())
#     locked = False
#     try:
#         # 🔒 Prevent multiple workers
#         locked = db.execute(
#             text("SELECT pg_try_advisory_lock(:id)"),
#             {"id": LOCK_ID}
#         ).scalar()

#         if not locked:
#             print("[CRON] ⏭️ Skipped (another worker running)")
#             return

#         now = datetime.now(IST)
#         today = now.date()
#         month = now.strftime("%Y-%m")

#         # ✅ correct last day of month
#         next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
#         last_day = next_month - timedelta(days=1)

#         # 🧊 FREEZE LOGIC
#         if today == last_day and now.time() >= FREEZE_TIME:
#             print("[CRON] 🧊 Leaderboard frozen (IST)")
#             return

#         # 1️⃣ Calculate votes
#         scores = (
#             db.query(Token.users_id, func.count(Token.token_id).label("votes"))
#             .filter(Token.source == "vote")
#             .filter(func.to_char(Token.created_at, "YYYY-MM") == month)
#             .group_by(Token.users_id)
#             .all()
#         )

#         # 2️⃣ Update scores
#         for user_id, votes in scores:
#             score = votes * 5
#             record = (
#                 db.query(Leaderboard)
#                 .filter_by(user_id=user_id, month=month)
#                 .first()
#             )
#             if not record:
#                 db.add(Leaderboard(user_id=user_id, month=month, score=score))
#             else:
#                 record.score = score

#         # 3️⃣ Stable ranking
#         records = (
#             db.query(Leaderboard)
#             .filter_by(month=month)
#             .order_by(
#                 Leaderboard.score.desc(),
#                 Leaderboard.updated_at.asc(),
#                 Leaderboard.user_id.asc()
#             )
#             .all()
#         )

#         for i, rec in enumerate(records, start=1):
#             rec.rank = i

#         db.commit()
#         print(f"[CRON] ✅ Leaderboard updated @ {now.strftime('%H:%M:%S IST')}")

#     finally:
#         if locked:
#             db.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": LOCK_ID})
#             db.commit()
#         db.close()


# def start_leaderboard_scheduler():
#     scheduler = BackgroundScheduler(timezone=IST)
#     scheduler.add_job(update_monthly_leaderboard, "interval", seconds=3)
#     scheduler.start()
#     print("[CRON] 🕒 Leaderboard updater started (every 3 sec)")


from datetime import datetime, timedelta, time
import pytz

from sqlalchemy import func, text
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal   # ✅ CHANGED (no get_db)
from app.models import Leaderboard, Token


IST = pytz.timezone("Asia/Kolkata")
FREEZE_TIME = time(10, 0)  # 10:00 AM IST
LOCK_ID = 778899


def update_monthly_leaderboard():
    db = SessionLocal()   # ✅ CORRECT WAY FOR CRON
    locked = False

    try:
        # 🔒 Prevent multiple workers (DB-level lock)
        locked = db.execute(
            text("SELECT pg_try_advisory_lock(:id)"),
            {"id": LOCK_ID}
        ).scalar()

        if not locked:
            print("[CRON] ⏭️ Skipped (another worker running)")
            return

        now = datetime.now(IST)
        today = now.date()
        month = now.strftime("%Y-%m")

        # ✅ Month start & end (index-friendly)
        month_start = datetime(now.year, now.month, 1, tzinfo=IST)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        # ✅ Correct last day of month
        last_day = (month_end - timedelta(days=1)).date()

        # 🧊 FREEZE LOGIC
        if today == last_day and now.time() >= FREEZE_TIME:
            print("[CRON] 🧊 Leaderboard frozen (IST)")
            return

        # 1️⃣ Calculate votes (FAST + INDEX SAFE)
        scores = (
            db.query(Token.users_id, func.count(Token.token_id).label("votes"))
            .filter(Token.source == "vote")
            .filter(Token.created_at >= month_start)
            .filter(Token.created_at < month_end)
            .group_by(Token.users_id)
            .all()
        )

        # 2️⃣ Update scores
        for user_id, votes in scores:
            score = votes * 5
            record = (
                db.query(Leaderboard)
                .filter_by(user_id=user_id, month=month)
                .first()
            )

            if not record:
                db.add(
                    Leaderboard(
                        user_id=user_id,
                        month=month,
                        score=score
                    )
                )
            else:
                record.score = score

        # 3️⃣ Stable ranking
        records = (
            db.query(Leaderboard)
            .filter_by(month=month)
            .order_by(
                Leaderboard.score.desc(),
                Leaderboard.updated_at.asc(),
                Leaderboard.user_id.asc()
            )
            .all()
        )

        for i, rec in enumerate(records, start=1):
            rec.rank = i

        db.commit()
        print(f"[CRON] ✅ Leaderboard updated @ {now.strftime('%H:%M:%S IST')}")

    except Exception as e:
        db.rollback()
        print("[CRON] ❌ Error:", e)

    finally:
        if locked:
            db.execute(
                text("SELECT pg_advisory_unlock(:id)"),
                {"id": LOCK_ID}
            )
            db.commit()

        db.close()   # 🔥 ALWAYS CLOSE


def start_leaderboard_scheduler():
    scheduler = BackgroundScheduler(timezone=IST)

    scheduler.add_job(
        update_monthly_leaderboard,
        "interval",
        seconds=10,        # ✅ safer than 3 sec
        max_instances=1,   # 🔥 PREVENT OVERLAP
        coalesce=True,
        misfire_grace_time=5,
    )

    scheduler.start()
    print("[CRON] 🕒 Leaderboard updater started (every 10 sec)")
