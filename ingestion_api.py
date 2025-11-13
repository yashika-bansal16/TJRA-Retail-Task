from fastapi import FastAPI, HTTPException, status
from app.schemas import EventRequest, EventResponse
from app.queue import enqueue_event
from datetime import datetime
from dateutil import parser as date_parser

app = FastAPI(title="Analytics Ingestion API", version="1.0.0")


@app.post("/event", response_model=EventResponse, status_code=status.HTTP_200_OK)
async def ingest_event(event: EventRequest):
    """
    Fast ingestion endpoint that validates and queues events.
    
    This endpoint is designed to be extremely fast by:
    1. Performing minimal validation
    2. Immediately queuing the event (non-blocking)
    3. Returning success without waiting for database writes
    """
    # Validate required fields
    if not event.site_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="site_id is required"
        )
    
    if not event.event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_type is required"
        )
    
    # Parse and validate timestamp if provided, otherwise use current time
    timestamp = datetime.utcnow()
    if event.timestamp:
        try:
            timestamp = date_parser.parse(event.timestamp)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format. Use ISO 8601 format (e.g., 2025-11-12T19:30:01Z)"
            )
    
    # Prepare event data for queue
    event_data = {
        "site_id": event.site_id,
        "event_type": event.event_type,
        "path": event.path,
        "user_id": event.user_id,
        "timestamp": timestamp.isoformat()
    }
    
    # Queue the event (non-blocking, fast operation)
    if not enqueue_event(event_data):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to queue event. Queue service may be unavailable."
        )
    
    # Immediately return success without waiting for processing
    return EventResponse(
        status="success",
        message="Event queued successfully"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

