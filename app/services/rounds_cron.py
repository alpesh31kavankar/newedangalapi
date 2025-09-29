# app/services/rounds_cron.py
from datetime import datetime, timezone
import random
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..database import SessionLocal
from ..models.category import Category
from ..models.product import Product
from ..models.question import Question
from ..models.question_round import QuestionRound

def generate_question_rounds():
    db: Session = SessionLocal()
    created_rounds = []

    try:
        # Fetch all categories
        categories = db.query(Category).all()

        for category in categories:
            # Get the latest round for this category
            last_round = (
                db.query(QuestionRound)
                .filter(QuestionRound.categories_id == category.id)
                .order_by(QuestionRound.release_time.desc())
                .first()
            )

            # Current UTC time (aware)
            now = datetime.now(timezone.utc)

            # Skip if last round exists and interval not passed
            if last_round:
                diff_seconds = (now - last_round.release_time).total_seconds()
                if diff_seconds < category.round_interval_minutes * 60:
                    print(f"⏳ Skipping category '{category.category_name}' ({diff_seconds/60:.1f} min since last round)")
                    continue

            # Get products for this category
            products = db.query(Product).filter(Product.categories_id == category.id).all()
            if len(products) < 2:
                print(f"⚠️ Not enough products in category '{category.category_name}' to create a round")
                continue

            # Randomly pick two products
            product1, product2 = random.sample(products, 2)

            # Random question
            question = db.query(Question).order_by(func.random()).first()
            if not question:
                print(f"⚠️ No questions found for category '{category.category_name}'")
                continue

            # Create new round
            new_round = QuestionRound(
                questions_id=question.id,
                categories_id=category.id,
                product1_id=product1.id,
                product2_id=product2.id,
                release_time=now,
                max_votes=100,
            )
            db.add(new_round)
            created_rounds.append(new_round)
            print(f"✅ Created new round for category '{category.category_name}'")

        # Commit all new rounds
        db.commit()
        return created_rounds

    except Exception as e:
        db.rollback()
        print(f"❌ Cron job error: {e}")
        raise
    finally:
        db.close()
