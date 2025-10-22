from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..routes.auth import get_current_user
from ..database import get_db
from ..schemas.user import UserOut  # Use Pydantic schema

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=UserOut)  # <-- Important
def get_me(current_user=Depends(get_current_user)):
    return current_user
