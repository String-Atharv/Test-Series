from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.test_lifecycle.Evaluation import Evaluation
    from app.models.course_hierarchy.Questions import Questions

class QuestionEvaluation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "question_evaluations"

    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    marks_obtained: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    evaluation: Mapped["Evaluation"] = relationship(back_populates="question_evaluations")
    question: Mapped["Questions"] = relationship()

    __table_args__ = (
        UniqueConstraint("evaluation_id", "question_id", name="uq_evaluation_question"),
    )
