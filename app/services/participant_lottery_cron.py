# app/services/participant_lottery_cron.py
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import SessionLocal


def perform_daily_participant_lottery():
    """
    Participant Lottery Cron Job:
    1. Fetch the active participant gift from p_gifts.
    2. Ensure one participant_lotteries row exists for today's date.
    3. Insert eligible tokens (source='vote') into participant_lottery_entries.
       - Avoid duplicates (ON CONFLICT DO NOTHING works only if UNIQUE constraint exists).
    4. Pick one random winner and insert into participant_lottery_winner.
    5. Mark today's participant lottery as completed.
    """

    today = date.today()
    print(f"[Participant Lottery Cron] Starting for {today}")

    db: Session = SessionLocal()
    try:
        # 1️⃣ Fetch active participant gift
        p_gift_id = db.execute(
            text("SELECT id FROM p_gifts WHERE status = 'active' LIMIT 1")
        ).scalar()

        if p_gift_id is None:
            print("[Participant Lottery Cron] ⚠️ No active participant gift found — skipping lottery.")
            return

        print(f"[Participant Lottery Cron] Using active p_gift id = {p_gift_id}")

        # 2️⃣ Ensure today's participant lottery exists
        insert_lottery_sql = text("""
            INSERT INTO participant_lotteries (lottery_date, lottery_round, p_gifts_id)
            SELECT :today, 1, :p_gift_id
            WHERE NOT EXISTS (
                SELECT 1 FROM participant_lotteries WHERE lottery_date = :today
            )
            RETURNING id
        """)
        res = db.execute(insert_lottery_sql, {"today": today, "p_gift_id": p_gift_id})
        row = res.fetchone()

        if row:
            lottery_id = row[0]
            print(f"[Participant Lottery Cron] ✅ Created new participant lottery id={lottery_id}")
        else:
            lottery_id = db.execute(
                text("SELECT id FROM participant_lotteries WHERE lottery_date = :today"),
                {"today": today}
            ).scalar()
            print(f"[Participant Lottery Cron] ℹ️ Participant lottery already exists (id={lottery_id})")

        if not lottery_id:
            raise RuntimeError("Could not create or retrieve today's participant lottery.")

        # 3️⃣ Insert eligible participant tokens (source='vote')
        insert_entries_sql = text("""
            INSERT INTO participant_lottery_entries (lottery_id, token_id, users_id, created_at)
            SELECT :lottery_id, t.token_id, t.users_id, now()
            FROM tokens t
            WHERE t.source = 'vote'
              AND t.created_at::date = :today
            ON CONFLICT (lottery_id, token_id) DO NOTHING
        """)
        db.execute(insert_entries_sql, {"lottery_id": lottery_id, "today": today})
        print("[Participant Lottery Cron] ✅ Inserted eligible participant tokens")

        # 4️⃣ Pick one random participant winner (if not already chosen)
        insert_winner_sql = text("""
            INSERT INTO participant_lottery_winner (lottery_id, users_id, token_id, created_at)
            SELECT ple.lottery_id, ple.users_id, ple.token_id, now()
            FROM participant_lottery_entries ple
            WHERE ple.lottery_id = :lottery_id
            ORDER BY RANDOM()
            LIMIT 1
            ON CONFLICT (lottery_id) DO NOTHING
        """)
        db.execute(insert_winner_sql, {"lottery_id": lottery_id})
        print("[Participant Lottery Cron] 🏆 Picked participant winner (if not already selected)")

        # 5️⃣ Mark participant lottery as completed
        db.execute(text("""
            UPDATE participant_lotteries
            SET is_completed = TRUE, updated_at = now()
            WHERE id = :lottery_id
        """), {"lottery_id": lottery_id})

        db.commit()
        print(f"[Participant Lottery Cron] ✅ Completed successfully for {today}")

    except Exception as e:
        db.rollback()
        print(f"[Participant Lottery Cron] ❌ ERROR: {e}")
        raise
    finally:
        db.close()
