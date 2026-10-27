"""
Tests for Rule-Based Ticket Prioritization Engine.
Verifies time-to-checkin thresholds, VIP tier weighting, payment failure bumps, and edge cases.
"""

from datetime import datetime, timedelta, timezone
from app.ml.priority import calculate_ticket_priority


def test_imminent_checkin_triggers_critical():
    tomorrow = (datetime.now(timezone.utc) + timedelta(hours=18)).strftime("%Y-%m-%d")
    booking = {
        "check_in_date": tomorrow,
        "payment_status": "paid",
        "booking_status": "confirmed"
    }
    res = calculate_ticket_priority(
        intent="booking_confirmation",
        booking_context=booking,
        customer_tier="Platinum"
    )
    assert res.priority in ["critical", "high"]
    assert res.score >= 75
    assert any("Imminent check-in" in r for r in res.reasons)
    assert any("VIP" in r for r in res.reasons)


def test_failed_payment_increases_priority():
    future_date = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%d")
    booking = {
        "check_in_date": future_date,
        "payment_status": "failed",
        "booking_status": "confirmed"
    }
    res = calculate_ticket_priority(
        intent="payment_issue",
        booking_context=booking,
        customer_tier="Standard"
    )
    assert res.score >= 60
    assert any("Payment failed" in r for r in res.reasons)


def test_missing_or_invalid_booking_context():
    # Should calculate gracefully without crashing
    res = calculate_ticket_priority(
        intent="general_travel_query",
        booking_context=None,
        customer_tier="Standard"
    )
    assert res.priority in ["low", "medium"]
    assert res.score < 50
    assert len(res.reasons) >= 1
