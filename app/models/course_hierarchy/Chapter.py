from sqlalchemy import UniqueConstraint
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.common.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.course_hierarchy.Subjects import Subjects
    from app.models.course_hierarchy.Topics import Topics
    

class Chapter(Base,UUIDPrimaryKeyMixin,TimestampMixin):
    __tablename__="chapters"
    name:Mapped[str]=mapped_column(
        String(50),
        nullable=False,
    )
    display_order:Mapped[int]=mapped_column(
        Integer,
        nullable=False,
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )

    #one chapter belongs to one subject
    subject:Mapped["Subjects"]=relationship(
        back_populates="chapters",
    )

    #one chapter has many topics    
    topics:Mapped[list["Topics"]]=relationship(
        back_populates="chapter",
        cascade="all,delete-orphan",
        order_by="Topics.display_order"
    )
    __table_args__=(
        UniqueConstraint("subject_id","name",name="uq_chapter_subject_name"),
        UniqueConstraint("subject_id","display_order",name="uq_chapter_subject_display_order"),
    )
    def __repr__(self) -> str:
        return f"<Chapter(name={self.name},order={self.display_order})>"