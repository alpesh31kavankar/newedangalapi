from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/user-tokens", tags=["UserTokens"])

@router.post("/", response_model=schemas.user_token.UserTokenOut)
def create_user_token(token: schemas.user_token.UserTokenCreate, db: Session = Depends(get_db)):
    db_token = models.user_token.UserToken(**token.dict())
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

@router.get("/", response_model=List[schemas.user_token.UserTokenOut])
def get_user_tokens(db: Session = Depends(get_db)):
    return db.query(models.user_token.UserToken).all()
