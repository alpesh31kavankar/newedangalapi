from datetime import datetime, timezone
import random
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..database import SessionLocal
from ..models.category import Category
from ..models.product import Product
from ..models.question import Question
from ..models.question_round import QuestionRound
from ..models.main_category import MainCategory
import pytz

ACTIVE_START_HOUR = 1
ACTIVE_END_HOUR = 19

def generate_question_rounds():
    db: Session = SessionLocal()
    created_rounds = []

    try:
        # Current time in IST
        now_utc = datetime.now(timezone.utc)
        ist = pytz.timezone("Asia/Kolkata")
        now_local = now_utc.astimezone(ist)
        current_hour = now_local.hour

        # Check active hours
        if current_hour < ACTIVE_START_HOUR or current_hour >= ACTIVE_END_HOUR:
            print("⏰ Outside active hours, skipping round generation.")
            return []

        # Load all main categories
        maincategories = db.query(MainCategory).all()

        for maincat in maincategories:

            # 1️⃣ Find last created round for this MAIN category
            last_round = (
                db.query(QuestionRound)
                .join(Category, Category.id == QuestionRound.categories_id)
                .filter(Category.maincategory_id == maincat.id)
                .order_by(QuestionRound.release_time.desc())
                .first()
            )

            # 2️⃣ Interval check
            if last_round:
                last_time = last_round.release_time
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)

                diff_seconds = (now_local - last_time).total_seconds()

                if diff_seconds < maincat.interval_minutes * 60:
                    print(f"⏳ '{maincat.name}' waiting... interval not finished.")
                    continue

            # 3️⃣ Get all subcategories under this main category
            subcategories = (
                db.query(Category)
                .filter(Category.maincategory_id == maincat.id)
                .all()
            )

            if not subcategories:
                print(f"⚠️ No subcategories for maincategory '{maincat.name}'")
                continue

            # 4️⃣ Pick ONE subcategory randomly
            selected_category = random.choice(subcategories)

            # 5️⃣ Load products from this subcategory
            products = (
                db.query(Product)
                .filter(Product.categories_id == selected_category.id)
                .all()
            )

            if len(products) < 2:
                print(f"⚠️ Not enough products in '{selected_category.category_name}'")
                continue

            product1, product2 = random.sample(products, 2)

            # 6️⃣ Load questions from this subcategory
            questions = (
                db.query(Question)
                .filter(Question.category_id == selected_category.id)
                .all()
            )

            if not questions:
                print(f"⚠️ No questions for '{selected_category.category_name}'")
                continue

            question = random.choice(questions)

            # 7️⃣ Create the new round
            new_round = QuestionRound(
                questions_id=question.id,
                categories_id=selected_category.id,
                product1_id=product1.id,
                product2_id=product2.id,
                release_time=now_local,
                max_votes=5
            )

            db.add(new_round)
            created_rounds.append(new_round)

            print(
                f"🔥 Round Created → MainCategory: {maincat.name}, "
                f"SubCategory: {selected_category.category_name}"
            )

        db.commit()
        return created_rounds

    except Exception as e:
        db.rollback()
        print("❌ Cron Error:", e)
        raise
    finally:
        db.close()
