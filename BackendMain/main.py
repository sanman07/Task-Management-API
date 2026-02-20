from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from BackendMain.database import Base, engine, get_db
from BackendMain.models import Task, Tag
from BackendMain.schema import TaskCreate, TaskUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = {}
    for err in exc.errors():
        field = err["loc"][-1]
        errors[field] = err["msg"]

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Failed",
            "details": errors,
        },
    )



@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    if task.due_date < date.today():
        raise HTTPException(
            status_code=400,
            detail={"error": "Validation Failed",
                    "details": {"due_date": "Cannot be in the past"}}
        )

    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
    )

    if task.tags:
        for tag_name in task.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            db_task.tags.append(tag)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return {
        **db_task.__dict__,
        "tags": [t.name for t in db_task.tags]
    }



@app.get("/tasks")
def get_tasks(
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    tags: Optional[str] = Query(None),
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):

    query = db.query(Task).filter(Task.is_deleted == False)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    if priority:
        query = query.filter(Task.priority == priority)

    if tags:
        tag_list = tags.split(",")
        query = query.join(Task.tags).filter(Tag.name.in_(tag_list))

    total = query.distinct().count()
    tasks = query.distinct().offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": [
            {**t.__dict__, "tags": [tag.name for tag in t.tags]}
            for t in tasks
        ],
    }


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {**task.__dict__, "tags": [t.name for t in task.tags]}


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, updates: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data = updates.model_dump(exclude_unset=True)

    if "due_date" in data and data["due_date"] < date.today():
        raise HTTPException(
            status_code=400,
            detail={"error": "Validation Failed",
                    "details": {"due_date": "Cannot be in the past"}}
        )

    for key, value in data.items():
        if key != "tags":
            setattr(task, key, value)

    if "tags" in data:
        task.tags.clear()
        for tag_name in data["tags"]:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            task.tags.append(tag)

    db.commit()
    db.refresh(task)

    return {**task.__dict__, "tags": [t.name for t in task.tags]}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_deleted = True
    db.commit()

    return {"message": "Task deleted successfully"}