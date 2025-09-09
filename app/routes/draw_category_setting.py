from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/draw-category-settings", tags=["DrawCategorySettings"])

@router.post("/", response_model=schemas.draw_category_setting.DrawCategorySettingOut)
def create_setting(setting: schemas.draw_category_setting.DrawCategorySettingCreate, db: Session = Depends(get_db)):
    db_obj = models.draw_category_setting.DrawCategorySetting(**setting.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[schemas.draw_category_setting.DrawCategorySettingOut])
def get_settings(db: Session = Depends(get_db)):
    return db.query(models.draw_category_setting.DrawCategorySetting).all()
