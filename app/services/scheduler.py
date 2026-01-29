from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text
from ..database import get_db

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

def rotate_daily_gift():
    db = next(get_db())
    try:
        # 1️⃣ Deactivate all gifts
        db.execute(text("""
            UPDATE gifts
            SET status = 'inactive';
        """))

        # 2️⃣ Activate gift based on weekday
        # Monday=1 ... Sunday=7
        db.execute(text("""
            WITH ranked_gifts AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        ORDER BY array_position(
                            ARRAY[3,7,9,10,13,14,15], id
                        )
                    ) AS rn
                FROM gifts
                WHERE id IN (3,7,9,10,13,14,15)
            )
            UPDATE gifts
            SET status = 'active'
            WHERE id = (
                SELECT id
                FROM ranked_gifts
                WHERE rn = EXTRACT(ISODOW FROM CURRENT_DATE)
            );
        """))

        db.commit()
        print("🎁 Weekday gift rotated successfully")

    except Exception as e:
        db.rollback()
        print("❌ Gift rotation failed:", e)

    finally:
        db.close()



