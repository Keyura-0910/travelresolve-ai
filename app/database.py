"""
Database setup and SQLAlchemy models for TravelResolve AI.
Uses a single local SQLite database for bookings, tickets, audit logs, and human reviews.
"""

import json
from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Engine with SQLite connect_args for multithreading in FastAPI / Streamlit
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(32), primary_key=True, index=True)
    customer_id = Column(String(32), nullable=False, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(120), nullable=False)
    customer_tier = Column(String(20), default="Standard")  # Standard, Silver, Gold, Platinum
    hotel_name = Column(String(150), nullable=False)
    hotel_city = Column(String(80), nullable=False)
    check_in_date = Column(String(10), nullable=False)   # YYYY-MM-DD
    check_out_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    booking_status = Column(String(20), default="confirmed")  # confirmed, pending, cancelled
    payment_status = Column(String(20), default="paid")        # paid, pending, refunded, failed
    total_amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    cancellation_eligible = Column(Boolean, default=True)
    refund_eligible_amount = Column(Float, default=0.0)
    room_type = Column(String(50), default="Deluxe King Room")
    special_requests = Column(String(255), default="None")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_tier": self.customer_tier,
            "hotel_name": self.hotel_name,
            "hotel_city": self.hotel_city,
            "check_in_date": self.check_in_date,
            "check_out_date": self.check_out_date,
            "booking_status": self.booking_status,
            "payment_status": self.payment_status,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "cancellation_eligible": self.cancellation_eligible,
            "refund_eligible_amount": self.refund_eligible_amount,
            "room_type": self.room_type,
            "special_requests": self.special_requests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(32), primary_key=True, index=True)
    booking_id = Column(String(32), nullable=True, index=True)
    customer_id = Column(String(32), nullable=True)
    customer_name = Column(String(100), nullable=True)
    customer_tier = Column(String(20), default="Standard")
    customer_message = Column(Text, nullable=False)
    predicted_intent = Column(String(50), default="general_travel_query")
    intent_confidence = Column(Float, default=0.0)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    priority_score = Column(Integer, default=50)
    priority_reasons = Column(Text, default="[]")     # JSON array string
    status = Column(String(30), default="open")      # open, auto_approved, pending_human_review, approved, rejected, escalated, closed
    draft_response = Column(Text, nullable=True)
    final_response = Column(Text, nullable=True)
    auditor_passed = Column(Boolean, default=False)
    auditor_findings = Column(Text, default="{}")    # JSON dict string
    escalation_reason = Column(Text, nullable=True)
    human_reviewer = Column(String(100), nullable=True)
    human_review_notes = Column(Text, nullable=True)
    execution_trace = Column(Text, default="[]")      # JSON array of node transitions
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_tier": self.customer_tier,
            "customer_message": self.customer_message,
            "predicted_intent": self.predicted_intent,
            "intent_confidence": self.intent_confidence,
            "priority": self.priority,
            "priority_score": self.priority_score,
            "priority_reasons": json.loads(self.priority_reasons) if self.priority_reasons else [],
            "status": self.status,
            "draft_response": self.draft_response,
            "final_response": self.final_response,
            "auditor_passed": self.auditor_passed,
            "auditor_findings": json.loads(self.auditor_findings) if self.auditor_findings else {},
            "escalation_reason": self.escalation_reason,
            "human_reviewer": self.human_reviewer,
            "human_review_notes": self.human_review_notes,
            "execution_trace": json.loads(self.execution_trace) if self.execution_trace else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(32), ForeignKey("tickets.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    actor = Column(String(80), nullable=False)
    details = Column(Text, default="")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(32), ForeignKey("tickets.id"), nullable=False, index=True)
    decision = Column(String(20), nullable=False)  # approve, reject, revise
    reviewer_name = Column(String(100), default="Support Supervisor")
    reviewer_notes = Column(Text, default="")
    original_draft = Column(Text, default="")
    edited_draft = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "decision": self.decision,
            "reviewer_name": self.reviewer_name,
            "reviewer_notes": self.reviewer_notes,
            "original_draft": self.original_draft,
            "edited_draft": self.edited_draft,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def init_db():
    """Initializes SQLite database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI and service dependency for acquiring a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
