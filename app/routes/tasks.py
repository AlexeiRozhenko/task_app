from fastapi import APIRouter, Depends, Form
import app.schemas.tasks as tasks_schemas
from fastapi import HTTPException, status

import app.models as models
from app.database import SessionLocal
from sqlalchemy.orm import Session

from app.routes.auth import get_current_user

router_tasks = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


### Get all tasks ###
@router_tasks.get("", response_model=list[tasks_schemas.TaskResponse])
def read_all(current_user: models.UsersDB = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(models.TasksDB).filter(models.TasksDB.user_id == current_user.id).all()
    return tasks


### Get specific task ###
@router_tasks.get("/{task_id}", response_model=tasks_schemas.TaskResponse)
def read_task(task_id: int, current_user: models.UsersDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(models.TasksDB).filter(
        (models.TasksDB.id == task_id) & 
        (models.TasksDB.user_id == current_user.id)
        ).first()
    
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    return db_task


### Add new task ###
@router_tasks.post("/create", response_model=tasks_schemas.TaskResponse)
def add_task(task: tasks_schemas.CreateTask, current_user: models.UsersDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = models.TasksDB(
        title=task.title,
        content=task.content,
        deadline=task.deadline,
        user_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


### Task update ###
@router_tasks.patch("/{task_id}", response_model=tasks_schemas.GeneralResponse)
def part_change_task(task_id: int, task: tasks_schemas.PartialUpdate, current_user: models.UsersDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(models.TasksDB).filter(
        (models.TasksDB.id == task_id) &
        (models.TasksDB.user_id == current_user.id)
    ).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    task_data = task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    return {
        "id": task_id,
        "message": f"Task {task_id} updated",
    }


### Delete task ###
@router_tasks.delete("/{task_id}", response_model=tasks_schemas.GeneralResponse)
def delete_task(task_id: int, current_user: models.UsersDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(models.TasksDB).filter(
        (models.TasksDB.id == task_id) &
        (models.TasksDB.user_id == current_user.id)
    ).first()

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    db.delete(db_task)
    db.commit()

    return {
        "id": task_id,
        "message": f"Task {task_id} deleted",
    }