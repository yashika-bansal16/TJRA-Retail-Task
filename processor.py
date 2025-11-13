import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Event
from app.queue import dequeue_event
from dateutil import parser as date_parser


def process_event(event_data: dict, db: Session):
    """
    Process a single event and write it to the database.
    """
    try:
        # Parse timestamp
        timestamp = datetime.utcnow()
        if event_data.get("timestamp"):
            timestamp = date_parser.parse(event_data["timestamp"])
        
        # Create event record
        event = Event(
            site_id=event_data["site_id"],
            event_type=event_data["event_type"],
            path=event_data.get("path"),
            user_id=event_data.get("user_id"),
            timestamp=timestamp
        )
        
        # Write to database
        db.add(event)
        db.commit()
        db.refresh(event)
        
        print(f"Processed event: {event.id} - {event.site_id} - {event.event_type}")
        return True
    except Exception as e:
        print(f"Error processing event: {e}")
        db.rollback()
        return False


def run_processor():
    """
    Main processor loop that continuously processes events from the queue.
    This is a background worker, not a public API.
    """
    print("Starting event processor...")
    
    # Initialize database
    init_db()
    
    # Main processing loop
    while True:
        try:
            # Get event from queue (blocking with timeout)
            event_data = dequeue_event()
            
            if event_data:
                # Process the event
                db = SessionLocal()
                try:
                    process_event(event_data, db)
                finally:
                    db.close()
            else:
                # No events in queue, small sleep to avoid busy waiting
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nShutting down processor...")
            break
        except Exception as e:
            print(f"Error in processor loop: {e}")
            time.sleep(1)  # Wait before retrying on error


if __name__ == "__main__":
    run_processor()

