"""
Pydantic schemas for data validation and API request/response contracts.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Booking Schemas
# -------------------------------------------------------------------------
class BookingBase(BaseModel):
    id: str = Field(..., description="Unique booking ID, e.g., TRV1025")
    customer_id: str
    customer_name: str
    customer_email: str
    customer_tier: str = "Standard"
    hotel_name: str
    hotel_city: str
    check_in_date: str
    check_out_date: str
    booking_status: str
    payment_status: str
    total_amount: float
    currency: str = "USD"
    cancellation_eligible: bool = True
    refund_eligible_amount: float = 0.0
    room_type: str = "Deluxe King Room"
    special_requests: str = "None"


class BookingResponse(BookingBase):
    created_at: Optional[str] = None


# -------------------------------------------------------------------------
# Intent Classification & Priority Schemas
# -------------------------------------------------------------------------
class ClassificationResult(BaseModel):
    predicted_intent: str
    confidence: float
    probabilities: Dict[str, float]
    model_name: str = "TFIDF-LogisticRegression"


class PriorityResult(BaseModel):
    priority: str  # low, medium, high, critical
    score: int
    reasons: List[str]
    time_to_checkin_hours: Optional[float] = None


# -------------------------------------------------------------------------
# Auditor Schemas
# -------------------------------------------------------------------------
class AuditorFinding(BaseModel):
    passed: bool
    checks_performed: List[str]
    violations: List[str]
    grounded_claims: List[str]
    hallucination_detected: bool
    summary: str


# -------------------------------------------------------------------------
# Ticket Schemas
# -------------------------------------------------------------------------
class TicketCreateRequest(BaseModel):
    customer_message: str = Field(..., min_length=3, description="Customer request message")
    booking_id: Optional[str] = Field(None, description="Optional booking reference, e.g., TRV1025")
    customer_id: Optional[str] = Field(None, description="Customer ID if known")
    customer_name: Optional[str] = Field(None, description="Customer name if known")
    customer_tier: Optional[str] = Field("Standard", description="Customer loyalty tier: Standard, Silver, Gold, Platinum")


class ExecutionTraceNode(BaseModel):
    node: str
    timestamp: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class TicketProcessResponse(BaseModel):
    ticket_id: str
    booking_id: Optional[str] = None
    customer_message: str
    predicted_intent: str
    intent_confidence: float
    priority: str
    priority_score: int
    priority_reasons: List[str]
    status: str
    draft_response: Optional[str] = None
    final_response: Optional[str] = None
    booking_context: Optional[Dict[str, Any]] = None
    policy_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    auditor_findings: Optional[Dict[str, Any]] = None
    auditor_passed: bool = False
    escalation_reason: Optional[str] = None
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)


class TicketDetailResponse(BaseModel):
    id: str
    booking_id: Optional[str]
    customer_id: Optional[str]
    customer_name: Optional[str]
    customer_tier: str
    customer_message: str
    predicted_intent: str
    intent_confidence: float
    priority: str
    priority_score: int
    priority_reasons: List[str]
    status: str
    draft_response: Optional[str]
    final_response: Optional[str]
    auditor_passed: bool
    auditor_findings: Dict[str, Any]
    escalation_reason: Optional[str]
    human_reviewer: Optional[str]
    human_review_notes: Optional[str]
    execution_trace: List[Dict[str, Any]]
    created_at: Optional[str]
    updated_at: Optional[str]


# -------------------------------------------------------------------------
# Human Review Schemas
# -------------------------------------------------------------------------
class HumanReviewRequest(BaseModel):
    decision: str = Field(..., pattern="^(approve|reject|revise)$", description="'approve', 'reject', or 'revise'")
    reviewer_name: str = "Support Supervisor"
    reviewer_notes: str = ""
    edited_draft: Optional[str] = None


class HumanReviewResponse(BaseModel):
    review_id: int
    ticket_id: str
    decision: str
    reviewer_name: str
    reviewer_notes: str
    final_status: str
    updated_at: str


# -------------------------------------------------------------------------
# Audit Log Schemas
# -------------------------------------------------------------------------
class AuditLogResponse(BaseModel):
    id: int
    ticket_id: str
    event_type: str
    actor: str
    details: str
    timestamp: str


# -------------------------------------------------------------------------
# Evaluation Schemas
# -------------------------------------------------------------------------
class EvaluationMetricsResponse(BaseModel):
    total_cases_evaluated: int
    intent_accuracy: float
    intent_macro_f1: float
    retrieval_recall_at_k: float
    booking_field_accuracy: float
    escalation_precision: float
    escalation_recall: float
    eligible_resolution_rate: float
    average_latency_ms: float
    system_comparison: Dict[str, Any]
    notes: List[str]
