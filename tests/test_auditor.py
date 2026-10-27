"""
Tests for Resolution Auditor.
Verifies detection of hallucinations, incorrect IDs, wrong amounts, and non-refundable policy violations.
"""

from app.agents.auditor import get_resolution_auditor


def test_auditor_clean_draft_passes():
    auditor = get_resolution_auditor()
    booking = {
        "id": "TRV1025",
        "hotel_name": "Grand Horizon Resort & Spa",
        "booking_status": "confirmed",
        "total_amount": 1240.00,
        "currency": "USD",
        "cancellation_eligible": True
    }
    draft = "Dear Elena, your confirmed booking TRV1025 at Grand Horizon Resort & Spa is active. Total paid: $1240.00."
    finding = auditor.audit_resolution(draft, booking, [], "booking_confirmation")
    assert finding.passed is True
    assert finding.hallucination_detected is False
    assert len(finding.violations) == 0


def test_auditor_catches_hallucinated_booking_id():
    auditor = get_resolution_auditor()
    booking = {
        "id": "TRV1025",
        "hotel_name": "Grand Horizon Resort & Spa",
        "booking_status": "confirmed",
        "total_amount": 1240.00,
        "cancellation_eligible": True
    }
    # Draft mentions TRV9999 instead of TRV1025
    bad_draft = "Your reservation TRV9999 at Grand Horizon is confirmed."
    finding = auditor.audit_resolution(bad_draft, booking, [], "booking_confirmation")
    assert finding.passed is False
    assert any("Hallucinated Booking ID" in v for v in finding.violations)


def test_auditor_catches_unauthorized_nonrefundable_refund():
    auditor = get_resolution_auditor()
    booking = {
        "id": "TRV1026",
        "hotel_name": "Alpine Pine Lodge",
        "booking_status": "confirmed",
        "total_amount": 890.50,
        "currency": "USD",
        "cancellation_eligible": False  # Non-refundable!
    }
    bad_draft = "Hello Marcus, for booking TRV1026 at Alpine Pine Lodge, we have issued a full refund to your card."
    finding = auditor.audit_resolution(bad_draft, booking, [], "cancellation")
    assert finding.passed is False
    assert any("Unauthorized Refund" in v for v in finding.violations)


def test_auditor_catches_empty_draft():
    auditor = get_resolution_auditor()
    finding = auditor.audit_resolution("", None, [], "cancellation")
    assert finding.passed is False
