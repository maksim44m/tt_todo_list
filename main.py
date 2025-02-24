from typing import List, Optional, Union
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException  # pip install fastapi uvicorn


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskUpdate(TaskCreate):
    title: Optional[str] = None
    completed: Optional[bool] = None


class Task(TaskCreate):
    id: int


class Response(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Union[Task, List[Task]]] = None


class TaskManager:
    def __init__(self):
        self.id = 0
        self.tasks: List[Task] = []

    def get_tasks(self, task_id: int = None) -> Response:
        if task_id:
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                return Response(success=True, data=task)
            else:
                raise HTTPException(status_code=404, detail='Task not found')
        else:
            return Response(success=True, data=self.tasks)

    def post_tasks(self, task: TaskCreate) -> Response:
        self.id += 1
        new_task = Task(id=self.id, **task.dict())
        self.tasks.append(new_task)
        return Response(success=True, message='New task added')

    def update_task(self, task_id: int, data: Union[TaskCreate, TaskUpdate]) -> Response:
        upd_task = next((t for t in self.tasks if t.id == task_id), None)
        if not upd_task:
            raise HTTPException(status_code=404, detail='Task not found')

        data_dict = data.dict(exclude_unset=True)
        if 'completed' in data_dict and data_dict['completed'] is None:
            data_dict.pop('completed')  # удаление если передан None, по логике должен быть True/False

        for key, value in data_dict.items():
            setattr(upd_task, key, value)

        return Response(success=True, message='Task updated')

    def delete_task(self, task_id: int) -> Response:
        del_task = next((t for t in self.tasks if t.id == task_id), None)
        if not del_task:
            raise HTTPException(status_code=404, detail='Task not found')
        self.tasks.remove(del_task)
        return Response(success=True, message='Task deleted')


app = FastAPI()
tasks_manager = TaskManager()


@app.get(path="/tasks",
         response_model=Response,
         tags=['Task manager'],
         summary='Get tasks')
def get_tasks():
    return tasks_manager.get_tasks()


@app.get(path='/tasks/{task_id}',
         response_model=Response,
         tags=['Task manager'],
         summary='Get task by id')
def get_task(task_id: int):
    return tasks_manager.get_tasks(task_id)


@app.post(path='/tasks',
          response_model=Response,
          tags=['Task manager'],
          summary='Add tasks')
def post_tasks(data: TaskCreate):
    return tasks_manager.post_tasks(data)


@app.put(path='/tasks/{task_id}',
         response_model=Response,
         tags=['Task manager'],
         summary='Update task in full')
def update_task_full(task_id: int, data: TaskCreate):
    return tasks_manager.update_task(task_id, data)


@app.patch(path='/tasks/{task_id}',
           response_model=Response,
           tags=['Task manager'],
           summary='Update task partially')
def update_task_part(task_id: int, data: TaskUpdate):
    return tasks_manager.update_task(task_id, data)


@app.delete(path='/tasks/{task_id}',
            response_model=Response,
            tags=['Task manager'],
            summary='Delete task')
def delete_task(task_id: int):
    return tasks_manager.delete_task(task_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)  # uvicorn main:app --reload
