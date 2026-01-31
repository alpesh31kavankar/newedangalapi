from datetime import datetime, timedelta, time
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import SessionLocal
import pytz

def perform_daily_participant_lottery():
    """
    Participant Lottery Cron Job (IST-safe, UTC DB):
    1. Fetch active participant gift
    2. Ensure today's participant lottery exists (IST date)
    3. Insert eligible vote tokens created TODAY in IST
    4. Pick one winner (excluding last 5 days)
    5. Mark lottery completed
    """

    db: Session = SessionLocal()

    try:
        # -----------------------------
        # 1️⃣ IST → UTC day window
        # -----------------------------
        IST = pytz.timezone("Asia/Kolkata")
        today_ist = datetime.now(IST).date()

        start_ist = datetime.combine(today_ist, time.min).replace(tzinfo=IST)
        end_ist = start_ist + timedelta(days=1)

        start_utc = start_ist.astimezone(pytz.UTC)
        end_utc = end_ist.astimezone(pytz.UTC)

        now_ist = datetime.now(IST)

        print(f"[Participant Lottery Cron] Running for IST date {today_ist}")

        # -----------------------------
        # 2️⃣ Fetch active participant gift
        # -----------------------------
        p_gift_id = db.execute(
            text("SELECT id FROM p_gifts WHERE status = 'active' LIMIT 1")
        ).scalar()

        if not p_gift_id:
            print("[Participant Lottery Cron] ⚠️ No active participant gift found — skipping.")
            return

        # -----------------------------
        # 3️⃣ Create participant lottery if not exists
        # -----------------------------
        row = db.execute(text("""
            INSERT INTO participant_lotteries (lottery_date, lottery_round, p_gifts_id)
            SELECT :today_ist, 1, :p_gift_id
            WHERE NOT EXISTS (
                SELECT 1 FROM participant_lotteries WHERE lottery_date = :today_ist
            )
            RETURNING id
        """), {
            "today_ist": today_ist,
            "p_gift_id": p_gift_id
        }).fetchone()

        if row:
            lottery_id = row[0]
        else:
            lottery_id = db.execute(
                text("SELECT id FROM participant_lotteries WHERE lottery_date = :today_ist"),
                {"today_ist": today_ist}
            ).scalar()

        if not lottery_id:
            raise RuntimeError("Failed to create or fetch participant lottery")

        # -----------------------------
        # 4️⃣ Insert eligible vote tokens (FIXED)
        # -----------------------------
        db.execute(text("""
            INSERT INTO participant_lottery_entries (lottery_id, token_id, users_id, created_at)
            SELECT :lottery_id, t.token_id, t.users_id, :now_ist
            FROM tokens t
            WHERE t.source = 'vote'
              AND t.created_at >= :start_utc
              AND t.created_at < :end_utc
            ON CONFLICT (lottery_id, token_id) DO NOTHING
        """), {
            "lottery_id": lottery_id,
            "now_ist": now_ist,
            "start_utc": start_utc,
            "end_utc": end_utc
        })

        print("[Participant Lottery Cron] ✅ Inserted eligible vote tokens")

        # -----------------------------
        # 5️⃣ Pick winner (exclude last 5 days)
        # -----------------------------
        last_5_days = today_ist - timedelta(days=5)

        db.execute(text("""
            INSERT INTO participant_lottery_winner (lottery_id, users_id, token_id, created_at)
            SELECT ple.lottery_id, ple.users_id, ple.token_id, :now_ist
            FROM participant_lottery_entries ple
            WHERE ple.lottery_id = :lottery_id
              AND ple.users_id NOT IN (
                  SELECT DISTINCT pw.users_id
                  FROM participant_lottery_winner pw
                  JOIN participant_lotteries pl ON pl.id = pw.lottery_id
                  WHERE pl.lottery_date >= :last_5_days
                    AND pl.lottery_date < :today_ist
              )
            ORDER BY RANDOM()
            LIMIT 1
            ON CONFLICT (lottery_id) DO NOTHING
        """), {
            "lottery_id": lottery_id,
            "now_ist": now_ist,
            "last_5_days": last_5_days,
            "today_ist": today_ist
        })

        # -----------------------------
        # 6️⃣ Mark lottery completed
        # -----------------------------
        db.execute(text("""
            UPDATE participant_lotteries
            SET is_completed = TRUE, updated_at = :now_ist
            WHERE id = :lottery_id
        """), {
            "lottery_id": lottery_id,
            "now_ist": now_ist
        })

        db.commit()
        print(f"[Participant Lottery Cron] ✅ Completed for {today_ist}")

    except Exception as e:
        db.rollback()
        print(f"[Participant Lottery Cron] ❌ ERROR: {e}")
        raise
    finally:
        db.close()
