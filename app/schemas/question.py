

from pydantic import BaseModel

class QuestionBase(BaseModel):
    question_text: str
    category_id: int

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
