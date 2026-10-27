"""
Tests for FastAPI Backend Endpoints.
Verifies HTTP status codes, request validation, and routing using TestClient.
"""

from fastapi.testclient import TestClient
from app.api.main import app
from app.database import init_db, SessionLocal
from app.seed_data import generate_seed_data

client = TestClient(app)


def setup_module():
    init_db()
    with SessionLocal() as db:
        generate_seed_data(db)


def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "TravelResolve AI"


def test_get_bookings():
    res = client.get("/bookings")
    assert res.status_code == 200
    bookings = res.json()
    assert len(bookings) >= 4
    assert any(b["id"] == "TRV1025" for b in bookings)


def test_get_single_booking_found_and_not_found():
    res_found = client.get("/bookings/TRV1025")
    assert res_found.status_code == 200
    assert res_found.json()["id"] == "TRV1025"

    res_missing = client.get("/bookings/TRV9999")
    assert res_missing.status_code == 404


def test_create_and_process_ticket_endpoint():
    payload = {
        "customer_message": "Could you please send me confirmation for my Miami stay under TRV1025?",
        "booking_id": "TRV1025",
        "customer_tier": "Platinum"
    }
    res = client.post("/tickets", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "ticket_id" in data
    assert data["predicted_intent"] == "booking_confirmation"
    assert data["auditor_passed"] is True


def test_ticket_validation_rejects_empty_message():
    res = client.post("/tickets", json={"customer_message": ""})
    assert res.status_code == 422  # Pydantic validation error


def test_review_queue_and_review_submission():
    queue_res = client.get("/review-queue")
    assert queue_res.status_code == 200
    items = queue_res.json()
    assert isinstance(items, list)

    # Review an existing ticket if available
    if items:
        target_id = items[0]["id"]
        review_payload = {
            "decision": "approve",
            "reviewer_name": "API Supervisor",
            "reviewer_notes": "Approved via automated API test"
        }
        submit_res = client.post(f"/tickets/{target_id}/review", json=review_payload)
        assert submit_res.status_code == 200
        assert submit_res.json()["final_status"] == "approved"


def test_evaluation_metrics_endpoint():
    res = client.get("/evaluation/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "intent_accuracy" in data
    assert "system_comparison" in data
