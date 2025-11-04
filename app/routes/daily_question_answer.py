
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.daily_question import DailyQuestion
from ..models.daily_question_answer import DailyQuestionAnswer
from ..schemas.daily_question_answer import AnswerCreate, AnswerResult
from ..models.user import User
from ..routes.auth import get_current_user

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
# ✅ Get results
@router.get("/{daily_question_id}/result")
def get_result(daily_question_id: int, db: Session = Depends(get_db)):
    yes_count = db.query(DailyQuestionAnswer).filter(
        DailyQuestionAnswer.daily_question_id == daily_question_id,
        DailyQuestionAnswer.answer == "Yes"
    ).count()

    no_count = db.query(DailyQuestionAnswer).filter(
        DailyQuestionAnswer.daily_question_id == daily_question_id,
        DailyQuestionAnswer.answer == "No"
    ).count()

    total_votes = yes_count + no_count

    if total_votes == 0:
        yes_percent = no_percent = 0
    else:
        yes_percent = round((yes_count / total_votes) * 100, 2)
        no_percent = round((no_count / total_votes) * 100, 2)

    return {
        "yes_count": yes_count,
        "no_count": no_count,
        "total_votes": total_votes,
        "yes_percent": yes_percent,
        "no_percent": no_percent,
    }



# ✅ Check if the user already voted
@router.get("/{daily_question_id}/check-vote")
def check_vote_status(
    daily_question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if the logged-in user already voted on this daily question.
    """
    existing_vote = db.query(DailyQuestionAnswer).filter(
        DailyQuestionAnswer.daily_question_id == daily_question_id,
        DailyQuestionAnswer.user_id == current_user.id
    ).first()

    if existing_vote:
        return {"has_voted": True, "answer": existing_vote.answer}
    return {"has_voted": False}