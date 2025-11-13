from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db, init_db
from app.models import Event
from app.schemas import StatsResponse, TopPath
from datetime import datetime, date
from dateutil import parser as date_parser
from typing import Optional

app = FastAPI(title="Analytics Reporting API", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/stats", response_model=StatsResponse)
async def get_stats(
    site_id: str = Query(..., description="Site identifier (required)"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (optional)"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated statistics for a site.
    
    Returns:
    - total_views: Total number of page views
    - unique_users: Number of unique users
    - top_paths: Top 10 most viewed paths
    """
    try:
        # Parse date if provided
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Use YYYY-MM-DD format."
                )
        
        # Build query base
        query = db.query(Event).filter(Event.site_id == site_id)
        
        # Filter by date if provided
        if target_date:
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            query = query.filter(
                and_(
                    Event.timestamp >= start_datetime,
                    Event.timestamp <= end_datetime
                )
            )
        
        # Get total views (count of all events)
        total_views = query.count()
        
        # Get unique users (count distinct user_ids, excluding None)
        unique_users = query.filter(Event.user_id.isnot(None)).distinct(Event.user_id).count()
        
        # Get top paths
        # Group by path, count views, order by count descending, limit to top 10
        top_paths_query = query.filter(Event.path.isnot(None))
        if target_date:
            top_paths_query = top_paths_query.filter(
                and_(
                    Event.timestamp >= start_datetime,
                    Event.timestamp <= end_datetime
                )
            )
        
        top_paths_results = (
            top_paths_query
            .with_entities(Event.path, func.count(Event.id).label('views'))
            .group_by(Event.path)
            .order_by(func.count(Event.id).desc())
            .limit(10)
            .all()
        )
        
        # Format top paths
        top_paths = [
            TopPath(path=path, views=views)
            for path, views in top_paths_results
        ]
        
        # Determine the date to return (use provided date or today)
        if target_date:
            result_date = date
        else:
            result_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        return StatsResponse(
            site_id=site_id,
            date=result_date,
            total_views=total_views,
            unique_users=unique_users,
            top_paths=top_paths
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

