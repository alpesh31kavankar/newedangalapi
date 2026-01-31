from datetime import datetime, timedelta, time
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import SessionLocal
import pytz

def perform_daily_lottery():
    """
    Daily Lottery (IST-safe, UTC DB)
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

        print(f"[Lottery Cron] Running for IST date {today_ist}")

        # -----------------------------
        # 2️⃣ Fetch active gift
        # -----------------------------
        gift_id = db.execute(
            text("SELECT id FROM gifts WHERE status = 'active' LIMIT 1")
        ).scalar()

        if not gift_id:
            raise RuntimeError("No active gift found")

        # -----------------------------
        # 3️⃣ Create lottery if not exists
        # -----------------------------
        row = db.execute(text("""
            INSERT INTO lotteries (lottery_date, lottery_round, gifts_id)
            SELECT :today_ist, 1, :gift_id
            WHERE NOT EXISTS (
                SELECT 1 FROM lotteries WHERE lottery_date = :today_ist
            )
            RETURNING id
        """), {
            "today_ist": today_ist,
            "gift_id": gift_id
        }).fetchone()

        if row:
            lottery_id = row[0]
        else:
            lottery_id = db.execute(
                text("SELECT id FROM lotteries WHERE lottery_date = :today_ist"),
                {"today_ist": today_ist}
            ).scalar()

        if not lottery_id:
            raise RuntimeError("Failed to create or fetch lottery")

        # -----------------------------
        # 4️⃣ Insert eligible tokens
        # -----------------------------
        db.execute(text("""
            INSERT INTO lottery_entries (lotteries_id, token_id, users_id, created_at)
            SELECT :lottery_id, t.token_id, t.users_id, :now_ist
            FROM tokens t
            WHERE t.source IN (
                'C_referral','claim','C_referral_bonus',
                'C_spin','monthly_reward','daily_lucky_draw'
            )
            AND t.created_at >= :start_utc
            AND t.created_at < :end_utc
            ON CONFLICT (lotteries_id, token_id) DO NOTHING
        """), {
            "lottery_id": lottery_id,
            "now_ist": now_ist,
            "start_utc": start_utc,
            "end_utc": end_utc
        })

        # -----------------------------
        # 5️⃣ Pick winner (exclude last 5 days)
        # -----------------------------
        last_5_days = today_ist - timedelta(days=5)

        db.execute(text("""
            INSERT INTO lottery_winner (lotteries_id, users_id, token_id, created_at)
            SELECT le.lotteries_id, le.users_id, le.token_id, :now_ist
            FROM lottery_entries le
            WHERE le.lotteries_id = :lottery_id
              AND le.users_id NOT IN (
                  SELECT DISTINCT lw.users_id
                  FROM lottery_winner lw
                  JOIN lotteries l ON l.id = lw.lotteries_id
                  WHERE l.lottery_date >= :last_5_days
                    AND l.lottery_date < :today_ist
              )
            ORDER BY RANDOM()
            LIMIT 1
            ON CONFLICT (lotteries_id) DO NOTHING
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
            UPDATE lotteries
            SET is_completed = TRUE, updated_at = :now_ist
            WHERE id = :lottery_id
        """), {
            "lottery_id": lottery_id,
            "now_ist": now_ist
        })

        db.commit()
        print(f"[Lottery Cron] Lottery completed for {today_ist}")

    except Exception as e:
        db.rollback()
        print(f"[Lottery Cron] ERROR: {e}")
        raise
    finally:
        db.close()
