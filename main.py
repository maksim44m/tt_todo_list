from typing import List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException  # pip install fastapi uvicorn


class TaskCreate(BaseModel):
    title: str
    description:  Optional[str] = None


class Tasks(TaskCreate):
    id: int
    completed: bool = False


class TaskManager:
    def __init__(self):
        self.id = 0
        self.tasks: List[Tasks] = []

    def get_tasks(self):
        return self.tasks

    def get_task(self, task_id: int):
        task = [t for t in self.tasks if t.id == task_id][0]
        if task:
            return task
        else:
            raise HTTPException(status_code=404, detail='Task not found')

    def post_tasks(self, task: TaskCreate):
        self.id += 1
        new_task = Tasks(id=self.id, **task.dict())
        self.tasks.append(new_task)
        return new_task


app = FastAPI()
tasks_manager = TaskManager()


@app.get(path="/tasks",
         response_model=List[Tasks],
         tags=['Get tasks'])
def get_tasks():
    return tasks_manager.get_tasks()


@app.get(path='/tasks/{task_id}',
         response_model=Tasks,
         tags=['Get task by id'])
def get_task(task_id: int):
    return tasks_manager.get_task(task_id)


@app.post(path='/tasks',
          response_model=Tasks,
          tags=['Add tasks'])
def post_tasks(task: TaskCreate):
    return tasks_manager.post_tasks(task)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)  # uvicorn main:app --reload
