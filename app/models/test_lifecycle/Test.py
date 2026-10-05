from app.models.course_hierarchy import Questions
from datetime import datetime, timedelta
from app.models.common.enums import TestStatus
from sqlalchemy import Enum, Numeric, DateTime, Interval, text
from app.models.common.enums import TestType
from app.models.common.base import TimestampMixin, UUIDPrimaryKeyMixin, Base
from sqlalchemy import String, Integer, ForeignKey, true, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.common.User import User
    from app.models.test_lifecycle.TestAttempt import TestAttempt
    from app.models.test_lifecycle.QuestionPaper import QuestionPaper

test_creators_table = Table(
    "test_creators",
    Base.metadata,
    Column("test_id", ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

test_questions_table=Table(
    "test_questions",
    Base.metadata,
    Column("question_id",ForeignKey("questions.id",ondelete="CASCADE"),primary_key=True),
    Column("test_id",ForeignKey("tests.id",ondelete="CASCADE"),primary_key=True),
    Column("question_order",Integer,nullable=False,index=True),
)

class Test(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__="tests"
    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
    )
    price:Mapped[float]=mapped_column(
        Numeric(10,2)
    )
    type:Mapped[TestType]=mapped_column(
        Enum(TestType, name="test_type_enum", native_enum=True),
        nullable=False,
    )
    status:Mapped[TestStatus]=mapped_column(
        Enum(TestStatus,name="test_status_enum",native_enum=True),
        nullable=False,
        default=TestStatus.DRAFT,
    )
    max_attempts:Mapped[int]=mapped_column(
        Integer,
        nullable=False,
        default=2,
        server_default="2",
    )
    max_upload_replacement:Mapped[int]=mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default="3",
    )
    replacement_window:Mapped[timedelta]=mapped_column(
        Interval,
        nullable=False,
        default=timedelta(hours=6),
        server_default=text("'6 hours'"),
    )
    submission_window_deadline:Mapped[timedelta]=mapped_column(
        Interval,
        nullable=False,
        default=timedelta(days=365),
        server_default=text("'12 months'"),
    )

    created_by: Mapped[list["User"]] = relationship(
        secondary="test_creators",
        back_populates="created_tests",
    )

    questions:Mapped[list[Questions]]=relationship(
        secondary="test_questions",
        back_populates="tests",
        order_by="test_questions.c.question_order",
    )
    
    attempts: Mapped[list["TestAttempt"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
    )

    question_paper: Mapped["QuestionPaper"] = relationship(
        back_populates="test",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Test(name={self.name},type={self.type})"