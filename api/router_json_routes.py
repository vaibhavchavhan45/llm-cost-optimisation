# API endpoints returning JSON (user answer + dev-facing metadata)

from fastapi import APIRouter, HTTPException

from schemas.request_schemas import TaskRequest, BatchTaskRequest, TaskResponse, BatchTaskResponse
from chains.routing_pipeline import run_routing_pipeline, run_batch_routing_pipeline
from validations.input_validation import validate_task_input

router = APIRouter()


@router.post("/route-task", response_model=TaskResponse, summary="Route Task JSON")
def route_task(request: TaskRequest):
    """
        This route supports the single task req.
    """
    valid, message = validate_task_input(request.task)
    if not valid:
        raise HTTPException(status_code=400, detail=message)

    try:
        result = run_routing_pipeline(request.task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task processing failed: {e}")

    return TaskResponse(task=result["task"], answer=result["answer"], dev_metadata=result["dev_metadata"])


@router.post("/route-task/batch", response_model=BatchTaskResponse, summary="Route Batch Tasks JSON")
def route_batch_tasks(request: BatchTaskRequest):
    """
        This route supports the Batch tasks
    """
    for task in request.tasks:
        valid, message = validate_task_input(task)
        if not valid:
            raise HTTPException(status_code=400, detail=f"Invalid task '{task}': {message}")

    try:
        results = run_batch_routing_pipeline(request.tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {e}")

    return BatchTaskResponse(
        results=[TaskResponse(task=r["task"], answer=r["answer"], dev_metadata=r["dev_metadata"]) for r in results]
    )