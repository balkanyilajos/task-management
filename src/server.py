from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from collections import Counter, defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from enum import Enum
from datetime import datetime


# --------- Database Setup ---------

SQLALCHEMY_DATABASE_URL = "sqlite:///tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ------------- Models -------------

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, nullable=True)
    status = Column(SqlEnum(TaskStatus), default=TaskStatus.PENDING)


Base.metadata.create_all(bind=engine)


# ---------- API Endpoints ----------

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
        
    if sort_by == "created_at" or sort_by == "due_date":
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
def suggest_tasks(db: Session = Depends(get_db), task_title: str = None, limit: int = 5, mode: str = "frequency", status_filter: TaskStatus = None):
    tasks = db.query(Task)
    
    if status_filter:
        tasks = tasks.filter(Task.status == status_filter)
    else:
        tasks = tasks.all()


    if mode == "frequency":
        return generate_title_description_suggestions(compute_similarity(tasks), task_title, limit)
    
    if mode == "sequence":
        completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).all()
        task_sequences = [task.title for task in completed_tasks]

        return generate_sequence_suggestions(task_sequences, limit)
    
    if mode == "time":
        return generate_time_based_suggestions(analyze_time_patterns(tasks), limit)


def compute_similarity(tasks: list[Task]) -> defaultdict:
    tfidf = TfidfVectorizer(stop_words='english')
    task_texts = [ f'{task.title} {task.description or ""}' for task in tasks ]
    tfidf_matrix = tfidf.fit_transform(task_texts)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    task_similarity = defaultdict(dict)
    for i, task in enumerate(tasks):
        for j, other_task in enumerate(tasks):
            if i != j:
                task_similarity[task.title][other_task.title] = similarity_matrix[i][j]

    return task_similarity


def generate_title_description_suggestions(similarity_matrix, task_title: str, limit: int) -> defaultdict:
    suggestions = defaultdict(list)

    for title, similarities in similarity_matrix.items():
        if task_title and title != task_title: continue

        sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        for similar_title, score in sorted_similarities:
            if score > 0.5:
                suggestions[f"{title} Follow-up"].append(similar_title)

                if limit > 0:
                    limit -= 1
                else:
                    return suggestions

    return suggestions


def generate_sequence_suggestions(task_sequences, limit) -> dict:
    sequence_counter = Counter(task_sequences)
    suggestions = {}

    for sequence, count in sequence_counter.most_common(limit):
        if count > 1:
            suggestions[f"{sequence} Follow-up"] = [sequence]

    return suggestions


def analyze_time_patterns(tasks: list[Task]) -> defaultdict:
    time_patterns = defaultdict(list)

    for task in tasks:
        if task.status == TaskStatus.COMPLETED and task.due_date:
            date_key = task.due_date.date()
            time_patterns[date_key].append(task.title)

    return time_patterns


def generate_time_based_suggestions(time_patterns, limit):
    suggestions = {}
    for date, task_titles in list(time_patterns.items()):
        if len(task_titles) > 1:
            follow_up_task = " and ".join(task_titles) + " Review"
            suggestions[follow_up_task] = task_titles

            if limit > 0:
                limit -= 1
            else:
                return suggestions

    return suggestions
