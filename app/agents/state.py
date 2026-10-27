"""
State definition for the LangGraph Ticket Resolution Workflow.
Uses TypedDict to define explicit, type-safe data transitions across workflow nodes.
"""

from typing import TypedDict, Optional, List, Dict, Any


class TicketWorkflowState(TypedDict, total=False):
    # Ticket Metadata & Input
    ticket_id: str
    customer_message: str
    booking_id: Optional[str]
    customer_id: Optional[str]
    customer_name: Optional[str]
    customer_tier: Optional[str]

    # Intake & ML Classification
    predicted_intent: str
    classification_confidence: float
    intent_probabilities: Dict[str, float]

    # Prioritization
    priority: str  # low, medium, high, critical
    priority_score: int
    priority_reasons: List[str]

    # Booking Investigation
    booking_record: Optional[Dict[str, Any]]
    booking_found: bool

    # Knowledge Retrieval (RAG)
    policy_evidence: List[Dict[str, Any]]
    evidence_retrieval_mode: str

    # Resolution Drafting
    draft_resolution: Optional[str]
    draft_source: str  # 'llm' or 'deterministic_template'

    # Auditor Findings
    auditor_findings: Dict[str, Any]
    auditor_passed: bool

    # Routing & Escalation
    needs_human_review: bool
    escalation_reason: Optional[str]

    # Human Review
    human_approval_status: Optional[str]  # 'approved', 'rejected', 'revised', None
    reviewer_notes: Optional[str]
    human_reviewer: Optional[str]

    # Final Outcome & Observability
    final_status: str  # 'auto_approved', 'pending_human_review', 'approved', 'rejected', 'escalated'
    final_resolution: Optional[str]
    execution_trace: List[Dict[str, Any]]
    warnings: List[str]
    errors: List[str]
