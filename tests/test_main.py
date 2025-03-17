import pytest  # pip install pytest httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from main import app, tasks_manager, Response
from database import DB, Base

test_engine = create_engine(f'sqlite:///:memory:',
                            connect_args={"check_same_thread": False},
                            poolclass=StaticPool,
                            future=True)


def override_get_db_session():
    # переопределение зависимости DB для тестов
    with DB(test_engine) as test_db:
        yield test_db.session


@pytest.fixture(autouse=True)  # автовызов перед каждым тестом
def reset_db():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)


app.dependency_overrides[tasks_manager.get_db_session] = override_get_db_session  # type: ignore
# Переопределение зависимости для использования тестовой БД

client = TestClient(app)  # TestClient для взаимодействия с FastAPI приложением


def test_get_empty_tasks_list():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == Response(success=True, data=[]).dict()
    # Ожидаем пустой список задач


def test_post_task():
    task_data = {"title": "Test task", "description": "Test description"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 200
    assert response.json() == Response(success=True,
                                       message='New task added').dict()

    # Проверяем, что задача действительно добавилась
    get_tasks_response = client.get("/tasks")
    assert get_tasks_response.status_code == 200
    tasks = get_tasks_response.json()["data"]
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test task"
    assert tasks[0]["description"] == "Test description"
    assert tasks[0]["completed"] is False


def test_get_task_by_id():
    # Сначала создадим задачу, чтобы получить ее ID
    task_data = {"title": "Test task for get", "description": "Test description for get"}
    post_response = client.post("/tasks", json=task_data)
    assert post_response.status_code == 200

    get_tasks_response = client.get("/tasks")
    task_id = get_tasks_response.json()["data"][0]["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    task = response.json()["data"]
    assert task["id"] == task_id
    assert task["title"] == "Test task for get"
    assert task["description"] == "Test description for get"


def test_get_task_not_found():
    response = client.get("/tasks/999")  # ID заведомо не существующей задачи
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_task_full():
    # Создаем задачу
    task_data = {"title": "Task to update", "description": "Description to update"}
    post_response = client.post("/tasks", json=task_data)
    assert post_response.status_code == 200
    get_tasks_response = client.get("/tasks")
    task_id = get_tasks_response.json()["data"][0]["id"]

    # Обновляем задачу полностью
    update_data = {"title": "Updated task title", "description": "Updated description", "completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    assert response.json() == Response(success=True, message="Task updated").dict()

    # Проверяем, что задача обновилась
    get_task_response = client.get(f"/tasks/{task_id}")
    updated_task = get_task_response.json()["data"]
    assert updated_task["title"] == "Updated task title"
    assert updated_task["description"] == "Updated description"
    assert updated_task["completed"] is True


def test_update_task_partial():
    # Создаем задачу
    task_data = {"title": "Task to partially update", "description": "Description to partially update"}
    post_response = client.post("/tasks", json=task_data)
    assert post_response.status_code == 200
    get_tasks_response = client.get("/tasks")
    task_id = get_tasks_response.json()["data"][0]["id"]

    # Обновляем задачу частично (только title)
    update_data = {"title": "Partially updated title"}
    response = client.patch(f"/tasks/{task_id}/partial", json=update_data)
    assert response.status_code == 200
    assert response.json() == Response(success=True, message="Task updated").dict()

    # Проверяем, что задача обновилась частично
    get_task_response = client.get(f"/tasks/{task_id}")
    updated_task = get_task_response.json()["data"]
    assert updated_task["title"] == "Partially updated title"  # Title должен быть обновлен
    assert updated_task["description"] == "Description to partially update"  # Description должен остаться прежним


def test_delete_task():
    # Создаем задачу
    task_data = {"title": "Task to delete", "description": "Description to delete"}
    post_response = client.post("/tasks", json=task_data)
    assert post_response.status_code == 200
    get_tasks_response = client.get("/tasks")
    task_id = get_tasks_response.json()["data"][0]["id"]

    # Удаляем задачу
    delete_response = client.delete(f"/tasks/{task_id}/remove")
    assert delete_response.status_code == 200
    assert delete_response.json() == Response(success=True,
                                              message="Task deleted").dict()

    # Проверяем, что задача удалена и не находится
    get_task_response = client.get(f"/tasks/{task_id}")
    assert get_task_response.status_code == 404
    assert get_task_response.json() == {"detail": "Task not found"}


if __name__ == "__main__":
    pytest.main([__file__])  # Запуск тестов, если запустить этот файл напрямую
