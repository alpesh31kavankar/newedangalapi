# from pydantic import BaseModel
# from typing import Optional

# class QuestionBase(BaseModel):
#     question_text: str

# class QuestionCreate(QuestionBase):
#     pass

# class QuestionUpdate(BaseModel):
#     question_text: Optional[str] = None

# class QuestionOut(QuestionBase):
#     question_id: int

#     class Config:
#         orm_mode = True


from pydantic import BaseModel

class QuestionBase(BaseModel):
    question_text: str

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
