import json
import asyncio
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.database import get_db_session
from app.models.matching_task import MatchingTask
from app.core.agents.graph import run_matching_pipeline


@celery_app.task(bind=True, max_retries=0)
def run_matching_async(self, task_id: str, requirement: str, top_n: int):
    db = get_db_session()
    try:
        task = db.query(MatchingTask).filter(
            MatchingTask.task_id == task_id
        ).first()
        if not task:
            return

        task.status = "running"
        db.commit()

        results = asyncio.run(
            run_matching_pipeline(requirement, top_n, db)
        )

        task.result = json.dumps(results, ensure_ascii=False)
        task.status = "done"
        task.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        task = db.query(MatchingTask).filter(
            MatchingTask.task_id == task_id
        ).first()
        if task:
            task.status = "failed"
            task.result = json.dumps({"error": str(e)})
            task.completed_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()
