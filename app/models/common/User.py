from app.models.common.enums import UserRole
from sqlalchemy import Enum, Boolean, true
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.common.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy.sql.sqltypes import String


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.test_lifecycle.Test import Test
    from app.models.test_lifecycle.TestAttempt import TestAttempt
    from app.models.test_lifecycle.Evaluation import Evaluation

class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum", native_enum=True), #user_role_enum is db level enum name , native_enum=true so db creates real ENUM type instead of varchar type of student,teacher,role
        default=UserRole.STUDENT,
        server_default=UserRole.STUDENT.name,
        nullable=False,
    )
    is_active:Mapped[bool]=mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default=true()   
    )

    created_tests: Mapped[list["Test"]] = relationship(
        secondary="test_creators",
        back_populates="created_by",
    )
    
    test_attempts: Mapped[list["TestAttempt"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="teacher",
    )