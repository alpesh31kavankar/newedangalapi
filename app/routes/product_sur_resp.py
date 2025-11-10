from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.product_sur_resp import ProductSurveyResponse
from ..models.product_sur_que import ProductSurveyQuestion
from ..schemas.product_sur_resp import (
    ProductSurveyResponseCreate,
    ProductSurveyResponseUpdate,
    ProductSurveyResponseOut,
)

router = APIRouter(prefix="/product-survey-response", tags=["Product Survey Response"])


# Create
@router.post("/", response_model=ProductSurveyResponseOut)
def create_survey_response(data: ProductSurveyResponseCreate, db: Session = Depends(get_db)):
    new_response = ProductSurveyResponse(**data.dict())
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    return new_response

@router.post("/submit")
def submit_survey_response(
    response_data: ProductSurveyResponseCreate,
    db: Session = Depends(get_db)
):
    # 1️⃣ Ensure the question exists
    question = db.query(ProductSurveyQuestion).filter(
        ProductSurveyQuestion.id == response_data.product_sur_queid
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # 2️⃣ Prevent duplicate submissions by the same user
    existing_response = db.query(ProductSurveyResponse).filter(
        ProductSurveyResponse.product_sur_queid == response_data.product_sur_queid,
        ProductSurveyResponse.userid == response_data.userid,
    ).first()

    if existing_response:
        raise HTTPException(
            status_code=400,
            detail="You have already submitted a response for this product."
        )

    # 3️⃣ Create a new response — directly approved
    new_response = ProductSurveyResponse(
        product_sur_queid=response_data.product_sur_queid,
        userid=response_data.userid,
        response=response_data.response,
        status="active",
        product_sur_resp_status="approved",  # ✅ Auto-approve
    )

    db.add(new_response)

    # 4️⃣ Update the corresponding question's response counts
    if response_data.response == "yes":
        question.yes_count += 1
    elif response_data.response == "no":
        question.no_count += 1
    elif response_data.response == "maybe":
        question.maybe_count += 1

    db.commit()
    db.refresh(new_response)

    return {"message": "Response submitted successfully", "data": new_response}



# Read all
@router.get("/", response_model=list[ProductSurveyResponseOut])
def get_all_survey_responses(db: Session = Depends(get_db)):
    return db.query(ProductSurveyResponse).all()


# Read single
@router.get("/{id}", response_model=ProductSurveyResponseOut)
def get_survey_response(id: int, db: Session = Depends(get_db)):
    response = db.query(ProductSurveyResponse).filter(ProductSurveyResponse.id == id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Survey response not found")
    return response


# Update
@router.put("/{id}", response_model=ProductSurveyResponseOut)
def update_survey_response(id: int, data: ProductSurveyResponseUpdate, db: Session = Depends(get_db)):
    response = db.query(ProductSurveyResponse).filter(ProductSurveyResponse.id == id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Survey response not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(response, key, value)

    db.commit()
    db.refresh(response)
    return response


# Delete
@router.delete("/{id}")
def delete_survey_response(id: int, db: Session = Depends(get_db)):
    response = db.query(ProductSurveyResponse).filter(ProductSurveyResponse.id == id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Survey response not found")

    db.delete(response)
    db.commit()
    return {"detail": "Survey response deleted successfully"}
