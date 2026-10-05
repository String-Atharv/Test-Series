from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, DateTime, Text, Enum
from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from app.models.common.enums import EvaluationStatus

if TYPE_CHECKING:
    from app.models.test_lifecycle.Submission import Submission
    from app.models.common.User import User
    from app.models.test_lifecycle.QuestionEvaluation import QuestionEvaluation

class Evaluation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "evaluations"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    evaluation_status: Mapped[EvaluationStatus] = mapped_column(
        Enum(EvaluationStatus, name="evaluation_status_enum", native_enum=True),
        nullable=False,
        default=EvaluationStatus.PENDING,
    )
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    overall_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    checked_storage_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    checked_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    checked_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checked_file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    checked_file_uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    submission: Mapped["Submission"] = relationship(back_populates="evaluation")
    teacher: Mapped["User"] = relationship(back_populates="evaluations")
    question_evaluations: Mapped[list["QuestionEvaluation"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )
