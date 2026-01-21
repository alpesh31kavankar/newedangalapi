from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class QuestionRoundVoteReason(Base):
    __tablename__ = "question_round_vote_reasons"

    id = Column(BigInteger, primary_key=True)

    question_rounds_id = Column(
        BigInteger,
        ForeignKey("question_rounds.id", ondelete="CASCADE"),
        nullable=False
    )

    reason_id = Column(
        BigInteger,
        ForeignKey("category_vote_reasons.id", ondelete="RESTRICT"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "question_rounds_id",
            "reason_id",
            name="uq_question_round_reason"
        ),
    )

    # Optional but strongly recommended
    question_round = relationship("QuestionRound")
    reason = relationship("CategoryVoteReason")
