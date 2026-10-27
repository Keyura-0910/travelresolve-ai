"""
Review Queue Page for TravelResolve.
Supervisor review and exception handling portal.
Developed by Keyura Motegaonkar.
"""

import streamlit as st
from app.database import SessionLocal, Ticket, Booking
from app.schemas import HumanReviewRequest
from app.services.review_service import submit_human_review


def render_review_queue():
    with SessionLocal() as db:
        pending_tickets = (
            db.query(Ticket)
            .filter(Ticket.status == "pending_human_review")
            .order_by(Ticket.priority_score.desc(), Ticket.created_at.asc())
            .all()
        )

    if not pending_tickets:
        with st.container(border=True):
            st.markdown("#### Review Queue Clear")
            st.caption("All escalated tickets have been reviewed. There are no pending supervisory actions.")
        return

    st.markdown(f"**Open Cases Requiring Review:** `{len(pending_tickets)}`")

    for t in pending_tickets:
        with st.container(border=True):
            c_header_left, c_header_right = st.columns([3, 1])
            with c_header_left:
                st.markdown(f"#### Case Reference: `{t.id}`")
                st.caption(f"Customer: {t.customer_name or 'Traveler'} | Tier: {t.customer_tier}")
            with c_header_right:
                st.markdown(f"**Priority:** `{t.priority.upper()}` ({t.priority_score}/100)")

            st.warning(f"**Escalation Trigger:** {t.escalation_reason or 'Supervisory policy review required.'}")

            # Entire interactive review workflow wrapped inside st.form to guarantee stable inputs and atomic submit
            with st.form(f"review_form_{t.id}"):
                col_msg, col_draft = st.columns(2)

                with col_msg:
                    st.markdown("**Customer Communication:**")
                    st.caption("Original traveler inquiry. Editable by supervisor for PII redaction or clarification.")
                    cust_msg = st.text_area(
                        "Customer Message",
                        value=t.customer_message or "",
                        height=140,
                        key=f"msg_{t.id}",
                        label_visibility="collapsed",
                        help="Original traveler inquiry message. You can edit this text directly if corrections or PII redaction are required."
                    )

                    # Booking details snapshot
                    if t.booking_id:
                        with SessionLocal() as db:
                            b = db.query(Booking).filter(Booking.id == t.booking_id).first()
                            if b:
                                st.info(
                                    f"• **Booking:** `{b.id}` | {b.hotel_name}  \n"
                                    f"• **Dates:** {b.check_in_date} to {b.check_out_date}  \n"
                                    f"• **Amount:** ${b.total_amount:.2f} {b.currency} | **Rate:** {'Flexible (Refundable)' if b.cancellation_eligible else 'Non-Refundable Fare'}"
                                )

                with col_draft:
                    st.markdown("**Proposed Response Resolution:**")
                    st.caption("AI-generated draft resolution. Fully editable by supervisor before authorization.")
                    draft_resp = st.text_area(
                        f"Proposed Draft ({t.id})",
                        value=t.draft_response or "",
                        height=200,
                        key=f"draft_{t.id}",
                        label_visibility="collapsed",
                        help="Supervisor-editable resolution text. Changes made here will be applied directly as the authorized response."
                    )

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("**Supervisor Review & Authorization:**")

                c_act, c_name = st.columns([1, 1])
                with c_act:
                    decision = st.selectbox(
                        "Decision",
                        ["approve", "revise", "reject"],
                        format_func=lambda x: {
                            "approve": "Approve Resolution",
                            "revise": "Edit and Approve",
                            "reject": "Reject Resolution"
                        }[x],
                        key=f"dec_{t.id}",
                        help="Choose supervisory action: Approve (with current draft), Edit and Approve (with custom revisions), or Reject."
                    )
                with c_name:
                    reviewer = st.text_input(
                        "Reviewer Name",
                        value="Keyura Motegaonkar (Supervisor)",
                        key=f"rev_{t.id}",
                        help="Supervisor identity recorded in the permanent audit trail."
                    )

                notes = st.text_input(
                    "Justification Notes",
                    placeholder="e.g., Authorized one-time accommodation voucher per policy EXC-402.",
                    key=f"notes_{t.id}",
                    help="Mandatory notes explaining the policy override, justification, or rejection rationale."
                )

                submit_btn = st.form_submit_button("Submit Supervisory Decision", type="primary", use_container_width=True)

                if submit_btn:
                    if not reviewer.strip():
                        st.error("Please enter a valid Reviewer Name before submitting.")
                    else:
                        req = HumanReviewRequest(
                            decision=decision,
                            reviewer_name=reviewer.strip(),
                            reviewer_notes=notes.strip(),
                            edited_draft=draft_resp.strip() if draft_resp else None
                        )
                        with SessionLocal() as db:
                            # Update customer message if modified
                            ticket_db = db.query(Ticket).filter(Ticket.id == t.id).first()
                            if ticket_db and cust_msg.strip() and cust_msg.strip() != (t.customer_message or "").strip():
                                ticket_db.customer_message = cust_msg.strip()
                                db.commit()

                            res = submit_human_review(t.id, req, db)
                        st.success(f"Case {t.id} successfully updated. Status: {res['final_status'].upper()}.")
                        st.rerun()
