from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..routes.auth import get_current_user
from app.models.product_vote_opinion import ProductVoteOpinion
from app.models.question_round import QuestionRound
from app.schemas.opinion_schema import OpinionCreate

router = APIRouter(
    prefix="/opinions",
    tags=["Opinions"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_opinion(
    payload: OpinionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1️⃣ Check round exists
    round_obj = db.query(QuestionRound).filter(
        QuestionRound.id == payload.question_round_id
    ).first()

    if not round_obj:
        raise HTTPException(status_code=404, detail="Question round not found")

    # 2️⃣ Prevent duplicate opinion
    existing = db.query(ProductVoteOpinion).filter(
        ProductVoteOpinion.user_id == current_user.id,
        ProductVoteOpinion.question_round_id == payload.question_round_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already submitted opinion for this round"
        )

    # 3️⃣ Validate products belong to round
    valid_products = {round_obj.product1_id, round_obj.product2_id}

    if payload.selected_product_id not in valid_products:
        raise HTTPException(status_code=400, detail="Invalid selected product")

    if payload.opposite_product_id not in valid_products:
        raise HTTPException(status_code=400, detail="Invalid opposite product")

    if payload.selected_product_id == payload.opposite_product_id:
        raise HTTPException(status_code=400, detail="Products cannot be same")

    # 4️⃣ Create opinion
    opinion = ProductVoteOpinion(
        user_id=current_user.id,
        question_round_id=payload.question_round_id,
        category_id=payload.category_id,
        selected_product_id=payload.selected_product_id,
        opposite_product_id=payload.opposite_product_id,
        reason_id=payload.reason_id
    )

    db.add(opinion)
    db.commit()
    db.refresh(opinion)

    return {"message": "Opinion saved successfully"}
