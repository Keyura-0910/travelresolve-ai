"""
Controlled booking lookup and calculation tools.
Safely queries the SQLite database, validates IDs, and performs deterministic
cancellation and refund eligibility calculations. Never fabricates records.
"""

import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import Booking, SessionLocal


def sanitize_booking_id(booking_id: Optional[str]) -> Optional[str]:
    """Sanitizes and extracts a standardized booking ID (e.g., 'TRV1025')."""
    if not booking_id:
        return None
    cleaned = booking_id.strip().upper()
    match = re.search(r"\b(TRV\d{3,6})\b", cleaned)
    return match.group(1) if match else cleaned


def lookup_booking_tool(
    booking_id: str,
    customer_id: Optional[str] = None,
    session: Optional[Session] = None
) -> Optional[Dict[str, Any]]:
    """
    Controlled SQLite booking lookup.
    Guarantees isolation: If customer_id is provided, cross-checks ownership.
    Returns None if booking is not found or customer mismatch occurs.
    """
    clean_id = sanitize_booking_id(booking_id)
    if not clean_id:
        return None

    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        query = session.query(Booking).filter(Booking.id == clean_id)
        booking = query.first()

        if not booking:
            return None

        # Cross-customer data isolation check
        if customer_id and booking.customer_id.strip().upper() != customer_id.strip().upper():
            return None

        return booking.to_dict()
    finally:
        if close_session:
            session.close()


def evaluate_cancellation_policy(booking: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic rule evaluation of cancellation and refund eligibility.
    Based on POL-CANC-001 and POL-REF-002:
    - Non-refundable rate: 0 refund, supervisor exception needed for medical emergencies.
    - >= 48 hours to check-in: 100% refund.
    - 24 - 48 hours to check-in: 50% refund.
    - < 24 hours: 0% refund (forfeited).
    """
    if not booking:
        return {
            "eligible": False,
            "refund_amount": 0.0,
            "cancellation_fee": 0.0,
            "reason": "No booking context available."
        }

    total_amount = float(booking.get("total_amount", 0.0))
    rate_eligible = bool(booking.get("cancellation_eligible", True))

    if not rate_eligible:
        return {
            "eligible": False,
            "refund_amount": 0.0,
            "cancellation_fee": total_amount,
            "reason": "Booking is non-refundable per rate terms. Supervisor exception required for compassionate cases."
        }

    check_in_str = booking.get("check_in_date")
    if not check_in_str:
        return {
            "eligible": True,
            "refund_amount": total_amount,
            "cancellation_fee": 0.0,
            "reason": "Standard flexible rate."
        }

    try:
        check_in_dt = datetime.strptime(check_in_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now_dt = datetime.now(timezone.utc)
        hours_to_checkin = (check_in_dt - now_dt).total_seconds() / 3600.0

        if hours_to_checkin >= 48.0:
            return {
                "eligible": True,
                "refund_amount": total_amount,
                "cancellation_fee": 0.0,
                "hours_to_checkin": round(hours_to_checkin, 1),
                "reason": f"Cancelled {round(hours_to_checkin, 1)}h prior to check-in (>= 48h window). Full 100% refund applies."
            }
        elif 24.0 <= hours_to_checkin < 48.0:
            fee = round(total_amount * 0.5, 2)
            refund = round(total_amount - fee, 2)
            return {
                "eligible": True,
                "refund_amount": refund,
                "cancellation_fee": fee,
                "hours_to_checkin": round(hours_to_checkin, 1),
                "reason": f"Cancelled {round(hours_to_checkin, 1)}h prior to check-in (24-48h window). 50% cancellation fee applies."
            }
        else:
            return {
                "eligible": False,
                "refund_amount": 0.0,
                "cancellation_fee": total_amount,
                "hours_to_checkin": round(hours_to_checkin, 1),
                "reason": f"Cancelled {round(hours_to_checkin, 1)}h prior to check-in (< 24h window). Non-refundable."
            }
    except Exception as e:
        return {
            "eligible": True,
            "refund_amount": total_amount,
            "cancellation_fee": 0.0,
            "reason": f"Check-in date calculation fallback: {e}"
        }
