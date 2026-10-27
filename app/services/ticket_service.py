"""
Service layer for Ticket processing, database synchronization, and audit logging.
Orchestrates LangGraph workflow runs and maintains audit trails.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import Ticket, AuditLog, Booking
from app.schemas import TicketCreateRequest, TicketProcessResponse
from app.agents.graph import run_ticket_workflow
from app.agents.state import TicketWorkflowState
from app.agents.tools import sanitize_booking_id


def generate_ticket_id(db: Session) -> str:
    """Generates sequential, user-friendly ticket identifiers (e.g., TCK-1004)."""
    count = db.query(func.count(Ticket.id)).scalar() or 0
    return f"TCK-{1001 + count}"


def create_and_process_ticket(request: TicketCreateRequest, db: Session) -> Dict[str, Any]:
    """
    Creates a new ticket, executes the LangGraph workflow, persists results,
    and returns the comprehensive execution outcome.
    """
    ticket_id = generate_ticket_id(db)
    clean_bid = sanitize_booking_id(request.booking_id)

    # Initial state for LangGraph
    initial_state: TicketWorkflowState = {
        "ticket_id": ticket_id,
        "customer_message": request.customer_message,
        "booking_id": clean_bid,
        "customer_id": request.customer_id,
        "customer_name": request.customer_name,
        "customer_tier": request.customer_tier or "Standard",
        "execution_trace": [],
        "warnings": [],
        "errors": []
    }

    # Execute LangGraph DAG
    final_state = run_ticket_workflow(initial_state, thread_id=ticket_id)

    # Persist Ticket in SQLite
    ticket = Ticket(
        id=ticket_id,
        booking_id=final_state.get("booking_id"),
        customer_id=final_state.get("customer_id"),
        customer_name=final_state.get("customer_name"),
        customer_tier=final_state.get("customer_tier", "Standard"),
        customer_message=final_state.get("customer_message"),
        predicted_intent=final_state.get("predicted_intent", "general_travel_query"),
        intent_confidence=float(final_state.get("classification_confidence", 0.0)),
        priority=final_state.get("priority", "medium"),
        priority_score=int(final_state.get("priority_score", 50)),
        priority_reasons=json.dumps(final_state.get("priority_reasons", [])),
        status=final_state.get("final_status", "open"),
        draft_response=final_state.get("draft_resolution"),
        final_response=final_state.get("final_resolution"),
        auditor_passed=bool(final_state.get("auditor_passed", False)),
        auditor_findings=json.dumps(final_state.get("auditor_findings", {})),
        escalation_reason=final_state.get("escalation_reason"),
        execution_trace=json.dumps(final_state.get("execution_trace", []))
    )
    db.add(ticket)

    # Create Audit Log Records for Key Workflow Transitions
    for step in final_state.get("execution_trace", []):
        audit_entry = AuditLog(
            ticket_id=ticket_id,
            event_type=step.get("node", "workflow_node").upper(),
            actor=f"AgentNode_{step.get('node')}",
            details=json.dumps(step.get("details", {}))
        )
        db.add(audit_entry)

    db.commit()
    db.refresh(ticket)

    return {
        "ticket_id": ticket.id,
        "booking_id": ticket.booking_id,
        "customer_message": ticket.customer_message,
        "predicted_intent": ticket.predicted_intent,
        "intent_confidence": ticket.intent_confidence,
        "priority": ticket.priority,
        "priority_score": ticket.priority_score,
        "priority_reasons": json.loads(ticket.priority_reasons),
        "status": ticket.status,
        "draft_response": ticket.draft_response,
        "final_response": ticket.final_response,
        "booking_context": final_state.get("booking_record"),
        "policy_evidence": final_state.get("policy_evidence", []),
        "auditor_findings": json.loads(ticket.auditor_findings),
        "auditor_passed": ticket.auditor_passed,
        "escalation_reason": ticket.escalation_reason,
        "execution_trace": json.loads(ticket.execution_trace)
    }


def get_ticket(ticket_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Retrieves ticket details by ID."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    return ticket.to_dict() if ticket else None


def list_tickets(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves list of tickets ordered by creation time descending."""
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(limit).all()
    return [t.to_dict() for t in tickets]


def get_ticket_audit_logs(ticket_id: str, db: Session) -> List[Dict[str, Any]]:
    """Retrieves chronological audit logs for a specific ticket."""
    logs = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).order_by(AuditLog.id.asc()).all()
    return [l.to_dict() for l in logs]
