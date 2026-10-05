from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.test_lifecycle.Test import Test

class QuestionPaper(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "question_papers"

    test_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")

    test: Mapped["Test"] = relationship(back_populates="question_paper")
