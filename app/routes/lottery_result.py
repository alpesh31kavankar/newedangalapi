from datetime import datetime, time, timedelta
from fastapi import APIRouter
from sqlalchemy import text
from ..database import SessionLocal
import pytz  # ✅ To ensure we use Indian Standard Time (IST)
from collections import defaultdict


router = APIRouter(prefix="/lottery", tags=["Lottery Results"])

@router.get("/current-winners")
def get_current_lottery_winners():
    db = SessionLocal()

    # ✅ Always use IST timezone to avoid server UTC mismatch
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    today = now.date()

    show_time = time(22, 0)  # ✅ Show result after 8:00 PM next day

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


# @router.get("/history")
# def lottery_history():
#     db = SessionLocal()

#     rows = db.execute(text("""
#         -- PARTICIPANTS
#         SELECT
#             p.created_at::date AS draw_date,
#             p.token_id,
#             u.username,
#             u.profile_image,
#             'participant' AS type
#         FROM participant_lottery_winner p
#         JOIN users u ON u.id = p.users_id

#         UNION ALL

#         -- WINNERS
#         SELECT
#             w.created_at::date AS draw_date,
#             w.token_id,
#             u.username,
#             u.profile_image,
#             'winner' AS type
#         FROM lottery_winner w
#         JOIN users u ON u.id = w.users_id

#         ORDER BY draw_date DESC
#     """)).mappings().all()

#     db.close()

#     result = defaultdict(list)

#     for r in rows:
#         date_key = str(r["draw_date"])

#         result[date_key].append({
#             "type": r["type"],          # "participant" | "winner"
#             "username": r["username"],
#             "profile_image": r["profile_image"],
#             "token": r["token_id"]
#         })

#     return dict(result)


@router.get("/history")
def lottery_history():
    db = SessionLocal()

    participant_rows = db.execute(text("""
        SELECT
            w.created_at::date AS win_date,
            w.token_id,
            u.username,
            u.profile_image
        FROM participant_lottery_winner w
        JOIN users u ON u.id = w.users_id
        ORDER BY w.created_at DESC
    """)).mappings().all()

    winning_rows = db.execute(text("""
        SELECT
            w.created_at::date AS win_date,
            w.token_id,
            u.username,
            u.profile_image
        FROM lottery_winner w
        JOIN users u ON u.id = w.users_id
        ORDER BY w.created_at DESC
    """)).mappings().all()

    db.close()

    grouped = defaultdict(list)

    for r in participant_rows:
        grouped[str(r["win_date"])].append({
            "type": "participant",
            "username": r["username"],
            "profile_image": r["profile_image"],
            "token": r["token_id"]
        })

    for r in winning_rows:
        grouped[str(r["win_date"])].append({
            "type": "winner",
            "username": r["username"],
            "profile_image": r["profile_image"],
            "token": r["token_id"]
        })

    # ✅ SORT DATE KEYS (latest first)
    sorted_result = dict(
        sorted(grouped.items(), key=lambda x: x[0], reverse=True)
    )

    return sorted_result