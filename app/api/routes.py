"""
FastAPI route definitions for TravelResolve AI.
Exposes REST endpoints for bookings, tickets, agent traces, audit logs, human review queue, and evaluation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    BookingResponse,
    TicketCreateRequest,
    TicketProcessResponse,
    TicketDetailResponse,
    HumanReviewRequest,
    HumanReviewResponse,
    AuditLogResponse,
    EvaluationMetricsResponse
)
from app.services.booking_service import get_booking, list_bookings
from app.services.ticket_service import (
    create_and_process_ticket,
    get_ticket,
    list_tickets,
    get_ticket_audit_logs
)
from app.services.review_service import get_pending_reviews, submit_human_review
from app.services.evaluation_service import get_cached_or_run_eval, run_benchmark_evaluation

router = APIRouter()


# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------
@router.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "TravelResolve AI",
        "version": "1.0.0",
        "storage": "SQLite Local",
        "agent_framework": "LangGraph"
    }


# -----------------------------------------------------------------------------
# Bookings Endpoints
# -----------------------------------------------------------------------------
@router.get("/bookings", response_model=List[BookingResponse], tags=["Bookings"])
def get_all_bookings(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """Retrieves synthetic booking records."""
    return list_bookings(db, limit=limit)


@router.get("/bookings/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
def get_booking_by_id(booking_id: str, db: Session = Depends(get_db)):
    """Retrieves a single booking by reference ID (e.g., TRV1025)."""
    booking = get_booking(booking_id, db)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking reference '{booking_id}' not found."
        )
    return booking


# -----------------------------------------------------------------------------
# Tickets & Agent Processing Endpoints
# -----------------------------------------------------------------------------
@router.post("/tickets", response_model=TicketProcessResponse, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_ticket(request: TicketCreateRequest, db: Session = Depends(get_db)):
    """
    Submits a customer travel inquiry.
    Executes the full LangGraph workflow:
    ML classification -> Booking lookup -> RAG retrieval -> Drafting -> Auditor -> Routing.
    """
    try:
        result = create_and_process_ticket(request, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ticket workflow execution error: {str(e)}"
        )


@router.get("/tickets", response_model=List[TicketDetailResponse], tags=["Tickets"])
def get_all_tickets(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Lists historical and active support tickets."""
    return list_tickets(db, limit=limit)


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse, tags=["Tickets"])
def get_ticket_details(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieves full ticket resolution details and metadata."""
    ticket = get_ticket(ticket_id, db)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found."
        )
    return ticket


@router.get("/tickets/{ticket_id}/trace", tags=["Observability"])
def get_ticket_execution_trace(ticket_id: str, db: Session = Depends(get_db)):
    """Returns the step-by-step LangGraph node execution trace."""
    ticket = get_ticket(ticket_id, db)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found."
        )
    return {
        "ticket_id": ticket_id,
        "execution_trace": ticket.get("execution_trace", [])
    }


@router.get("/tickets/{ticket_id}/audit", response_model=List[AuditLogResponse], tags=["Observability"])
def get_ticket_audit(ticket_id: str, db: Session = Depends(get_db)):
    """Returns immutable audit logs recorded for this ticket."""
    logs = get_ticket_audit_logs(ticket_id, db)
    return logs


# -----------------------------------------------------------------------------
# Human Review Queue Endpoints
# -----------------------------------------------------------------------------
@router.get("/review-queue", response_model=List[TicketDetailResponse], tags=["Human Review"])
def list_review_queue(db: Session = Depends(get_db)):
    """Lists all tickets escalated and awaiting supervisor action."""
    return get_pending_reviews(db)


@router.post("/tickets/{ticket_id}/review", response_model=HumanReviewResponse, tags=["Human Review"])
def review_ticket(ticket_id: str, review_req: HumanReviewRequest, db: Session = Depends(get_db)):
    """Submits a supervisor review decision (approve, reject, or revise)."""
    try:
        res = submit_human_review(ticket_id, review_req, db)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# -----------------------------------------------------------------------------
# Evaluation & Benchmark Endpoints
# -----------------------------------------------------------------------------
@router.get("/evaluation/metrics", response_model=EvaluationMetricsResponse, tags=["Evaluation"])
def get_evaluation_metrics():
    """Returns benchmark comparison metrics across Baseline, RAG Baseline, and TravelResolve AI."""
    metrics = get_cached_or_run_eval()
    return metrics


@router.post("/evaluation/run", response_model=EvaluationMetricsResponse, tags=["Evaluation"])
def trigger_evaluation_run(sample_limit: int = Query(100, ge=10, le=200)):
    """Triggers an on-demand benchmark evaluation run against synthetic cases."""
    metrics = run_benchmark_evaluation(sample_limit=sample_limit)
    return metrics
