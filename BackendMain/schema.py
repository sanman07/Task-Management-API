from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    priority: int = Field(..., ge=1, le=5)
    due_date: date
    tags: Optional[List[str]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[date] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    due_date: date
    completed: bool
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)