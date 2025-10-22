from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
@router.get("/product/{product_id}", response_model=list[ReviewOut])
def get_reviews_for_product(product_id: int, db: Session = Depends(get_db)):
    return db.query(ProductReview).filter(ProductReview.product_id == product_id).all()

# Get average rating for a product
@router.get("/product/{product_id}/average")
def get_average_rating(product_id: int, db: Session = Depends(get_db)):
    avg_rating = db.query(func.avg(ProductReview.rating)).filter(ProductReview.product_id == product_id).scalar()
    return {"product_id": product_id, "average_rating": round(avg_rating or 0, 2)}
