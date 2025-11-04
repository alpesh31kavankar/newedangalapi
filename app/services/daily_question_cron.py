from datetime import datetime
import random
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.daily_question import DailyQuestion
from ..models.randamqty import RandamQty

def pick_daily_question():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()

        # Get today's existing question
        today_q = db.query(DailyQuestion).filter(
            DailyQuestion.start_date >= datetime(now.year, now.month, now.day)
        ).first()

        if today_q:
            print(f"✅ Already have a daily question for {now.date()}: ID {today_q.id}")
            return

        # Get all RandamQty IDs
        all_questions = db.query(RandamQty).all()
        if not all_questions:
            print("⚠️ No questions available in RandamQty table.")
            return

        rand_ids = [q.id for q in all_questions]

        # Get all used question IDs
        used_ids = [q.randamqty_id for q in db.query(DailyQuestion).all()]

        # Filter unused questions
        available_ids = [qid for qid in rand_ids if qid not in used_ids]

        # If all questions used, allow reusing
        if not available_ids:
            print("♻️ All questions used. Resetting pool.")
            available_ids = rand_ids

        # Pick one random question
        new_id = random.choice(available_ids)

        # Save in DailyQuestion table
        new_q = DailyQuestion(randamqty_id=new_id, start_date=now)
        db.add(new_q)
        db.commit()
        db.refresh(new_q)

        print(f"🌞 New daily question selected: RandamQty ID {new_id} (DailyQuestion ID {new_q.id})")

    except Exception as e:
        print(f"❌ Error in daily question cron: {e}")
        db.rollback()
    finally:
        db.close()
