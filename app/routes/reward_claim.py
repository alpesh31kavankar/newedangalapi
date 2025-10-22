from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.reward_claim import RewardClaim
from ..models.lottery import Lottery
from ..models.gift import Gift
from ..schemas.reward_claim import RewardClaimRequest, RewardClaimResponse
from ..models.participant_lottery import ParticipantLottery
from ..models.p_gift import PGift

router = APIRouter(prefix="/reward", tags=["Reward Claims"])


# Fetch gift details for a lottery
@router.get("/claim-details")
def get_claim_details(
    lottery_id: int,
    type: str = Query("winning"),
    db: Session = Depends(get_db)
):
    if type == "winning":
        lottery = db.query(Lottery).filter(Lottery.id == lottery_id).first()
        if not lottery:
            raise HTTPException(status_code=404, detail="Winning lottery not found")
        gift = db.query(Gift).filter(Gift.id == lottery.gifts_id).first() if lottery.gifts_id else None

    elif type == "participant":
        lottery = db.query(ParticipantLottery).filter(ParticipantLottery.id == lottery_id).first()
        if not lottery:
            raise HTTPException(status_code=404, detail="Participant lottery not found")
        gift = db.query(PGift).filter(PGift.id == lottery.p_gifts_id).first() if lottery.p_gifts_id else None

    else:
        raise HTTPException(status_code=400, detail="Invalid type")

    return {"lottery": lottery, "gift": gift}


# Submit a reward claim (winning / participant)
@router.post("/submit-claim", response_model=RewardClaimResponse)
def submit_claim(request: RewardClaimRequest, db: Session = Depends(get_db)):
    # Check if already claimed
    existing = db.query(RewardClaim).filter(
        RewardClaim.user_id == request.user_id,
        RewardClaim.lottery_id == request.lottery_id,
        RewardClaim.claim_type == request.claim_type
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"{request.claim_type.capitalize()} reward already claimed"
        )

    # Insert new claim
    claim = RewardClaim(
        user_id=request.user_id,
        lottery_id=request.lottery_id,
        gift_id=request.gift_id,
        postal_code=request.postal_code,
        contact_no=request.contact_no,
        address=request.address,
        claim_type=request.claim_type
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    return {"message": f"{request.claim_type.capitalize()} claim submitted successfully"}

@router.get("/check-claim")
def check_claim(user_id: int, lottery_id: int, claim_type: str, db: Session = Depends(get_db)):
    existing = db.query(RewardClaim).filter(
        RewardClaim.user_id == user_id,
        RewardClaim.lottery_id == lottery_id,
        RewardClaim.claim_type == claim_type
    ).first()

    if existing:
        return {"already_claimed": True, "message": f"{claim_type.capitalize()} reward already claimed"}
    return {"already_claimed": False}

@router.get("/my-gifts")
def get_my_gifts(user_id: int, db: Session = Depends(get_db)):
    claims = db.query(RewardClaim).filter(RewardClaim.user_id == user_id).all()  # <- filter by user_id

    results = []
    for c in claims:
        if c.claim_type == "winning":
            lottery = db.query(Lottery).filter(Lottery.id == c.lottery_id).first()
            gift = db.query(Gift).filter(Gift.id == c.gift_id).first()
        else:
            lottery = db.query(ParticipantLottery).filter(ParticipantLottery.id == c.lottery_id).first()
            gift = db.query(PGift).filter(PGift.id == c.gift_id).first()

        results.append({
            "claim_id": c.id,
            "claim_type": c.claim_type,
            "is_claimed": c.is_claimed,
            "lottery_id": c.lottery_id,
            "lottery_name": getattr(lottery, "name", None),
            "gift_name": getattr(gift, "name", None),
            "gift_image": getattr(gift, "image_url", None),
            "claimed_at": c.created_at,
        })

    return results


