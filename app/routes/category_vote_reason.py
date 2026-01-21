from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List

from ..database import get_db
from app.models.category_vote_reason import CategoryVoteReason
from app.models.question_round_vote_reason import QuestionRoundVoteReason
from app.models.question_round import QuestionRound
from app.schemas.category_vote_reason import CategoryVoteReasonOut

router = APIRouter(
    prefix="/category-vote-reasons",
    tags=["Category Vote Reasons"]
)


@router.get("/round/{question_round_id}", response_model=List[CategoryVoteReasonOut])
def get_reasons_for_round(
    question_round_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns the SAME 5 reasons for all users for a question round.
    Randomly picks 5 reasons only once per round, and then locks them.
    """

    try:
        # 1️⃣ Check if reasons already locked for this round
        existing = (
            db.query(CategoryVoteReason)
            .join(QuestionRoundVoteReason,
                  QuestionRoundVoteReason.reason_id == CategoryVoteReason.id)
            .filter(
                QuestionRoundVoteReason.question_rounds_id == question_round_id
            )
            .order_by(QuestionRoundVoteReason.id)
            .all()
        )
        if existing:
            return existing

        # 2️⃣ Get the category of the round (ORM version)
        round_obj = db.query(QuestionRound).filter(
            QuestionRound.id == question_round_id
        ).first()

        if not round_obj:
            raise HTTPException(status_code=404, detail="Question round not found")

        category_id = round_obj.categories_id

        # 3️⃣ Pick 5 random active reasons from this category
        reasons = (
            db.query(CategoryVoteReason)
            .filter(
                CategoryVoteReason.categories_id == category_id,
                CategoryVoteReason.is_active == True
            )
            .order_by(func.random())  # randomize order
            .limit(5)
            .all()
        )

        if len(reasons) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough active reasons in category {category_id}"
            )

        # 4️⃣ Lock the selected reasons for this round
        for r in reasons:
            db.add(
                QuestionRoundVoteReason(
                    question_rounds_id=question_round_id,
                    reason_id=r.id
                )
            )
        db.commit()

        return reasons

    except Exception as e:
        print("ERROR in get_reasons_for_round:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
