

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
ACTIVE_END_HOUR = 23

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

            # 3️⃣ Get all subcategories with at least 2 products and 1 question
            subcategories = (
                db.query(Category)
                .filter(Category.maincategory_id == maincat.id)
                .all()
            )

            valid_subcategories = []
            for subcat in subcategories:
                product_count = db.query(Product).filter(Product.categories_id == subcat.id).count()
                question_count = db.query(Question).filter(Question.categories_id == subcat.id).count()
                if product_count >= 2 and question_count >= 1:
                    valid_subcategories.append(subcat)

            if not valid_subcategories:
                print(f"⚠️ No valid subcategories for maincategory '{maincat.name}'")
                continue

            # 4️⃣ Pick ONE valid subcategory randomly
            selected_category = random.choice(valid_subcategories)

            # 5️⃣ Pick 2 random products
            products = db.query(Product).filter(Product.categories_id == selected_category.id).all()
            product1, product2 = random.sample(products, 2)

            # 6️⃣ Pick 1 random question
            questions = db.query(Question).filter(Question.categories_id == selected_category.id).all()
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
            db.commit()           # ← REQUIRED so ID gets generated
            db.refresh(new_round)
            created_rounds.append(new_round)

            print(
                f"🔥 Round Created → MainCategory: {maincat.name}, "
                f"SubCategory: {selected_category.category_name}"
            )

        return created_rounds

    except Exception as e:
        db.rollback()
        print("❌ Cron Error:", e)
        raise
    finally:
        db.close()

