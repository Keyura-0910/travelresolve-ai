"""
Tests for Safe Booking Lookup and Cancellation Calculation Tools.
Verifies SQLite lookup, customer data isolation, and policy calculation rules.
"""

from app.database import init_db, SessionLocal
from app.seed_data import generate_seed_data
from app.agents.tools import (
    sanitize_booking_id,
    lookup_booking_tool,
    evaluate_cancellation_policy
)


def setup_module():
    init_db()
    with SessionLocal() as db:
        generate_seed_data(db)


def test_sanitize_booking_id():
    assert sanitize_booking_id("trv1025") == "TRV1025"
    assert sanitize_booking_id("Please check booking TRV1026 thanks") == "TRV1026"
    assert sanitize_booking_id("   TRV1027   ") == "TRV1027"
    assert sanitize_booking_id(None) is None


def test_lookup_existing_booking():
    booking = lookup_booking_tool("TRV1025")
    assert booking is not None
    assert booking["id"] == "TRV1025"
    assert "Grand Horizon" in booking["hotel_name"]
    assert booking["customer_id"] == "CUST-801"


def test_lookup_nonexistent_booking():
    booking = lookup_booking_tool("TRV9999")
    assert booking is None


def test_cross_customer_isolation():
    # Attempting to access CUST-801's booking as CUST-999 must return None
    booking = lookup_booking_tool("TRV1025", customer_id="CUST-999")
    assert booking is None

    # Correct customer ID returns the record
    valid_booking = lookup_booking_tool("TRV1025", customer_id="CUST-801")
    assert valid_booking is not None


def test_cancellation_policy_rules():
    # Non-refundable booking
    non_ref_booking = lookup_booking_tool("TRV1026")
    calc = evaluate_cancellation_policy(non_ref_booking)
    assert calc["eligible"] is False
    assert calc["refund_amount"] == 0.0
    assert "non-refundable" in calc["reason"].lower()
