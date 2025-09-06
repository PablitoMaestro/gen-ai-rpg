from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    status: str = Field(default="success", description="Response status")
    message: Optional[str] = Field(default=None, description="Optional message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field(default="error", description="Error status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None