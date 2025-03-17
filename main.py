from fastapi import FastAPI, Depends  # pip install fastapi uvicorn
from sqlalchemy.orm import Session

from utils import TaskManager, TaskCreate, TaskUpdate, Response

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
