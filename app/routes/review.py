from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload  
from sqlalchemy.sql import func  # ✅ ADD THIS LINE
from ..database import get_db
from ..models.review import ProductReview
from ..schemas.review import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["reviews"])

# Create review
@router.post("/", response_model=ReviewOut)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    new_review = ProductReview(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# Get all reviews for a product
# @router.get("/product/{product_id}", response_model=list[ReviewOut])
# def get_reviews_for_product(product_id: int, db: Session = Depends(get_db)):
#     return db.query(ProductReview).filter(ProductReview.product_id == product_id).all()
@router.get("/product/{product_id}", response_model=list[ReviewOut])
def get_reviews_for_product(product_id: int, db: Session = Depends(get_db)):
    # Join ProductReview with User to get username
    reviews = (
        db.query(ProductReview)
        .options(joinedload(ProductReview.user))
        .filter(ProductReview.product_id == product_id)
        .all()
    )

    # Add username to each review dict
    result = []
    for r in reviews:
        review_data = r.__dict__.copy()
        review_data["username"] = r.user.username if r.user else None
        result.append(review_data)

    return result

# Get average rating for a product
@router.get("/product/{product_id}/average")
def get_average_rating(product_id: int, db: Session = Depends(get_db)):
    avg_rating = db.query(func.avg(ProductReview.rating)).filter(ProductReview.product_id == product_id).scalar()
    return {"product_id": product_id, "average_rating": round(avg_rating or 0, 2)}
