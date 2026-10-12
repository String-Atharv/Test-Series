from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.common.enums import CACourses


class CourseCreateRequest(BaseModel):
    name: CACourses
    display_order: int


class CourseUpdateRequest(BaseModel):
    name: CACourses | None = None
    display_order: int | None = None


class CourseResponse(BaseModel):
    id: UUID
    name: CACourses
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
