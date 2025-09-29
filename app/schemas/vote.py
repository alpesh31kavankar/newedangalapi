from pydantic import BaseModel

class VoteBase(BaseModel):
    users_id: int
    question_rounds_id: int
    products_id: int

class VoteCreate(VoteBase):
    pass

class VoteOut(VoteBase):
    id: int
    created_at: str

    class Config:
        orm_mode = True
