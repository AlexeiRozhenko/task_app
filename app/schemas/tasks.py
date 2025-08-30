from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateTask(BaseModel):
    title: str = "Some task"
    content: str = Field(max_length=500)
    deadline: datetime
    is_done: bool = False


class FullUpdate(BaseModel):
    title: str
    content: str = Field(max_length=500)
    deadline: datetime
    is_done: bool


class PartialUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = Field(max_length=500)
    deadline: Optional[datetime] = None
    is_done: Optional[bool] = None


### Responses ###
class TaskResponse(BaseModel):
    id: int
    title: str
    content: str
    deadline: datetime
    is_done: bool
    created_at: datetime


class GeneralResponse(BaseModel):
    id: int
    message: str