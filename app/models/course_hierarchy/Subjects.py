import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.course_hierarchy.CaCourses import CaCourses
    from app.models.course_hierarchy.Chapter import Chapter


class Subjects(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ca_courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationship: One Subject Belongs to One Course
    course: Mapped["CaCourses"] = relationship(
        back_populates="subjects",
    )

    #One subject has many chapters
    chapters:Mapped[list["Chapter"]]=relationship(
        back_populates="subject",
        cascade="all,delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("course_id", "display_order", name="uq_subject_course_display_order"),
        UniqueConstraint("course_id", "name", name="uq_subject_course_name"),
    )

    def __repr__(self) -> str:
        return f"<Subjects(name={self.name}, order={self.display_order})>"