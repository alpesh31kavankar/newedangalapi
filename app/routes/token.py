from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.token import Token
from ..schemas.token import TokenOut

router = APIRouter(prefix="/tokens", tags=["tokens"])

# Get all tokens
@router.get("/", response_model=list[TokenOut])
def get_all_tokens(db: Session = Depends(get_db)):
    return db.query(Token).all()

# Get tokens by user
@router.get("/user/{user_id}", response_model=list[TokenOut])
def get_tokens_by_user(user_id: int, db: Session = Depends(get_db)):
    tokens = db.query(Token).filter(Token.users_id == user_id).all()
    if not tokens:
        raise HTTPException(status_code=404, detail="No tokens found for user")
    return tokens

# Get tokens by type (participation/winning)
@router.get("/user/{user_id}/type/{token_type}", response_model=list[TokenOut])
def get_tokens_by_user_and_type(user_id: int, token_type: str, db: Session = Depends(get_db)):
    if token_type not in ["participation", "winning"]:
        raise HTTPException(status_code=400, detail="Invalid token type")
    tokens = db.query(Token).filter(
        Token.users_id == user_id,
        Token.token_type == token_type
    ).all()
    if not tokens:
        raise HTTPException(status_code=404, detail=f"No {token_type} tokens found for user")
    return tokens
