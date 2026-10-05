
import uuid
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.course_hierarchy.Chapter import Chapter
    from app.models.course_hierarchy.Questions import Questions

class Topics(Base,UUIDPrimaryKeyMixin,TimestampMixin):
    __tablename__="topics"
    name:Mapped[str]=mapped_column(
        String(50),
        nullable=False,
    )
    display_order:Mapped[int]=mapped_column(
        Integer,
        nullable=False,
    )

    chapter_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id",ondelete="CASCADE"),
        nullable=False,
    )
    
    #one topic belong to one chapter
    chapter:Mapped["Chapter"]=relationship(
        back_populates="topics",
    )

    #one topic has many questions
    questions:Mapped[list["Questions"]]=relationship(
        back_populates="topics",
        secondary="questions_topics",
    )
    __table_args__ = (
        UniqueConstraint("chapter_id", "display_order", name="uq_topic_chapter_display_order"),
        UniqueConstraint("chapter_id", "name", name="uq_topic_chapter_name"),
    )
    
    def __repr__(self) -> str:
        return f"<Topics(name={self.name},order={self.display_order},chapter_id={self.chapter_id}>"