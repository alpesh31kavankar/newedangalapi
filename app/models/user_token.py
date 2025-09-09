# app/models/user_token.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from app.database import Base

class UserToken(Base):
    __tablename__ = 'user_tokens'

    token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    draw_id = Column(Integer, ForeignKey("draws.draw_id", ondelete="CASCADE"))
    unlock_id = Column(Integer, ForeignKey("question_unlocks.unlock_id"))
    token_type = Column(String(20))  # 'participant' or 'winning'
    issued_at = Column(DateTime, server_default=func.now())
