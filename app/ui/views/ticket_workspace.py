"""
Ticket Workspace Page for TravelResolve.
Futuristic, floating customer support operations interface and agent resolution environment.
Developed by Keyura Motegaonkar.
"""

import streamlit as st
from app.database import SessionLocal
from app.schemas import TicketCreateRequest
from app.services.ticket_service import create_and_process_ticket

SAMPLE_SCENARIOS = {
    "-- Select an Inquiry Template --": {
        "message": "",
        "booking_id": "",
        "tier": "Standard"
    },
    "Template 1: Late Arrival Notice (TRV1025 - Imminent Check-in)": {
        "message": "My flight was delayed and I'll arrive after midnight. Can you confirm my late check-in at Grand Horizon Resort? Booking TRV1025.",
        "booking_id": "TRV1025",
        "tier": "Platinum"
    },
    "Template 2: Emergency Cancellation Request (TRV1026 - Non-Refundable)": {
        "message": "I need to cancel my trip to Aspen immediately and get a full refund due to a sudden family medical emergency. Booking TRV1026.",
        "booking_id": "TRV1026",
        "tier": "Standard"
    },
    "Template 3: Payment Notification Follow-up (TRV1030 - Failed Settlement)": {
        "message": "I received an alert that my payment failed for Urban Metropolitan Hotel TRV1030. How do I fix this before my room is released?",
        "booking_id": "TRV1030",
        "tier": "Gold"
    },
    "Template 4: Reschedule Dates Request (TRV1027 - Standard Schedule)": {
        "message": "We would like to reschedule our vacation dates by pushing check-in back two days for reservation TRV1027 in Kyoto.",
        "booking_id": "TRV1027",
        "tier": "Gold"
    },
    "Template 5: Unverified Booking Query (TRV9999 - Missing Record)": {
        "message": "Please cancel my reservation TRV9999 and refund my $800 payment immediately.",
        "booking_id": "TRV9999",
        "tier": "Standard"
    }
}


