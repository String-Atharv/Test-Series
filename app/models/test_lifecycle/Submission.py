from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, DateTime
from typing import TYPE_CHECKING
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from app.models.test_lifecycle.TestAttempt import TestAttempt
    from app.models.test_lifecycle.Evaluation import Evaluation

class Submission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "submissions"

    test_attempt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("test_attempts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    test_attempt: Mapped["TestAttempt"] = relationship(back_populates="submission")
    evaluation: Mapped["Evaluation"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
