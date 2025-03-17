from datetime import datetime
from typing import List, Optional, Union, Any

from pydantic import BaseModel, field_validator, model_validator


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True  # извлечение данных из объектов
        from_attributes = True  # то же самое для Pydantic v2

    # @field_validator('completed', mode='before')
    # def convert_empty_completed(cls, v: Any):
    #     return v if v else False
    #
    # @model_validator(mode='before')
    # def convert_empty_created_at(cls, values: Any):
    #     created_at = values.get('created_at', None)
    #     if isinstance(created_at, str) and created_at.strip() == "":
    #         values['created_at'] = None
    #
    #     description = values.get('description', None)
    #     if isinstance(description, str) and description.strip() == "":
    #         values['description'] = None
    #     return values


class TaskUpdate(TaskCreate):
    title: Optional[str] = None
    completed: Optional[bool] = None
    created_at: Optional[datetime] = None


class Task(TaskCreate):
    id: int


class Response(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Union[Task, List[Task]]] = None