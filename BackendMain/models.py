from sqlalchemy import (
    Column, Integer, String, Boolean, Date,
    Table, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from BackendMain.database import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String)
    priority = Column(Integer, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    completed = Column(Boolean, default=False, index=True)
    is_deleted = Column(Boolean, default=False, index=True)

    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")

    __table_args__ = (
        Index("idx_priority_completed", "priority", "completed"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)

    tasks = relationship("Task", secondary=task_tags, back_populates="tags")