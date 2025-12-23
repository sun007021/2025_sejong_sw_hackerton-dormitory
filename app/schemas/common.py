from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    total: int = Field(..., description="Total number of items")
    items: List[T] = Field(..., description="List of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")

    model_config = {"from_attributes": True}