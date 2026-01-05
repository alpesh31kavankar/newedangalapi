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

#     participant_rows = db.execute(text("""
#         SELECT
#             w.created_at::date AS win_date,
#             w.token_id,
#             u.username,
#             u.profile_image
#         FROM participant_lottery_winner w
#         JOIN users u ON u.id = w.users_id
#         ORDER BY w.created_at DESC
#     """)).mappings().all()

#     winning_rows = db.execute(text("""
#         SELECT
#             w.created_at::date AS win_date,
#             w.token_id,
#             u.username,
#             u.profile_image
#         FROM lottery_winner w
#         JOIN users u ON u.id = w.users_id
#         ORDER BY w.created_at DESC
#     """)).mappings().all()

#     db.close()

#     grouped = defaultdict(list)

#     for r in participant_rows:
#         grouped[str(r["win_date"])].append({
#             "type": "participant",
#             "username": r["username"],
#             "profile_image": r["profile_image"],
#             "token": r["token_id"]
#         })

#     for r in winning_rows:
#         grouped[str(r["win_date"])].append({
#             "type": "winner",
#             "username": r["username"],
#             "profile_image": r["profile_image"],
#             "token": r["token_id"]
#         })

#     # ✅ SORT DATE KEYS (latest first)
#     sorted_result = dict(
#         sorted(grouped.items(), key=lambda x: x[0], reverse=True)
#     )

#     return sorted_result


@router.get("/history")
def lottery_history():
    db = SessionLocal()

    participant_rows = db.execute(text("""
        SELECT
            p.created_at::date AS win_date,
            p.token_id,
            u.username,
            u.profile_image,
            p.lottery_id AS lottery_id, 
            CASE
                WHEN rc.id IS NOT NULL THEN true
                ELSE false
            END AS is_claimed
        FROM participant_lottery_winner p
        JOIN users u ON u.id = p.users_id
        LEFT JOIN reward_claims rc
            ON rc.user_id = p.users_id
            AND rc.lottery_id = p.lottery_id  
            AND rc.claim_type = 'participant'
        ORDER BY p.created_at DESC
    """)).mappings().all()

    winning_rows = db.execute(text("""
        SELECT
            w.created_at::date AS win_date,
            w.token_id,
            u.username,
            u.profile_image,
            w.lotteries_id AS lottery_id,
            CASE
                WHEN rc.id IS NOT NULL THEN true
                ELSE false
            END AS is_claimed
        FROM lottery_winner w
        JOIN users u ON u.id = w.users_id
        LEFT JOIN reward_claims rc
            ON rc.user_id = w.users_id
            AND rc.lottery_id = w.lotteries_id
            AND rc.claim_type = 'winning'
        ORDER BY w.created_at DESC
    """)).mappings().all()

    db.close()

    grouped = defaultdict(list)

    for r in participant_rows:
        grouped[str(r["win_date"])].append({
            "type": "participant",
            "username": r["username"],
            "profile_image": r["profile_image"],
            "token": r["token_id"],
            "lottery_id": r["lottery_id"],
            "is_claimed": r["is_claimed"]
        })

    for r in winning_rows:
        grouped[str(r["win_date"])].append({
            "type": "winner",
            "username": r["username"],
            "profile_image": r["profile_image"],
            "token": r["token_id"],
            "lottery_id": r["lottery_id"],
            "is_claimed": r["is_claimed"]
        })

    # ✅ latest date first
    sorted_result = dict(
        sorted(grouped.items(), key=lambda x: x[0], reverse=True)
    )

    return sorted_result