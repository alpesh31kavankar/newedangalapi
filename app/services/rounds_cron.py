from datetime import datetime, timezone
import random
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..database import SessionLocal
from ..models.category import Category
from ..models.product import Product
from ..models.question import Question
from ..models.question_round import QuestionRound
import pytz

# Active hours: only generate rounds between 8 AM and 10 PM
ACTIVE_START_HOUR = 11
ACTIVE_END_HOUR = 12

def generate_question_rounds():
    db: Session = SessionLocal()
    created_rounds = []

    try:
        # Current UTC time and convert to IST
        now_utc = datetime.now(timezone.utc)
        ist = pytz.timezone("Asia/Kolkata")
        now_local = now_utc.astimezone(ist)
        current_hour = now_local.hour

        # Skip generation if outside active hours
        if current_hour < ACTIVE_START_HOUR or current_hour >= ACTIVE_END_HOUR:
            print(f"⏰ Outside active hours ({ACTIVE_START_HOUR}-{ACTIVE_END_HOUR}), skipping round generation")
            return []

        categories = db.query(Category).all()

        for category in categories:
            # Latest round
            last_round = (
                db.query(QuestionRound)
                .filter(QuestionRound.categories_id == category.id)
                .order_by(QuestionRound.release_time.desc())
                .first()
            )

            # Skip if interval not passed
            if last_round:
                # Ensure last_round.release_time is timezone-aware
                last_round_time = last_round.release_time
                if last_round_time.tzinfo is None:
                    last_round_time = last_round_time.replace(tzinfo=timezone.utc)
                diff_seconds = (now_local - last_round_time).total_seconds()
                if diff_seconds < category.round_interval_minutes * 60:
                    print(f"⏳ Skipping category '{category.category_name}' ({diff_seconds/60:.1f} min since last round)")
                    continue

            # Get products
            products = db.query(Product).filter(Product.categories_id == category.id).all()
            if len(products) < 2:
                print(f"⚠️ Not enough products in category '{category.category_name}' to create a round")
                continue

            # Pick two products
            product1, product2 = random.sample(products, 2)

            # Random question
            question = db.query(Question).order_by(func.random()).first()
            if not question:
                print(f"⚠️ No questions found for category '{category.category_name}'")
                continue

            # Create round using timezone-aware now
            new_round = QuestionRound(
                questions_id=question.id,
                categories_id=category.id,
                product1_id=product1.id,
                product2_id=product2.id,
                release_time=now_local,
                max_votes=100,
            )
            db.add(new_round)
            created_rounds.append(new_round)
            print(f"✅ Created new round for category '{category.category_name}'")

        db.commit()
        return created_rounds

    except Exception as e:
        db.rollback()
        print(f"❌ Cron job error: {e}")
        raise
    finally:
        db.close()
