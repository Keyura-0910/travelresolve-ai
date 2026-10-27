"""
LangGraph workflow nodes for TravelResolve AI.
Each node is a pure or state-transforming function operating on TicketWorkflowState.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
import re

from app.agents.state import TicketWorkflowState
from app.agents.tools import sanitize_booking_id, lookup_booking_tool
from app.agents.auditor import get_resolution_auditor
from app.agents.prompts import draft_resolution_with_llm
from app.ml.classifier import get_classifier
from app.ml.priority import calculate_ticket_priority
from app.rag.retriever import get_policy_retriever
from app.config import settings


def _add_trace(state: TicketWorkflowState, node_name: str, status: str, details: Dict[str, Any]):
    """Appends an execution step to the state's audit trace."""
    trace = state.get("execution_trace", [])
    trace.append({
        "node": node_name,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details
    })
    state["execution_trace"] = trace


# -----------------------------------------------------------------------------
# NODE 1: INTAKE & CLASSIFICATION
# -----------------------------------------------------------------------------
def node_intake_classification(state: TicketWorkflowState) -> TicketWorkflowState:
    message = state.get("customer_message", "").strip()
    
    # Check if a booking ID is embedded inside the customer message
    current_bid = state.get("booking_id")
    if not current_bid:
        extracted = sanitize_booking_id(message)
        if extracted:
            state["booking_id"] = extracted

    # Run ML Intent Classifier
    classifier = get_classifier()
    clf_res = classifier.predict(message)
    
    state["predicted_intent"] = clf_res.predicted_intent
    state["classification_confidence"] = clf_res.confidence
    state["intent_probabilities"] = clf_res.probabilities

    _add_trace(
        state,
        node_name="intake_classification",
        status="completed",
        details={
            "predicted_intent": clf_res.predicted_intent,
            "confidence": clf_res.confidence,
            "detected_booking_id": state.get("booking_id")
        }
    )
    return state


# -----------------------------------------------------------------------------
# NODE 2: BOOKING INVESTIGATION
# -----------------------------------------------------------------------------
def node_booking_investigation(state: TicketWorkflowState) -> TicketWorkflowState:
    bid = state.get("booking_id")
    cid = state.get("customer_id")
    booking_record = None

    if bid:
        booking_record = lookup_booking_tool(bid, customer_id=cid)

    if booking_record:
        state["booking_record"] = booking_record
        state["booking_found"] = True
        if not state.get("customer_name"):
            state["customer_name"] = booking_record.get("customer_name")
        if not state.get("customer_tier"):
            state["customer_tier"] = booking_record.get("customer_tier")
    else:
        state["booking_record"] = None
        state["booking_found"] = False

    # Compute rule-based priority with verified booking context
    priority_res = calculate_ticket_priority(
        intent=state.get("predicted_intent", "general_travel_query"),
        booking_context=booking_record,
        customer_tier=state.get("customer_tier", "Standard")
    )
    state["priority"] = priority_res.priority
    state["priority_score"] = priority_res.score
    state["priority_reasons"] = priority_res.reasons

    _add_trace(
        state,
        node_name="booking_investigation",
        status="completed",
        details={
            "booking_found": state["booking_found"],
            "booking_id": bid,
            "priority": priority_res.priority,
            "priority_score": priority_res.score,
            "priority_reasons": priority_res.reasons
        }
    )
    return state


# -----------------------------------------------------------------------------
# NODE 3: KNOWLEDGE RETRIEVAL (RAG)
# -----------------------------------------------------------------------------
def node_knowledge_retrieval(state: TicketWorkflowState) -> TicketWorkflowState:
    query = f"{state.get('predicted_intent', '')} {state.get('customer_message', '')}"
    retriever = get_policy_retriever()
    evidence = retriever.retrieve_evidence(query, top_k=settings.RAG_TOP_K)

    state["policy_evidence"] = evidence
    mode = evidence[0].get("retrieval_mode", "none") if evidence else "none"
    state["evidence_retrieval_mode"] = mode

    _add_trace(
        state,
        node_name="knowledge_retrieval",
        status="completed",
        details={
            "retrieved_count": len(evidence),
            "retrieval_mode": mode,
            "retrieved_policies": [e.get("policy_id") for e in evidence]
        }
    )
    return state


# -----------------------------------------------------------------------------
# NODE 4: RESOLUTION DRAFTING
# -----------------------------------------------------------------------------
def node_resolution_drafting(state: TicketWorkflowState) -> TicketWorkflowState:
    draft = draft_resolution_with_llm(
        customer_message=state.get("customer_message", ""),
        intent=state.get("predicted_intent", "general_travel_query"),
        confidence=state.get("classification_confidence", 1.0),
        booking_record=state.get("booking_record"),
        policy_evidence=state.get("policy_evidence", []),
        customer_name=state.get("customer_name")
    )
    state["draft_resolution"] = draft
    state["draft_source"] = "llm" if (settings.LLM_PROVIDER == "openai" and settings.LLM_API_KEY) else "deterministic_template"

    _add_trace(
        state,
        node_name="resolution_drafting",
        status="completed",
        details={"draft_source": state["draft_source"]}
    )
    return state


