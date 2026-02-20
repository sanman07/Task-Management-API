import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BackendMain.main import app

client = TestClient(app)


def test_create_task_success():
    response = client.post("/tasks", json={
        "title": "Test Task",
        "priority": 3,
        "due_date": "2099-01-01"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_create_invalid_priority():
    response = client.post("/tasks", json={
        "title": "Bad Task",
        "priority": 10,
        "due_date": "2099-01-01"
    })
    assert response.status_code == 422
    assert response.json()["error"] == "Validation Failed"


def test_patch_partial_update():
    create = client.post("/tasks", json={
        "title": "Patch Me",
        "priority": 2,
        "due_date": "2099-01-01"
    })
    task_id = create.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={
        "priority": 5
    })

    assert response.status_code == 200
    assert response.json()["priority"] == 5


def test_filter_by_priority():
    response = client.get("/tasks?priority=5")
    assert response.status_code == 200


def test_delete_task():
    create = client.post("/tasks", json={
        "title": "Delete Me",
        "priority": 1,
        "due_date": "2099-01-01"
    })
    task_id = create.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200