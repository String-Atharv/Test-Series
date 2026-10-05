from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.models.common.enums import TestAttemptStatus

if TYPE_CHECKING:
    from app.models.test_lifecycle.Test import Test
    from app.models.common.User import User
    from app.models.test_lifecycle.Submission import Submission

class TestAttempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "test_attempts"

    test_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    status: Mapped[TestAttemptStatus] = mapped_column(
        Enum(TestAttemptStatus, name="test_attempt_status_enum", native_enum=True),
        nullable=False,
        default=TestAttemptStatus.IN_PROGRESS,
    )
    question_paper_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    answer_submission_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    replacement_deadline_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    submission_replacement_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    test: Mapped["Test"] = relationship(back_populates="attempts")
    student: Mapped["User"] = relationship(back_populates="test_attempts")
    submission: Mapped["Submission"] = relationship(
        back_populates="test_attempt",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("test_id", "student_id", "attempt_number", name="uq_test_student_attempt"),
    )
