# routes/main_categories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
# from app.database import get_db
from ..database import  get_db, engine
from app.models.main_category import MainCategory
from app.schemas.main_category import MainCategoryCreate, MainCategoryOut, MainCategoryUpdate

# if you want DB tables created automatically (optional)
# from models import some_other_models... then:
# MainCategory.metadata.create_all(bind=engine)  # typically use Alembic in prod

router = APIRouter(prefix="/main-categories", tags=["main_categories"])



@router.post("/", response_model=MainCategoryOut, status_code=status.HTTP_201_CREATED)
def create_main_category(payload: MainCategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(MainCategory).filter(MainCategory.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="MainCategory with this name already exists")
    mc = MainCategory(
        name=payload.name,
        interval_minutes=payload.interval_minutes or 10,
        image_url=payload.image_url
    )
    db.add(mc)
    db.commit()
    db.refresh(mc)
    return mc


@router.get("/", response_model=List[MainCategoryOut])
def list_main_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(MainCategory).offset(skip).limit(limit).all()
    return items


@router.get("/{mc_id}", response_model=MainCategoryOut)
def get_main_category(mc_id: int, db: Session = Depends(get_db)):
    mc = db.query(MainCategory).get(mc_id)
    if not mc:
        raise HTTPException(status_code=404, detail="MainCategory not found")
    return mc


@router.put("/{mc_id}", response_model=MainCategoryOut)
def update_main_category(mc_id: int, payload: MainCategoryUpdate, db: Session = Depends(get_db)):
    mc = db.query(MainCategory).get(mc_id)
    if not mc:
        raise HTTPException(status_code=404, detail="MainCategory not found")

    if payload.name is not None:
        mc.name = payload.name
    if payload.interval_minutes is not None:
        mc.interval_minutes = payload.interval_minutes
    if payload.image_url is not None:
        mc.image_url = payload.image_url

    db.add(mc)
    db.commit()
    db.refresh(mc)
    return mc


@router.delete("/{mc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_main_category(mc_id: int, db: Session = Depends(get_db)):
    mc = db.query(MainCategory).get(mc_id)
    if not mc:
        raise HTTPException(status_code=404, detail="MainCategory not found")
    db.delete(mc)
    db.commit()
    return
