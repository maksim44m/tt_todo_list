from typing import Union

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import DB, TaskModel
from utils.models import Task, TaskCreate, TaskUpdate, Response
from config import sqlite_url


class TaskManager:
    def __init__(self):
        self.engine = create_engine(sqlite_url, future=True)

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