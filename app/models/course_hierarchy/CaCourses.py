from typing import TYPE_CHECKING
from sqlalchemy import Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.models.common.enums import CACourses

if TYPE_CHECKING:
    from app.models.course_hierarchy.Subjects import Subjects


class CaCourses(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ca_courses"

    name: Mapped[CACourses] = mapped_column(
        Enum(CACourses, name="ca_courses_enum", native_enum=True),
        nullable=False,
        unique=True,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
    )
    # Relationship: One Course has Many Subjects
    subjects: Mapped[list["Subjects"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CACourse(name={self.name.value}, order={self.display_order})>"