"""
Execution Trace Page for TravelResolve.
Futuristic, step-by-step workflow state transitions, node validations, and routing decisions.
Developed by Keyura Motegaonkar.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd

from app.database import SessionLocal, Ticket
from app.config import settings


def _format_node_name(node_key: str) -> str:
    """Formats raw internal DAG node key into enterprise-friendly title."""
    mapping = {
        "intake_classification": "Intake & Classification",
        "booking_investigation": "Booking Investigation & Priority",
        "knowledge_retrieval": "Knowledge Retrieval (RAG)",
        "resolution_drafting": "Resolution Drafting",
        "resolution_auditor": "Resolution Auditor & Verification",
        "routing_decision": "Routing Decision & Policy Gates",
        "human_review": "Supervisor Review & Override",
        "finalization": "Case Finalization & Delivery"
    }
    return mapping.get(node_key, node_key.replace("_", " ").title())


def _status_badge_html(status: str) -> str:
    """Returns styled dark-theme luminous badge for step status."""
    st_lower = status.lower()
    if st_lower in ["completed", "passed", "auto_approved", "approved"]:
        bg = "rgba(53, 212, 154, 0.15)"
        color = "#35D49A"
        border = "rgba(53, 212, 154, 0.45)"
        glow = "0 0 10px rgba(53, 212, 154, 0.25)"
        label = "COMPLETED" if st_lower == "completed" else ("PASSED" if st_lower == "passed" else "APPROVED")
    elif st_lower in ["routed_to_human_review", "pending_human_review", "needs_review", "warning"]:
        bg = "rgba(255, 199, 106, 0.15)"
        color = "#FFC76A"
        border = "rgba(255, 199, 106, 0.45)"
        glow = "0 0 10px rgba(255, 199, 106, 0.25)"
        label = "REVIEW REQUIRED"
    elif st_lower in ["failed", "rejected", "error"]:
        bg = "rgba(255, 100, 124, 0.15)"
        color = "#FF647C"
        border = "rgba(255, 100, 124, 0.45)"
        glow = "0 0 10px rgba(255, 100, 124, 0.25)"
        label = "FAILED" if st_lower == "failed" else "REJECTED"
    else:
        bg = "rgba(130, 117, 255, 0.15)"
        color = "#C0B7FF"
        border = "rgba(130, 117, 255, 0.45)"
        glow = "0 0 10px rgba(130, 117, 255, 0.25)"
        label = status.upper().replace("_", " ")

    return (
        f'<span style="background: {bg}; color: {color}; border: 1px solid {border}; '
        f'box-shadow: {glow}; padding: 4px 10px; border-radius: 6px; font-size: 0.72rem; '
        f'font-weight: 700; letter-spacing: 0.05em;">{label}</span>'
    )


def _render_step_summary(node_key: str, status: str, details: Dict[str, Any], ticket: Ticket):
    """Renders human-readable, domain-specific summary of actions taken in the step."""
    if node_key == "intake_classification":
        intent = details.get("predicted_intent", ticket.predicted_intent).replace("_", " ").title()
        conf = details.get("confidence", ticket.intent_confidence)
        bid = details.get("detected_booking_id", ticket.booking_id)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"• **Classified Intent:** `{intent}`")
            st.markdown(f"• **Classification Confidence:** `{conf:.1%}`")
        with c2:
            st.markdown(f"• **Extracted Booking ID:** `{bid or 'None embedded in message'}`")
            st.markdown(f"• **Model:** TF-IDF Vectorizer + Multinomial Logistic Regression")

        # Low-Confidence Scenario Alert
        threshold = settings.CONFIDENCE_THRESHOLD_ESCALATION
        if conf < threshold:
            st.warning(
                f"**Low Confidence Warning:** Predicted confidence ({conf:.1%}) is below the automated approval "
                f"threshold ({threshold:.1%}). Routing gate intercepted inquiry for supervisor review."
            )

    elif node_key == "booking_investigation":
        found = details.get("booking_found", bool(ticket.booking_id))
        bid = details.get("booking_id", ticket.booking_id)
        prio = details.get("priority", ticket.priority).title()
        score = details.get("priority_score", ticket.priority_score)
        reasons = details.get("priority_reasons", [])
        if isinstance(reasons, str):
            try:
                reasons = json.loads(reasons)
            except Exception:
                reasons = [reasons]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"• **Reservation Verification:** `{'Verified in Database' if found else 'No Matching Record'}`")
            st.markdown(f"• **Queried Reference:** `{bid or 'N/A'}`")
        with c2:
            st.markdown(f"• **Calculated Urgency:** `{prio}` (Score: **{score}/100**)")
            st.markdown(f"• **Customer Tier:** `{ticket.customer_tier or 'Standard'}`")

        if reasons:
            st.markdown("**Priority Scoring Factors:**")
            for r in reasons:
                st.markdown(f"- {r}")

    elif node_key == "knowledge_retrieval":
        count = details.get("retrieved_count", 0)
        mode = details.get("retrieval_mode", "faiss_vector")
        policies = details.get("retrieved_policies", [])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"• **Retrieved Policy Chunks:** `{count}`")
            mode_display = "FAISS Vector Search" if "faiss" in mode.lower() else "Deterministic Lexical BM25 Fallback"
            st.markdown(f"• **Retrieval Mode:** `{mode_display}`")
        with c2:
            st.markdown(f"• **Policies Cited:** {', '.join([f'`{p}`' for p in policies]) if policies else 'Standard guidelines'}")

    elif node_key == "resolution_drafting":
        source = details.get("draft_source", "deterministic_template")
        source_display = "Hosted LLM API" if source == "llm" else "Deterministic Grounded Template"
        st.markdown(f"• **Generation Engine:** `{source_display}`")
        preview = details.get("draft_preview")
        if not preview and ticket.draft_response:
            preview = ticket.draft_response[:220] + ("..." if len(ticket.draft_response) > 220 else "")
        if preview:
            st.markdown(f"• **Draft Content Preview:**  \n> *\"{preview}\"*")

    elif node_key == "resolution_auditor":
        passed = details.get("passed", ticket.auditor_passed)
        violations = details.get("violations", [])
        claims = details.get("grounded_claims", [])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"• **Deterministic Audit:** `{'Passed (5/5 Checks)' if passed else 'Audit Failed'}`")
            st.markdown(f"• **Rule Violations Detected:** `{len(violations)}`")
        with c2:
            st.markdown(f"• **Grounded Claim Verifications:** `{len(claims)} verified facts`")

        if violations:
            st.error("**Audit Violations Detected:**")
            for v in violations:
                st.markdown(f"- {v}")
        elif claims:
            with st.expander("Verified Grounded Entities", expanded=False):
                for c in claims:
                    st.markdown(f"✓ {c}")

    elif node_key == "routing_decision":
        needs_review = details.get("needs_human_review", ticket.status == "pending_human_review")
        decision = details.get("decision", ticket.status)
        escalation_reason = details.get("escalation_reason", ticket.escalation_reason)

        if needs_review:
            st.warning(
                f"**Routed to Supervisor Review Queue**  \n"
                f"• **Escalation Reason:** {escalation_reason or 'Supervisory policy override required.'}  \n"
                f"• **Recommended Action:** Supervisor must review traveler's request and authorize or edit the draft in the Review Queue."
            )
        else:
            st.success(
                f"**Auto-Approval Granted**  \n"
                f"• **Verification Gate:** All deterministic auditor checks passed. Factual entities match database records.  \n"
                f"• **Autonomous Action:** Resolution released directly to traveler without manual intervention."
            )

    elif node_key == "human_review":
        approval = details.get("approval_status", ticket.status)
        reviewer = details.get("reviewer", ticket.human_reviewer or "Supervisor")
        notes = details.get("reviewer_notes", ticket.human_review_notes or "None provided")

        st.markdown(f"• **Supervisory Decision:** `{approval.upper()}`")
        st.markdown(f"• **Authorized Reviewer:** `{reviewer}`")
        if notes:
            st.markdown(f"• **Supervisor Notes:** {notes}")

    elif node_key == "finalization":
        f_status = details.get("final_status", ticket.status)
        has_res = details.get("has_resolution", bool(ticket.final_response or ticket.draft_response))
        st.markdown(f"• **Final Case Status:** `{f_status.upper()}`")
        st.markdown(f"• **Resolution Dispatched:** `{'Yes' if has_res else 'Pending'}`")


def render_execution_trace():
    with SessionLocal() as db:
        tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()

    if not tickets:
        st.info("No tickets recorded yet.")
        return

    # Clean Ticket Selector
    ticket_options = {
        f"{t.id} — {t.customer_name or 'Traveler'} ({t.predicted_intent.replace('_', ' ').title()}) [{t.status.upper()}]": t.id
        for t in tickets
    }
    selected_label = st.selectbox(
        "Select Ticket Reference",
        list(ticket_options.keys()),
        help="Choose a ticket to inspect its complete execution trace and state progression."
    )
    selected_id = ticket_options[selected_label]

    with SessionLocal() as db:
        ticket = db.query(Ticket).filter(Ticket.id == selected_id).first()

    if not ticket:
        st.error("Ticket record not found.")
        return

    # Parse trace steps
    trace_raw = ticket.execution_trace
    trace_steps: List[Dict[str, Any]] = json.loads(trace_raw) if trace_raw else []

    # Calculate summary metrics
    total_steps = len(trace_steps)
    completed_steps = sum(1 for s in trace_steps if s.get("status") in ["completed", "passed", "auto_approved", "approved"])
    failed_steps = sum(1 for s in trace_steps if s.get("status") in ["failed", "rejected"])
    review_steps = sum(1 for s in trace_steps if s.get("status") in ["routed_to_human_review", "pending_human_review"])

    # Compute execution duration
    total_duration_ms: Optional[float] = None
    if trace_steps:
        t_start_raw = trace_steps[0].get("timestamp")
        t_end_raw = trace_steps[-1].get("timestamp")
        if t_start_raw and t_end_raw:
            try:
                dt_start = datetime.fromisoformat(t_start_raw)
                dt_end = datetime.fromisoformat(t_end_raw)
                total_duration_ms = max(0.0, (dt_end - dt_start).total_seconds() * 1000)
            except Exception:
                total_duration_ms = None

    # -------------------------------------------------------------------------
    # 1. Top Workflow Summary Container
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("#### Workflow Execution Telemetry")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Steps", total_steps)
        m2.metric("Completed Steps", completed_steps)
        m3.metric("Review Triggers", review_steps)
        m4.metric("Failed Steps", failed_steps)

        duration_display = f"{total_duration_ms:.0f} ms" if total_duration_ms is not None else "N/A"
        m5.metric("Total Latency", duration_display)

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        c_meta1, c_meta2, c_meta3 = st.columns([1.5, 1.5, 1.5])
        with c_meta1:
            st.markdown(f"**Case Reference:** `{ticket.id}`")
        with c_meta2:
            st.markdown(f"**Booking ID:** `{ticket.booking_id or 'None'}`")
        with c_meta3:
            st.markdown(f"**Workflow Status:** `{ticket.status.upper()}`")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Chronological Step Progression (Timeline Cards)
    # -------------------------------------------------------------------------
    st.markdown("#### Chronological DAG State Progression")
    st.caption("Step-by-step state transitions, node validations, and parameter outputs across the LangGraph DAG.")

    if not trace_steps:
        st.info("No execution trace steps recorded for this case.")
    else:
        for idx, step in enumerate(trace_steps, 1):
            node_key = step.get("node", f"step_{idx}")
            formatted_name = _format_node_name(node_key)
            status = step.get("status", "completed")
            raw_ts = step.get("timestamp", "")
            details = step.get("details", {})

            # Clean timestamp formatting
            ts_display = "N/A"
            if raw_ts:
                try:
                    dt = datetime.fromisoformat(raw_ts)
                    ts_display = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"
                except Exception:
                    ts_display = raw_ts[:19].replace("T", " ")

            # Subtle connecting line before step (except first)
            if idx > 1:
                st.markdown("""
                <div style="display: flex; justify-content: flex-start; padding-left: 28px; height: 14px;">
                    <div style="width: 2px; height: 100%; background: linear-gradient(180deg, rgba(130, 117, 255, 0.4) 0%, rgba(56, 201, 255, 0.2) 100%);"></div>
                </div>
                """, unsafe_allow_html=True)

            # Native bordered container for each step card
            with st.container(border=True):
                # Header Row: Step Number & Title on Left, Status Badge on Right
                c_title, c_badge = st.columns([3, 1.2])
                with c_title:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #8275FF; font-weight: 700; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;">
                            STEP {idx:02d}
                        </span>
                        <span style="color: rgba(130, 117, 255, 0.4);">•</span>
                        <span style="color: #F4F5FF; font-weight: 700; font-size: 1.05rem;">
                            {formatted_name}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                with c_badge:
                    badge_html = _status_badge_html(status)
                    st.markdown(f"<div style='text-align: right;'>{badge_html}</div>", unsafe_allow_html=True)

                # Meta Row: Timestamp
                st.caption(f"Timestamp: `{ts_display}`")

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

                # Body: Domain-specific human summary
                _render_step_summary(node_key, status, details, ticket)

                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

                # Expandable Technical Details (Closed by Default)
                with st.expander("View technical details", expanded=False):
                    st.json(details)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. Serialized Database Record
    # -------------------------------------------------------------------------
    with st.expander("View full serialized database record", expanded=False):
        st.json(ticket.to_dict())
