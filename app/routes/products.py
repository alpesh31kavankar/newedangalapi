# app/routers/product.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# Create product
@router.post("/", response_model=schemas.product.ProductOut)
def create_product(product: schemas.product.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.product.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Get all products
@router.get("/", response_model=List[schemas.product.ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.product.Product).all()

# Get single product
@router.get("/{product_id}", response_model=schemas.product.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.product.Product).filter(models.product.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update product
@router.put("/{product_id}", response_model=schemas.product.ProductOut)
def update_product(product_id: int, update: schemas.product.ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.product.Product).filter(models.product.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in update.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product

# Delete product
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.product.Product).filter(models.product.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"detail": "Product deleted successfully"}
