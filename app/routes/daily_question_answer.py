# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models.daily_question import DailyQuestion
# from ..models.daily_question_answer import DailyQuestionAnswer
# from ..schemas.daily_question_answer import AnswerCreate, AnswerResult

# router = APIRouter(prefix="/daily-question-answer", tags=["Daily Question Answer"])

# @router.post("/{daily_question_id}/answer")
# def submit_answer(daily_question_id: int, answer: AnswerCreate, db: Session = Depends(get_db)):
#     if answer.answer not in ["Yes", "No"]:
#         raise HTTPException(status_code=400, detail="Answer must be 'Yes' or 'No'")

#     daily = db.query(DailyQuestion).filter(DailyQuestion.id == daily_question_id).first()
#     if not daily:
#         raise HTTPException(status_code=404, detail="Daily question not found")

#     existing = db.query(DailyQuestionAnswer).filter(
#         DailyQuestionAnswer.daily_question_id == daily_question_id,
#         DailyQuestionAnswer.user_id == answer.user_id
#     ).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="User already answered this question today")

#     new_answer = DailyQuestionAnswer(
#         daily_question_id=daily_question_id,
#         user_id=answer.user_id,
#         answer=answer.answer
#     )
#     db.add(new_answer)
#     db.commit()
#     return {"detail": "Answer submitted successfully"}

# @router.get("/{daily_question_id}/result", response_model=AnswerResult)
# def get_result(daily_question_id: int, db: Session = Depends(get_db)):
#     yes_count = db.query(DailyQuestionAnswer).filter(
#         DailyQuestionAnswer.daily_question_id == daily_question_id,
#         DailyQuestionAnswer.answer == "Yes"
#     ).count()
#     no_count = db.query(DailyQuestionAnswer).filter(
#         DailyQuestionAnswer.daily_question_id == daily_question_id,
#         DailyQuestionAnswer.answer == "No"
#     ).count()
#     return AnswerResult(yes_count=yes_count, no_count=no_count)






from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.daily_question import DailyQuestion
from ..models.daily_question_answer import DailyQuestionAnswer
from ..schemas.daily_question_answer import AnswerCreate, AnswerResult

router = APIRouter(prefix="/daily-question-answer", tags=["Daily Question Answer"])

# ✅ Submit answer (Yes/No)
@router.post("/{daily_question_id}/answer")
def submit_answer(daily_question_id: int, answer: AnswerCreate, db: Session = Depends(get_db)):
    # Validate Yes/No
    user_answer = answer.answer.strip().capitalize()
    if user_answer not in ["Yes", "No"]:
        raise HTTPException(status_code=400, detail="Answer must be 'Yes' or 'No'")

    # Verify question exists
    daily = db.query(DailyQuestion).filter(DailyQuestion.id == daily_question_id).first()
    if not daily:
        raise HTTPException(status_code=404, detail="Daily question not found")

    # Prevent multiple answers by same user
    existing = db.query(DailyQuestionAnswer).filter(
        DailyQuestionAnswer.daily_question_id == daily_question_id,
        DailyQuestionAnswer.user_id == answer.user_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already answered this question")

    # Save new answer
    new_answer = DailyQuestionAnswer(
        daily_question_id=daily_question_id,
        user_id=answer.user_id,
        answer=user_answer
    )
    db.add(new_answer)
    db.commit()
    return {"detail": "Answer submitted successfully"}

# ✅ Get results
@router.get("/{daily_question_id}/result", response_model=AnswerResult)
def get_result(daily_question_id: int, db: Session = Depends(get_db)):
    yes_count = db.query(DailyQuestionAnswer).filter(
        DailyQuestionAnswer.daily_question_id == daily_question_id,
        DailyQuestionAnswer.answer == "Yes"
    ).count()

    no_count = db.query(DailyQuestionAnswer).filter(
        DailyQuestionAnswer.daily_question_id == daily_question_id,
        DailyQuestionAnswer.answer == "No"
    ).count()

    return AnswerResult(yes_count=yes_count, no_count=no_count)
