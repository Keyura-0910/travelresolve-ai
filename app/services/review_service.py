"""
Service layer for the Human Review Queue and supervisory interventions.
Enables approving, rejecting, or revising drafts with full persistence and auditability.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database import Ticket, HumanReview, AuditLog
from app.schemas import HumanReviewRequest
from app.agents.graph import resume_ticket_workflow


def get_pending_reviews(db: Session) -> List[Dict[str, Any]]:
    """Retrieves all tickets waiting in the Human Review Queue."""
    tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "pending_human_review")
        .order_by(Ticket.priority_score.desc(), Ticket.created_at.asc())
        .all()
    )
    return [t.to_dict() for t in tickets]


def submit_human_review(
    ticket_id: str,
    review_req: HumanReviewRequest,
    db: Session
) -> Dict[str, Any]:
    """
    Records a supervisor review decision, resumes the LangGraph workflow thread,
    updates ticket status, and logs an audit event.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise ValueError(f"Ticket '{ticket_id}' not found.")

    decision = review_req.decision.lower()

    # Create HumanReview record
    review_entry = HumanReview(
        ticket_id=ticket_id,
        decision=decision,
        reviewer_name=review_req.reviewer_name,
        reviewer_notes=review_req.reviewer_notes,
        original_draft=ticket.draft_response or "",
        edited_draft=review_req.edited_draft
    )
    db.add(review_entry)

    # Determine final response and ticket status
    if decision == "approve":
        final_status = "approved"
        final_response = review_req.edited_draft or ticket.draft_response
    elif decision == "revise":
        final_status = "approved"
        final_response = review_req.edited_draft or review_req.reviewer_notes or ticket.draft_response
    elif decision == "reject":
        final_status = "rejected"
        final_response = (
            f"Automated resolution rejected by supervisor ({review_req.reviewer_name}). "
            f"Notes: {review_req.reviewer_notes or 'Transferred to manual agent queue.'}"
        )
    else:
        raise ValueError(f"Unsupported review decision: {decision}")

    ticket.status = final_status
    ticket.human_reviewer = review_req.reviewer_name
    ticket.human_review_notes = review_req.reviewer_notes
    ticket.final_response = final_response

    # Resume LangGraph thread state
    try:
        resume_ticket_workflow(
            thread_id=ticket_id,
            human_decision=decision,
            reviewer_name=review_req.reviewer_name,
            reviewer_notes=review_req.reviewer_notes
        )
    except Exception as e:
        print(f"Notice: Workflow state resume skipped ({e}). Direct DB persistence applied.")

    # Record Audit Log
    audit = AuditLog(
        ticket_id=ticket_id,
        event_type="HUMAN_REVIEW_DECISION",
        actor=review_req.reviewer_name,
        details=(
            f"Decision: {decision.upper()}. Notes: {review_req.reviewer_notes}. "
            f"Ticket transitioned to status: {final_status}."
        )
    )
    db.add(audit)

    db.commit()
    db.refresh(ticket)
    db.refresh(review_entry)

    return {
        "review_id": review_entry.id,
        "ticket_id": ticket.id,
        "decision": decision,
        "reviewer_name": review_req.reviewer_name,
        "reviewer_notes": review_req.reviewer_notes,
        "final_status": ticket.status,
        "final_response": ticket.final_response,
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else datetime.now(timezone.utc).isoformat()
    }
