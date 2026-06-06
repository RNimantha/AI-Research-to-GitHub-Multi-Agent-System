import logging

from backend.app.graph.checkpoints import checkpointer
from backend.app.graph.workflow import Trend2POCWorkflow
from backend.app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.run_pipeline")
def run_pipeline_task(self, run_id: str, topic: str | None = None, user_id: str | None = None):
    try:
        workflow = Trend2POCWorkflow()
        state = workflow.run(input_topic=topic, user_id=user_id, run_id=run_id)
        checkpointer.save(run_id, state)
        return {"run_id": run_id, "status": state.status}
    except Exception as exc:
        logger.error(f"Pipeline task {run_id} failed: {exc}")
        raise self.retry(exc=exc, countdown=30, max_retries=1)


@celery_app.task(bind=True, name="tasks.resume_poc")
def resume_poc_task(self, run_id: str):
    try:
        state = checkpointer.load(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found in checkpoint store")
        workflow = Trend2POCWorkflow()
        updated = workflow.resume_after_report_approval(state)
        checkpointer.save(run_id, updated)
        return {"run_id": run_id, "status": updated.status}
    except Exception as exc:
        logger.error(f"POC resume task {run_id} failed: {exc}")
        raise self.retry(exc=exc, countdown=30, max_retries=1)


@celery_app.task(bind=True, name="tasks.publish_github")
def publish_github_task(self, run_id: str):
    try:
        state = checkpointer.load(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found in checkpoint store")
        workflow = Trend2POCWorkflow()
        updated = workflow.resume_after_github_approval(state)
        checkpointer.save(run_id, updated)
        return {"run_id": run_id, "status": updated.status, "github_url": updated.github_repo_url}
    except Exception as exc:
        logger.error(f"GitHub publish task {run_id} failed: {exc}")
        raise self.retry(exc=exc, countdown=30, max_retries=1)
