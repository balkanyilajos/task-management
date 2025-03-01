import pandas as pd

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Task, TaskStatus
from suggestion import suggest_similar_tasks


app = FastAPI()

@app.post("/tasks/")
def create_task(title: str, description: str, due_date: datetime, db: Session = Depends(get_db)):
    task = Task(title=title, description=description, due_date=due_date)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@app.get("/tasks/")
def get_tasks(status: TaskStatus = None, sort_by: str = "created_at", order: str = "asc", db: Session = Depends(get_db)):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    
    columns = { "created_at", "due_date" }

    if sort_by not in columns:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if sort_by in columns:
        if order == "desc":
            query = query.order_by(getattr(Task, sort_by).desc())
        else:
            query = query.order_by(getattr(Task, sort_by).asc())

    return query.all()


@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str = None, description: str = None, status: TaskStatus = None, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if title:       task.title = title
    if description: task.description = description
    if status:      task.status = status

    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}


@app.get("/tasks/suggestions/")
def suggest_tasks(target_title: str = None, target_description: str = None, top_n: int = 5, status_filter: TaskStatus = None, db: Session = Depends(get_db)):
    tasks = db.query(Task)
    
    if status_filter:
        tasks = tasks.filter(Task.status == status_filter)

    tasks_df = pd.read_sql(tasks.statement, db.bind)
    suggested_tasks = suggest_similar_tasks(tasks_df, Task(title=target_title, description=target_description), top_n)

    return {"message": suggested_tasks }
