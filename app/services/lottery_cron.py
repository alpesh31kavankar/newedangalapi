# app/services/lottery_cron.py
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import SessionLocal

def perform_daily_lottery():
    """
    1) Ensure one lottery row exists for today (lottery_round = 1) with active gift.
    2) Insert eligible tokens (status = 'C_referral', 'C_referral_bonus', 'daily_lucky_draw')
       into lottery_entries (ON CONFLICT DO NOTHING).
    3) Randomly pick one entry from lottery_entries for today's lottery and insert into lottery_winner
       (ON CONFLICT DO NOTHING to avoid duplicates).
    4) Mark lottery as completed.
    """
    today = date.today()
    print(f"[Lottery Cron] Starting lottery for {today}")

    db: Session = SessionLocal()
    try:
        # 0) Fetch active gift id
        gift_id = db.execute(
            text("SELECT id FROM gifts WHERE status = 'active' LIMIT 1")
        ).scalar()
        if gift_id is None:
            raise RuntimeError("No active gift found for today's lottery")
        print(f"[Lottery Cron] Using active gift id={gift_id}")

        # 1) Create today's lottery if not exists
        insert_lottery_sql = text("""
            INSERT INTO lotteries (lottery_date, lottery_round, gifts_id)
            SELECT :today, 1, :gift_id
            WHERE NOT EXISTS (
                SELECT 1 FROM lotteries WHERE lottery_date = :today
            )
            RETURNING id
        """)
        res = db.execute(insert_lottery_sql, {"today": today, "gift_id": gift_id})
        row = res.fetchone()
        if row:
            lottery_id = row[0]
            print(f"[Lottery Cron] Created new lottery id={lottery_id} for {today}")
        else:
            lottery_id = db.execute(
                text("SELECT id FROM lotteries WHERE lottery_date = :today"),
                {"today": today}
            ).scalar()
            print(f"[Lottery Cron] Lottery already exists id={lottery_id} for {today}")

        if lottery_id is None:
            raise RuntimeError("Could not create or find today's lottery")

        # 2) Insert eligible tokens into lottery_entries
        insert_entries_sql = text("""
            INSERT INTO lottery_entries (lotteries_id, token_id, users_id, created_at)
            SELECT :lottery_id, t.token_id, t.users_id, now()
            FROM tokens t
            WHERE t.source IN ('C_referral','claim', 'C_referral_bonus', 'daily_lucky_draw')
              AND (t.created_at::date = :today)
            ON CONFLICT (lotteries_id, token_id) DO NOTHING
        """)
        db.execute(insert_entries_sql, {"lottery_id": lottery_id, "today": today})
        print("[Lottery Cron] Inserted eligible tokens into lottery_entries (if any)")

        # 3) Pick one random winner for this lottery
        insert_winner_sql = text("""
            INSERT INTO lottery_winner (lotteries_id, users_id, token_id, created_at)
            SELECT le.lotteries_id, le.users_id, le.token_id, now()
            FROM lottery_entries le
            WHERE le.lotteries_id = :lottery_id
            ORDER BY RANDOM()
            LIMIT 1
            ON CONFLICT (lotteries_id) DO NOTHING
        """)
        db.execute(insert_winner_sql, {"lottery_id": lottery_id})

        # 4) Mark lottery as completed
        db.execute(text("""
            UPDATE lotteries
            SET is_completed = TRUE, updated_at = now()
            WHERE id = :lottery_id
        """), {"lottery_id": lottery_id})

        db.commit()
        print(f"[Lottery Cron] Completed lottery processing for id={lottery_id}")

    except Exception as e:
        db.rollback()
        print(f"[Lottery Cron] ERROR: {e}")
        raise
    finally:
        db.close()
