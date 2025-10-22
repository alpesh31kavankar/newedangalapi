from sqlalchemy.orm import aliased
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.token import Token
from ..schemas.token import TokenOut
from ..models.user import User    
from ..routes.auth import get_current_user ,get_current_user_optional
from typing import Optional
from typing import List 
from ..models.question import Question 
from ..models.question_round import QuestionRound
from ..models.product import Product
from datetime import date
from sqlalchemy import cast, Date


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

@router.post("/claim/{token_id}", response_model=TokenOut)
def claim_token(
    token_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    token = db.query(Token).filter(
        Token.token_id == token_id,
        Token.users_id == current_user.id
    ).first()

    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    if token.source == "claim":
        raise HTTPException(status_code=400, detail="Token already claimed")

    if token.source != "round_win":
        raise HTTPException(status_code=400, detail="Only winning tokens can be claimed")

    # ✅ Mark as claimed
    token.source = "claim"
    db.commit()
    db.refresh(token)

    return token
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

@router.get("/participation")
def get_participation_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all participation (P) tokens for the logged-in user,
    along with question text from Questions.
    """
    today = date.today()
    tokens = (
        db.query(Token, QuestionRound, Question)
        .join(QuestionRound, Token.question_rounds_id == QuestionRound.id)
        .join(Question, QuestionRound.questions_id == Question.id)   # 👈 join questions table
        .filter(Token.users_id == current_user.id, Token.token_type == "P",cast(Token.created_at, Date) == today )
        .all()
    )

    result = []
    for token, question_round, question in tokens:
        result.append({
            "token_id": token.token_id,
            "question_rounds_id": token.question_rounds_id,
            "product_id": token.product_id,
            "question_text": question.question_text,   # 👈 now comes from Questions
            "created_at": token.created_at,
        })

    return result

@router.get("/winning")
def get_participation_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all today's W tokens for the logged-in user:
    - 'claim' tokens → linked to questions
    - 'C_referral_bonus' and 'C_referral' → referral tokens
    """
    today = date.today()

    # 1️⃣ Claim tokens (linked to questions)
    claim_tokens = (
        db.query(Token, QuestionRound, Question)
        .join(QuestionRound, Token.question_rounds_id == QuestionRound.id)
        .join(Question, QuestionRound.questions_id == Question.id)
        .filter(
            Token.users_id == current_user.id,
            Token.token_type == "W",
            Token.source == "claim",
            cast(Token.created_at, Date) == today
        )
        .all()
    )

    # Map claim tokens
    result = [
        {
            "token_id": token.token_id,
            "question_rounds_id": token.question_rounds_id,
            "product_id": token.product_id,
            "question_text": question.question_text,
            "created_at": token.created_at,
            "source": token.source
        }
        for token, question_round, question in claim_tokens
    ]

    # 2️⃣ Referral tokens (not linked to questions)
    referral_tokens = (
        db.query(Token)
        .filter(
            Token.users_id == current_user.id,
            Token.token_type == "W",
            Token.source.in_(["C_referral_bonus", "C_referral"]),
            cast(Token.created_at, Date) == today
        )
        .all()
    )

    # Map referral tokens
    result += [
        {
            "token_id": t.token_id,
            "question_rounds_id": None,
            "product_id": None,
            "question_text": None,
            "created_at": t.created_at,
            "source": t.source
        }
        for t in referral_tokens
    ]

        # 3️⃣ Daily Lucky Draw tokens (new addition)
    lucky_draw_tokens = (
        db.query(Token)
        .filter(
            Token.users_id == current_user.id,
            Token.token_type == "W",
            Token.source == "daily_lucky_draw",
            cast(Token.created_at, Date) == today
        )
        .all()
    )

    result += [
        {
            "token_id": t.token_id,
            "question_rounds_id": None,
            "product_id": None,
            "question_text": None,
            "created_at": t.created_at,
            "source": t.source
        }
        for t in lucky_draw_tokens
    ]

    return result

@router.get("/verify/{token_id}")
def verify_ticket(
    token_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)  # Optional user
):
    # 🔍 Find token by ID (any token, not restricted to user)
    token = db.query(Token).filter(Token.token_id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    # Get token owner
    user = db.query(User).filter(User.id == token.users_id).first()

    # Determine ownership
    is_owner = current_user.id == token.users_id if current_user else False

    # Helper for formatting datetime
    def format_dt(dt) -> Optional[str]:
        return dt.strftime("%Y-%m-%d %H:%M") if dt else None

    # Determine claimed_at based on source rules
    claimed_at = None
    if token.source in ["vote", "daily_lucky_draw", "C_referral", "claim", "C_referral_bonus"]:
        claimed_at = format_dt(token.created_at)

    # Prepare result object
    result = {
        "ticket_number": token.token_id,
        "issued_to": user.username if user else "Unknown User",
        "created_at": format_dt(token.created_at),
        "claimed_at": claimed_at,
        "ticket_type": "Winning" if token.token_type == "W" else "Participation",
        "source": None,
        "lucky_draw_result": None,
        "product_battle_details": None,
        "is_owner": is_owner
    }

    # Source classification
    if token.source in ["vote", "round_win", "claim"]:
        result["source"] = "Product Battle"
        if token.source == "round_win" and not claimed_at:
            # Not yet claimed
            result["claimed_at"] = None
        elif token.source == "claim":
            result["claimed_at"] = format_dt(token.created_at)

        # Add product battle info if relevant
        Product1 = aliased(Product)
        Product2 = aliased(Product)
        round_data = (
            db.query(QuestionRound, Question, Product1, Product2)
            .join(Question, QuestionRound.questions_id == Question.id)
            .join(Product1, QuestionRound.product1_id == Product1.id)
            .join(Product2, QuestionRound.product2_id == Product2.id)
            .filter(QuestionRound.id == token.question_rounds_id)
            .first()
        )
        if round_data:
            qr, question, p1, p2 = round_data
            winner_product = db.query(Product).filter(Product.id == qr.winner_product_id).first()
            result["product_battle_details"] = {
                "question": question.question_text,
                "products": f"{p1.name} vs {p2.name}",
                "winner": winner_product.name if winner_product else None,
                "date": format_dt(qr.created_at)
            }

    elif token.source in ["daily_lucky_draw"]:
        result["source"] = "Daily Lucky Draw"
        result["lucky_draw_result"] = "🏆 Won"

    elif token.source in ["C_referral", "C_referral_bonus", "referral_bonus"]:
        result["source"] = "Referral"
        if token.source in ["C_referral", "C_referral_bonus"]:
            result["lucky_draw_result"] = "🏆 Referral Reward"
        else:  # referral_bonus not claimed yet
            result["lucky_draw_result"] = "Pending"

    return result