def render_ticket_workspace():
    # -------------------------------------------------------------------------
    # 1. Inquiry Intake Panel
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("#### 1. Inquiry Intake & Traveler Context")
        st.caption("Load a pre-configured traveler scenario or enter custom inquiry parameters.")

        selected_scenario_name = st.selectbox(
            "Quick-Load Inquiry Template",
            list(SAMPLE_SCENARIOS.keys()),
            help="Choose a pre-built traveler scenario to demonstrate intent classification and policy routing."
        )
        scenario_data = SAMPLE_SCENARIOS[selected_scenario_name]

        # Input Form
        with st.form("ticket_input_form"):
            col_id, col_tier = st.columns([2, 1])
            with col_id:
                input_bid = st.text_input(
                    "Booking Reference",
                    value=scenario_data["booking_id"],
                    placeholder="e.g. TRV1025 (Optional if inside message)"
                )
            with col_tier:
                input_tier = st.selectbox(
                    "Customer Loyalty Tier",
                    ["Standard", "Silver", "Gold", "Platinum"],
                    index=["Standard", "Silver", "Gold", "Platinum"].index(scenario_data["tier"])
                )

            input_msg = st.text_area(
                "Traveler Communication Message",
                value=scenario_data["message"],
                height=110,
                placeholder="Type customer message or select a template above..."
            )

            submit_btn = st.form_submit_button("⚡ Process Ticket Through LangGraph", type="primary", use_container_width=True)

    # -------------------------------------------------------------------------
    # 2. Execution & Resolution Results
    # -------------------------------------------------------------------------
    if submit_btn:
        if not input_msg.strip():
            st.error("Please enter a customer message or load an inquiry template.")
            return

        with st.spinner("Executing LangGraph DAG: Classifying intent, querying reservation database, and auditing policies..."):
            req = TicketCreateRequest(
                customer_message=input_msg.strip(),
                booking_id=input_bid.strip() if input_bid else None,
                customer_tier=input_tier
            )
            with SessionLocal() as db:
                result = create_and_process_ticket(req, db)

        st.success(f"Ticket processed successfully. Assigned Reference: **{result['ticket_id']}**")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 4 Core KPI Summary Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Predicted Intent", result["predicted_intent"].replace("_", " ").title())
        m2.metric("ML Confidence", f"{result['intent_confidence']:.1%}")

        prio_val = result["priority"].title()
        m3.metric("Urgency Level", f"{prio_val} ({result['priority_score']}/100)")

        status_display = {
            "auto_approved": "Auto-Approved",
            "pending_human_review": "Supervisor Review",
            "approved": "Supervisor Approved",
            "rejected": "Rejected"
        }.get(result["status"], result["status"])
        m4.metric("Workflow Gate", status_display)

        # Priority Scoring Factors in Clean Expander
        with st.expander("Priority Factors & Scoring Telemetry", expanded=False):
            for r in result["priority_reasons"]:
                st.markdown(f"• {r}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Two Columns: Booking Details vs Retrieved Policy Clauses
        col_b, col_p = st.columns([1, 1])
        with col_b:
            with st.container(border=True):
                st.markdown("#### Verified Reservation File")
                st.caption("Direct record query from primary SQLite database")

                b_ctx = result["booking_context"]
                if b_ctx:
                    st.markdown(
                        f"• **Booking Reference:** `{b_ctx['id']}`  \n"
                        f"• **Status:** `{b_ctx['booking_status'].upper()}`  \n"
                        f"• **Property:** {b_ctx['hotel_name']} ({b_ctx['hotel_city']})  \n"
                        f"• **Schedule:** {b_ctx['check_in_date']} to {b_ctx['check_out_date']}  \n"
                        f"• **Total Settlement:** ${b_ctx['total_amount']:.2f} {b_ctx['currency']} ({b_ctx['payment_status'].title()})  \n"
                        f"• **Rate Condition:** {'Flexible (Refundable)' if b_ctx['cancellation_eligible'] else 'Non-Refundable Fare'}"
                    )
                else:
                    st.info("No active reservation file found matching the reference.")

        with col_p:
            with st.container(border=True):
                st.markdown("#### Applicable Policy Guidelines")
                st.caption("Retrieved from FAISS dense vector repository")

                evidence = result.get("policy_evidence", [])
                if evidence:
                    for ev in evidence:
                        st.markdown(f"**{ev.get('title')} (`{ev.get('policy_id')}`)**")
                        st.caption(f"{ev.get('content')[:160]}...")
                else:
                    st.write("Standard customer service guidelines applied.")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Proposed Response Resolution Card
        with st.container(border=True):
            st.markdown("#### Proposed Response Resolution")
            st.caption("Generated using verified reservation data and policy constraints")

            st.text_area(
                "Draft Response",
                value=result["draft_response"] or "",
                height=150,
                disabled=True,
                label_visibility="collapsed"
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Policy Compliance & Verification Audit Card
        with st.container(border=True):
            st.markdown("#### Policy Compliance & Verification Audit")
            st.caption("Deterministic verification of factual entities, temporal schedule, and fare constraints")

            auditor = result.get("auditor_findings", {})
            if result["auditor_passed"]:
                st.info("Verification Passed: All dates, amounts, property names, and fare constraints match verified records.")
                claims = auditor.get("grounded_claims", [])
                if claims:
                    with st.expander("Verified Grounded Entities", expanded=False):
                        for c in claims:
                            st.markdown(f"✓ {c}")
            else:
                st.warning("Audit Flag: Policy discrepancies or exception limits detected requiring human authorization.")
                for v in auditor.get("violations", []):
                    st.markdown(f"• {v}")

            if result["status"] == "pending_human_review":
                st.warning(
                    f"**Routing Notice:** {result.get('escalation_reason')}  \n"
                    "This case has been intercepted and queued in the **Supervisor Review Queue**."
                )
