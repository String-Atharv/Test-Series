import uuid
from typing import Any
from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.common.base import TimestampMixin, UUIDPrimaryKeyMixin, Base
from app.models.common.enums import QuestionType, Difficulty, QuestionStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.course_hierarchy.Topics import Topics
    from app.models.test_lifecycle.Test import Test
    

class Questions(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "questions"

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, name="question_type_enum", native_enum=True),
        nullable=False,
    )
    model_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    correct_answer: Mapped[Any | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    difficulty:Mapped[Difficulty]=mapped_column(
        Enum(Difficulty,name="difficulty_enum",native_enum=True),
        nullable=False,
    )

    status:Mapped[QuestionStatus]=mapped_column(
        Enum(QuestionStatus,name="question_status_enum",native_enum=True),
        nullable=False,
        default=QuestionStatus.DRAFT,
        server_default=QuestionStatus.DRAFT.name,
    )

    #one question has many topics
    topics:Mapped[list["Topics"]]=relationship(
        back_populates="questions",
        secondary="questions_topics",
    )

    #one question can be in many tests
    tests:Mapped[list["Test"]]=relationship(
        back_populates="questions",
        secondary="test_questions",
        order_by="test_questions.c.question_order",
    )
