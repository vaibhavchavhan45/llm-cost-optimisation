# Data models (Schema) for the routing decision and dev-facing metadata.

from pydantic import BaseModel, Field
from typing import Optional


# metadata for devs
class DevMetadata(BaseModel):
    model_used: str = Field(description="Actual model name used (dev-facing only)")
    display_model: str = Field(description="Generic label shown to user: Fast or Advanced")
    complexity_score: int = Field(description="Final complexity score calculated")
    matched_rules: list[str] = Field(description="Which rules triggered this decision")
    estimated_cost: float = Field(description="Estimated cost for this request")
    hypothetical_heavy_cost: Optional[float] = Field(
        default=None, description="What this would have cost on heavy model (only shown when light model is used)"
    )
    estimated_savings: Optional[float] = Field(
        default=None, description="Cost saved by using light model instead of heavy (only when light model is used)"
    )


# Final response structure : user-facing answer and dev metadata.
class RoutedResponse(BaseModel):
    answer: str = Field(description="The actual response to the user's task")
    dev_metadata: DevMetadata = Field(description="Backend-only routing and cost data")