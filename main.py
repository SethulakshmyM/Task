from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import psycopg2

# -----------------------------
# Database connection using environment variables
# -----------------------------
DB_NAME = os.environ.get("DB_NAME", "TaskManager")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Karthikeyan@21")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    print("✅ Database connected successfully!")
except Exception as e:
    print(f"⚠️ Failed to connect to database: {e}")
    raise e

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="Task Manager API")

# -----------------------------
# Pydantic models
# -----------------------------
class Task(BaseModel):
    id: int
    title: str
    description: str
    is_done: bool

class TaskCreate(BaseModel):
    title: str
    description: str
    is_done: bool = False

# -----------------------------
# Routes
# -----------------------------
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    cur.execute("SELECT id, title, description, is_done FROM tasks ORDER BY id ASC")
    rows = cur.fetchall()

    tasks = [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "is_done": row[3]
        }
        for row in rows
    ]
    return tasks


@app.post("/tasks", response_model=Task, status_code=201)
def add_task(task: TaskCreate):
    cur.execute(
        "INSERT INTO tasks (title, description, is_done) VALUES (%s, %s, %s) RETURNING id",
        (task.title, task.description, task.is_done)
    )
    task_id = cur.fetchone()[0]
    conn.commit()

    return {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "is_done": task.is_done
    }


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    cur.execute("SELECT id, title, description, is_done FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "is_done": row[3]
    }


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    cur.execute(
        "UPDATE tasks SET title = %s, description = %s, is_done = %s WHERE id = %s RETURNING id",
        (task.title, task.description, task.is_done, task_id)
    )
    updated = cur.fetchone()
    conn.commit()

    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "is_done": task.is_done
    }


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
    deleted = cur.fetchone()
    conn.commit()

    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}


@app.get("/")
def root():
    return {"message": "Task Manager API is running! Use /tasks to manage tasks."}
