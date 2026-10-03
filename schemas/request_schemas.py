# Request and response models for the API. Supports single and batch tasks.

from pydantic import BaseModel, Field


# Pydantic Schema for the user request includes single task
class TaskRequest(BaseModel):
    task: str = Field(..., min_length=3, description="The task/prompt to process")


# Pydantic Schema for the user request includes muctiple tasks (max limit = 10)
class BatchTaskRequest(BaseModel):
    tasks: list[str] = Field(..., min_length=1, max_length=10, description="List of independent tasks to process (max 10)")


# Pydantic Schema for the LLM response includes single task's answer and metadata
class TaskResponse(BaseModel):
    task: str
    answer: str
    dev_metadata: dict


# Pydantic Schema for the response includes multiple tasks' answers and metadata
class BatchTaskResponse(BaseModel):
    results: list[TaskResponse]