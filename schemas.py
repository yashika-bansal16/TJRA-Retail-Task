from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class EventRequest(BaseModel):
    """Schema for incoming event data"""
    site_id: str = Field(..., description="Site identifier (required)")
    event_type: str = Field(..., description="Event type (required)")
    path: Optional[str] = Field(None, description="Page path")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp")


class EventResponse(BaseModel):
    """Schema for event ingestion response"""
    status: str = "success"
    message: str = "Event queued successfully"


class TopPath(BaseModel):
    """Schema for top path statistics"""
    path: str
    views: int


class StatsResponse(BaseModel):
    """Schema for statistics response"""
    site_id: str
    date: str
    total_views: int
    unique_users: int
    top_paths: List[TopPath]