# -----------------------------------------------------------------------------
# NODE 5: RESOLUTION AUDITOR
# -----------------------------------------------------------------------------
def node_resolution_auditor(state: TicketWorkflowState) -> TicketWorkflowState:
    auditor = get_resolution_auditor()
    finding = auditor.audit_resolution(
        draft_text=state.get("draft_resolution", ""),
        booking_record=state.get("booking_record"),
        policy_evidence=state.get("policy_evidence", []),
        intent=state.get("predicted_intent", "general_travel_query")
    )
    state["auditor_findings"] = finding.model_dump()
    state["auditor_passed"] = finding.passed

    _add_trace(
        state,
        node_name="resolution_auditor",
        status="passed" if finding.passed else "failed",
        details={
            "passed": finding.passed,
            "violations_count": len(finding.violations),
            "violations": finding.violations,
            "grounded_claims": finding.grounded_claims
        }
    )
    return state


# -----------------------------------------------------------------------------
# NODE 6: ROUTING DECISION
# -----------------------------------------------------------------------------
def node_routing_decision(state: TicketWorkflowState) -> TicketWorkflowState:
    escalation_reasons: List[str] = []
    needs_review = False

    # Reason 1: Auditor failed
    if not state.get("auditor_passed", True):
        needs_review = True
        violations = state.get("auditor_findings", {}).get("violations", [])
        escalation_reasons.append(f"Auditor violation: {'; '.join(violations)}")

    # Reason 2: Low classification confidence
    conf = state.get("classification_confidence", 1.0)
    if conf < settings.CONFIDENCE_THRESHOLD_ESCALATION:
        needs_review = True
        escalation_reasons.append(f"Low intent classification confidence ({round(conf*100, 1)}% < {round(settings.CONFIDENCE_THRESHOLD_ESCALATION*100)}%).")

    # Reason 3: Booking provided but not found in DB
    if state.get("booking_id") and not state.get("booking_found", False):
        needs_review = True
        escalation_reasons.append(f"Booking reference '{state.get('booking_id')}' was not found in the reservation system.")

    # Reason 4: Sensitive actions (cancellation on non-refundable rate or high amount)
    booking = state.get("booking_record")
    intent = state.get("predicted_intent")
    if booking and intent in ["cancellation", "refund"]:
        if not booking.get("cancellation_eligible", True):
            needs_review = True
            escalation_reasons.append("Non-refundable reservation: requires supervisor policy override authorization.")
        if float(booking.get("total_amount", 0)) > 500.0:
            needs_review = True
            escalation_reasons.append("High financial exposure: refund/cancellation exceeds $500 threshold.")

    # Reason 5: Critical Priority with payment issues
    if state.get("priority") == "critical" and intent == "payment_issue":
        needs_review = True
        escalation_reasons.append("Critical priority payment failure: manual billing intervention needed.")

    state["needs_human_review"] = needs_review
    state["escalation_reason"] = " | ".join(escalation_reasons) if escalation_reasons else None
    
    if not needs_review:
        state["final_status"] = "auto_approved"
        state["final_resolution"] = state.get("draft_resolution")
    else:
        state["final_status"] = "pending_human_review"

    _add_trace(
        state,
        node_name="routing_decision",
        status="routed_to_human_review" if needs_review else "auto_approved",
        details={
            "needs_human_review": needs_review,
            "escalation_reason": state["escalation_reason"],
            "decision": "pending_human_review" if needs_review else "auto_approved"
        }
    )
    return state


# -----------------------------------------------------------------------------
# NODE 7: HUMAN REVIEW
# -----------------------------------------------------------------------------
def node_human_review(state: TicketWorkflowState) -> TicketWorkflowState:
    approval = state.get("human_approval_status")
    
    if approval == "approved":
        state["final_status"] = "approved"
        state["final_resolution"] = state.get("draft_resolution")
    elif approval == "revised":
        state["final_status"] = "approved"
        # If edited draft was provided, use that
        edited = state.get("reviewer_notes")
        state["final_resolution"] = edited or state.get("draft_resolution")
    elif approval == "rejected":
        state["final_status"] = "rejected"
        state["final_resolution"] = (
            "This automated resolution was rejected by a supervisor. "
            f"Reviewer notes: {state.get('reviewer_notes', 'Requires manual agent follow-up.')}"
        )
    else:
        # Paused awaiting human input
        state["final_status"] = "pending_human_review"

    _add_trace(
        state,
        node_name="human_review",
        status=state["final_status"],
        details={
            "approval_status": approval,
            "reviewer": state.get("human_reviewer"),
            "reviewer_notes": state.get("reviewer_notes")
        }
    )
    return state


# -----------------------------------------------------------------------------
# NODE 8: FINALIZATION
# -----------------------------------------------------------------------------
def node_finalization(state: TicketWorkflowState) -> TicketWorkflowState:
    if not state.get("final_resolution"):
        state["final_resolution"] = state.get("draft_resolution")

    _add_trace(
        state,
        node_name="finalization",
        status="completed",
        details={
            "final_status": state.get("final_status"),
            "has_resolution": bool(state.get("final_resolution"))
        }
    )
    return state
