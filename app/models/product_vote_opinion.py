from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
    DateTime,
    func
)
from ..database import Base


class ProductVoteOpinion(Base):
    __tablename__ = "product_vote_opinions"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(BigInteger, nullable=False)
    question_round_id = Column(BigInteger, ForeignKey("question_rounds.id"), nullable=False)

    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)

    selected_product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    opposite_product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)

    reason_id = Column(BigInteger, ForeignKey("category_vote_reasons.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "question_round_id", name="uniq_user_round"),
    )
