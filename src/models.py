from sqlalchemy import Column, Integer, String, DateTime, Enum as SqlEnum
from datetime import datetime
from enum import Enum
from database import Base


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, nullable=True)
    status = Column(SqlEnum(TaskStatus), default=TaskStatus.PENDING)
    