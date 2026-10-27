"""
Tests for LangGraph Multi-Agent Workflow Execution & Human Review.
Verifies DAG transitions, conditional routing, and state resumption.
"""

from app.database import init_db, SessionLocal
from app.seed_data import generate_seed_data
from app.agents.graph import run_ticket_workflow, resume_ticket_workflow
from app.agents.state import TicketWorkflowState
from app.schemas import HumanReviewRequest
from app.services.review_service import submit_human_review
from app.database import Ticket


def setup_module():
    init_db()
    with SessionLocal() as db:
        generate_seed_data(db)


def test_clean_ticket_auto_approves():
    initial_state: TicketWorkflowState = {
        "ticket_id": "TEST-TCK-001",
        "customer_message": "Can you please verify my confirmed reservation TRV1025 at Grand Horizon?",
        "booking_id": "TRV1025",
        "customer_tier": "Platinum",
        "execution_trace": [],
        "warnings": [],
        "errors": []
    }
    result = run_ticket_workflow(initial_state, thread_id="TEST-TCK-001")
    assert result["predicted_intent"] == "booking_confirmation"
    assert result["booking_found"] is True
    assert result["auditor_passed"] is True
    assert result["final_status"] == "auto_approved"
    assert len(result["execution_trace"]) >= 5


def test_sensitive_ticket_escalates_to_human_review():
    initial_state: TicketWorkflowState = {
        "ticket_id": "TEST-TCK-002",
        "customer_message": "I need to cancel booking TRV1026 right now and get all my money refunded.",
        "booking_id": "TRV1026",
        "customer_tier": "Standard",
        "execution_trace": [],
        "warnings": [],
        "errors": []
    }
    result = run_ticket_workflow(initial_state, thread_id="TEST-TCK-002")
    assert result["needs_human_review"] is True
    assert result["final_status"] == "pending_human_review"
    assert result["escalation_reason"] is not None


def test_human_review_approval_resumption():
    # Submit review on TCK-1002 (seeded as pending_human_review)
    req = HumanReviewRequest(
        decision="approve",
        reviewer_name="Sarah Supervisor",
        reviewer_notes="Approved exception voucher."
    )
    with SessionLocal() as db:
        res = submit_human_review("TCK-1002", req, db)
        assert res["final_status"] == "approved"
        assert res["reviewer_name"] == "Sarah Supervisor"

        # Verify DB persistence
        ticket = db.query(Ticket).filter(Ticket.id == "TCK-1002").first()
        assert ticket.status == "approved"
        assert ticket.human_reviewer == "Sarah Supervisor"
