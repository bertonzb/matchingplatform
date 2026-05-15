import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.matching_task import MatchingTask
from app.tasks.matching_task import run_matching_async

router = APIRouter(prefix="/api/v1/matching", tags=["matching"])


class MatchingRequest(BaseModel):
    requirement: str = Field(..., min_length=10, description="匹配需求描述")
    top_n: int = Field(default=5, ge=1, le=20)


class MatchingResponse(BaseModel):
    task_id: str
    status: str


class MatchingResult(BaseModel):
    task_id: str
    status: str
    result: list | None = None
    created_at: str | None = None
    completed_at: str | None = None


@router.post("/", response_model=MatchingResponse, status_code=202)
def submit_matching(req: MatchingRequest, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    db_task = MatchingTask(
        task_id=task_id,
        user_requirement=req.requirement,
        status="pending",
        top_n=req.top_n,
    )
    db.add(db_task)
    db.commit()

    celery_task = run_matching_async.delay(task_id, req.requirement, req.top_n)
    db_task.celery_task_id = celery_task.id
    db.commit()

    return MatchingResponse(task_id=task_id, status="pending")


@router.get("/{task_id}", response_model=MatchingResult)
def get_matching_result(task_id: str, db: Session = Depends(get_db)):
    task = db.query(MatchingTask).filter(
        MatchingTask.task_id == task_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result = None
    if task.result:
        result = json.loads(task.result)

    return MatchingResult(
        task_id=task.task_id,
        status=task.status,
        result=result,
        created_at=task.created_at.isoformat() if task.created_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("/history/list")
def get_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    tasks = db.query(MatchingTask).order_by(
        MatchingTask.created_at.desc()
    ).offset(skip).limit(limit).all()
    return [
        {
            "task_id": t.task_id,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in tasks
    ]
