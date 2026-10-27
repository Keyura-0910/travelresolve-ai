"""
Service layer for booking lookups and catalog operations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.database import Booking
from app.agents.tools import sanitize_booking_id


def get_booking(booking_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Safely retrieves a booking record by ID."""
    clean_id = sanitize_booking_id(booking_id)
    if not clean_id:
        return None
    booking = db.query(Booking).filter(Booking.id == clean_id).first()
    return booking.to_dict() if booking else None


def list_bookings(db: Session, limit: int = 100) -> List[Dict[str, Any]]:
    """Lists recent synthetic bookings."""
    bookings = db.query(Booking).order_by(Booking.check_in_date.asc()).limit(limit).all()
    return [b.to_dict() for b in bookings]
