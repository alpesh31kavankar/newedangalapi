from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class CategoryVoteReason(Base):
    __tablename__ = "category_vote_reasons"

    id = Column(BigInteger, primary_key=True, index=True)
    categories_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )
    reason_key = Column(String(50), nullable=False)
    reason_label = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    category = relationship(
        "Category",
        back_populates="vote_reasons"
    )
