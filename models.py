from sqlalchemy import Column, String, Integer, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Event(Base):
    """Database model for storing analytics events"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    path = Column(String)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_site_date', 'site_id', 'timestamp'),
    )

