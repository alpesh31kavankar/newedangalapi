from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.product import Product
from ..models.review import ProductReview
from ..schemas.product import ProductCreate, ProductOut

router = APIRouter(prefix="/products", tags=["products"])

# Create product
@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return ProductOut.from_orm(new_product)

# Get all products with avg_rating & review_count
@router.get("/", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)):
    # Join with reviews to calculate avg_rating and review_count
    results = (
        db.query(
            Product,
            func.coalesce(func.avg(ProductReview.rating), 0).label("avg_rating"),
            func.coalesce(func.count(ProductReview.id), 0).label("review_count")
        )
        .outerjoin(ProductReview, Product.id == ProductReview.product_id)
        .group_by(Product.id)
        .all()
    )

    products_list = [
        ProductOut.from_orm(product).model_copy(update={
            "avg_rating": float(avg_rating),
            "review_count": int(review_count)
        })
        for product, avg_rating, review_count in results
    ]
    return products_list

# Get single product by ID
@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(
            Product,
            func.coalesce(func.avg(ProductReview.rating), 0).label("avg_rating"),
            func.coalesce(func.count(ProductReview.id), 0).label("review_count")
        )
        .outerjoin(ProductReview, Product.id == ProductReview.product_id)
        .filter(Product.id == product_id)
        .group_by(Product.id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    product, avg_rating, review_count = result
    return ProductOut.from_orm(product).model_copy(update={
        "avg_rating": float(avg_rating),
        "review_count": int(review_count)
    })

# Get products by category
@router.get("/category/{category_id}", response_model=list[ProductOut])
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            Product,
            func.coalesce(func.avg(ProductReview.rating), 0).label("avg_rating"),
            func.coalesce(func.count(ProductReview.id), 0).label("review_count")
        )
        .outerjoin(ProductReview, Product.id == ProductReview.product_id)
        .filter(Product.categories_id == category_id)
        .group_by(Product.id)
        .all()
    )

    products_list = [
        ProductOut.from_orm(product).model_copy(update={
            "avg_rating": float(avg_rating),
            "review_count": int(review_count)
        })
        for product, avg_rating, review_count in results
    ]
    return products_list
