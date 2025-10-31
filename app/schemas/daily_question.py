from pydantic import BaseModel
from datetime import datetime

class DailyQuestionOut(BaseModel):
    id: int
    randamqty_id: int
    randamqty_text: str
    start_date: datetime

    class Config:
        orm_mode = True
