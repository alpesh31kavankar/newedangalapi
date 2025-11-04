
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random

from ..database import get_db
from ..models.daily_question import DailyQuestion
from ..models.randamqty import RandamQty
from ..schemas.daily_question import DailyQuestionOut

router = APIRouter(prefix="/daily-question", tags=["Daily Question"])

@router.get("/", response_model=DailyQuestionOut)
def get_daily_question(db: Session = Depends(get_db)):
    now = datetime.utcnow()

    daily = db.query(DailyQuestion).order_by(DailyQuestion.start_date.desc()).first()

    if not daily or daily.start_date.date() < now.date():
        all_questions = db.query(RandamQty).all()
        rand_ids = [r.id for r in all_questions]

        if not rand_ids:
            raise HTTPException(status_code=404, detail="No random questions available")

        used_ids = [q.randamqty_id for q in db.query(DailyQuestion).all()]
        available_ids = [qid for qid in rand_ids if qid not in used_ids]

        if not available_ids:
            available_ids = rand_ids

        new_id = random.choice(available_ids)
        daily = DailyQuestion(randamqty_id=new_id, start_date=now)
        db.add(daily)
        db.commit()
        db.refresh(daily)

    randamqty = db.query(RandamQty).filter(RandamQty.id == daily.randamqty_id).first()

    if not randamqty:
        raise HTTPException(status_code=404, detail="Question not found")

    return DailyQuestionOut(
        id=daily.id,
        randamqty_id=randamqty.id,
        randamqty_text=randamqty.randamqty_text,
        start_date=daily.start_date
    )

