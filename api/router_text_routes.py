# API endpoint that returns only the plain text answer

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from schemas.request_schemas import TaskRequest, BatchTaskRequest
from chains.routing_pipeline import run_routing_pipeline, run_batch_routing_pipeline
from services.formatter import format_answer
from validations.input_validation import validate_task_input

router = APIRouter()


@router.post("/route-task/answer-text", response_class=PlainTextResponse, summary="Route Task Plain Text")
def route_task_plain_text(request: TaskRequest):
    """
        Route support a single task and returns the answer as plain text.
    """
    valid, message = validate_task_input(request.task)
    if not valid:
        raise HTTPException(status_code=400, detail=message)

    try:
        result = run_routing_pipeline(request.task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task processing failed: {e}")

    return format_answer(result)


@router.post("/route-task/batch/answer-text", response_class=PlainTextResponse, summary="Route Batch Tasks Plain Text")
def route_batch_plain_text(request: BatchTaskRequest):
    """
        Route supports the multiples tasks and returns their question and answer as plain text.
    """
    for task in request.tasks:
        valid, message = validate_task_input(task)
        if not valid:
            raise HTTPException(status_code=400, detail=f"Invalid task '{task}': {message}")

    try:
        results = run_batch_routing_pipeline(request.tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {e}")

    formatted = [f"Q: {r['task']}\nA: {format_answer(r)}" for r in results]
    return "\n\n---\n\n".join(formatted)