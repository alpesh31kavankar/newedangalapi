from pydantic import BaseModel
from datetime import datetime

class LockedRoundOut(BaseModel):
    question_round_id: int
    category_image: str
    question_text: str
    product1_name: str
    product1_image: str
    product2_name: str
    product2_image: str
    participant_count: int
    max_votes: int
    is_locked: bool
    is_winner: bool = False       # whether current user won
    user_token_id: str | None = None
    winning_token_id: str | None   # user participation token id
    token_claimed: bool = False

    class Config:
        orm_mode = True
