from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.common.base import Base

questions_topics=Table(
    "questions_topics",
    Base.metadata,
    Column(
        "question_id",
        UUID(as_uuid=True),
        ForeignKey("questions.id",ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "topic_id",
        UUID(as_uuid=True),
        ForeignKey("topics.id",ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    )
)