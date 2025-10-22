from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..database import SessionLocal
from ..models.question_round import QuestionRound
from ..models.vote import Vote
from ..models.token import Token
import pytz

# Finalization active hour (after 8 PM IST)
FINALIZE_HOUR = 18 # 8 PM IST

def generate_token_id_next(token_type: str, last_seq: int) -> tuple[str, int]:
    """Generate next token id based on last sequence."""
    today_str = datetime.utcnow().strftime("%Y%m%d")
    next_seq = last_seq + 1
    return f"{token_type}{today_str}{next_seq:04d}", next_seq

def finalize_rounds():
    db: Session = SessionLocal()
    finalized_count = 0

    try:
        # Current IST time
        now_utc = datetime.now(timezone.utc)
        ist = pytz.timezone("Asia/Kolkata")
        now_local = now_utc.astimezone(ist)

        # Only run after FINALIZE_HOUR
        if now_local.hour < FINALIZE_HOUR:
            print(f"⏰ Not time to finalize rounds yet ({now_local.hour} < {FINALIZE_HOUR})")
            return

        # Get all rounds not locked yet
        rounds = db.query(QuestionRound).filter(QuestionRound.is_locked == False).all()
        if not rounds:
            print("✅ No unlocked rounds to finalize")
            return

        # Get last W token seq for today
        last_token = (
            db.query(Token)
            .filter(Token.token_type == 'W')
            .filter(Token.token_id.like("W" + datetime.utcnow().strftime("%Y%m%d") + "%"))
            .order_by(Token.token_id.desc())
            .first()
        )
        last_seq = int(last_token.token_id[-4:]) if last_token else 0

        for r in rounds:
            # Count votes
            votes_p1 = db.query(func.count(Vote.id)).filter(
                Vote.question_rounds_id == r.id,
                Vote.products_id == r.product1_id
            ).scalar()
            votes_p2 = db.query(func.count(Vote.id)).filter(
                Vote.question_rounds_id == r.id,
                Vote.products_id == r.product2_id
            ).scalar()
            total_votes = votes_p1 + votes_p2

            # Lock round
            r.is_locked = True
            if votes_p1 > votes_p2:
                r.winner_product_id = r.product1_id
            elif votes_p2 > votes_p1:
                r.winner_product_id = r.product2_id
            else:
                r.is_draw = True

            # Issue winning tokens if not a draw
            if not r.is_draw and r.winner_product_id:
                winning_votes = db.query(Vote).filter(
                    Vote.question_rounds_id == r.id,
                    Vote.products_id == r.winner_product_id
                ).all()
                for v in winning_votes:
                    exists = db.query(Token).filter(
                        Token.users_id == v.users_id,
                        Token.question_rounds_id == r.id,
                        Token.token_type == 'W'
                    ).first()
                    if not exists:
                        token_id, last_seq = generate_token_id_next('W', last_seq)
                        token = Token(
                            token_id=token_id,
                            users_id=v.users_id,
                            question_rounds_id=r.id,
                            product_id=v.products_id,
                            token_type='W',
                            source='round_win'
                        )
                        db.add(token)

            finalized_count += 1

        db.commit()
        print(f"✅ Finalized {finalized_count} rounds")

    except Exception as e:
        db.rollback()
        print(f"❌ Error finalizing rounds: {e}")
        raise
    finally:
        db.close()
