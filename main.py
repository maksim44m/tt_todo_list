from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union, Any
from pydantic import BaseModel, field_validator, model_validator

from fastapi import FastAPI, HTTPException, Depends  # pip install fastapi uvicorn
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from database import DB, TaskModel


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

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


class TaskManager:

    def __init__(self):
        self.db_url = (Path(__file__).resolve().parent /
                       'data' / 'database' / 'data.db')
        self.engine = create_engine(f'sqlite:///{self.db_url}',
                                    future=True)

    def get_db_session(self):
        with DB(self.engine) as db:
            yield db.session

    @staticmethod
    def post_tasks(db_session: Session, task: TaskCreate) -> Response:
        new_task = TaskModel(**task.dict(exclude_unset=True))
        db_session.add(new_task)
        return Response(success=True, message='New task added')

    @staticmethod
    def get_tasks(db_session: Session, task_id: int = None) -> Response:
        if task_id:
            task_db = db_session.get(TaskModel, task_id)
            if not task_db:
                raise HTTPException(status_code=404, detail="Task not found")
            task = Task.from_orm(task_db)
            return Response(success=True, data=task)
        else:
            tasks_db = db_session.query(TaskModel).all()
            tasks = [Task.from_orm(task) for task in tasks_db]
            return Response(success=True, data=tasks)

    @staticmethod
    def update_task(db_session: Session, task_id: int,
                    data: Union[TaskCreate, TaskUpdate]) -> Response:
        upd_task = db_session.get(TaskModel, task_id)
        if not upd_task:
            raise HTTPException(status_code=404, detail='Task not found')

        data_dict = data.dict(exclude_unset=True)
        if 'completed' in data_dict and data_dict['completed'] is None:
            data_dict.pop('completed')  # удаление если передан None, по логике должен быть True/False

        for key, value in data_dict.items():
            setattr(upd_task, key, value)

        return Response(success=True, message='Task updated')

    @staticmethod
    def delete_task(db_session: Session, task_id: int) -> Response:
        del_task = db_session.get(TaskModel, task_id)
        if del_task:
            db_session.delete(del_task)
        else:
            raise HTTPException(status_code=404, detail='Task not found')

        return Response(success=True, message='Task deleted')


app = FastAPI()
tasks_manager = TaskManager()


@app.post(path='/tasks',
          response_model=Response,
          tags=['Task manager'],
          summary='Add tasks')
def post_tasks(data: TaskCreate,
               db_session: Session = Depends(tasks_manager.get_db_session)):
    return tasks_manager.post_tasks(db_session, data)


@app.get(path="/tasks",
         response_model=Response,
         tags=['Task manager'],
         summary='Get tasks')
def get_tasks(db_session: Session = Depends(tasks_manager.get_db_session)):
    return tasks_manager.get_tasks(db_session)


@app.get(path='/tasks/{task_id}',
         response_model=Response,
         tags=['Task manager'],
         summary='Get task by id')
def get_task(task_id: int,
             db_session: Session = Depends(tasks_manager.get_db_session)):
    return tasks_manager.get_tasks(db_session, task_id)


@app.put(path='/tasks/{task_id}',
         response_model=Response,
         tags=['Task manager'],
         summary='Update task full')
def update_task_full(task_id: int, data: TaskCreate,
                     db_session: Session = Depends(tasks_manager.get_db_session)):
    return tasks_manager.update_task(db_session, task_id, data)


@app.patch(path='/tasks/{task_id}/partial',
           response_model=Response,
           tags=['Task manager'],
           summary='Update task partially')
def update_task_part(task_id: int, data: TaskUpdate,
                     db_session: Session = Depends(tasks_manager.get_db_session)):
    return tasks_manager.update_task(db_session, task_id, data)


@app.delete(path='/tasks/{task_id}/remove',
            response_model=Response,
            tags=['Task manager'],
            summary='Delete task')
def delete_task(task_id: int,
                db_session: Session = Depends(tasks_manager.get_db_session)):
    return tasks_manager.delete_task(db_session, task_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)  # uvicorn main:app --reload
