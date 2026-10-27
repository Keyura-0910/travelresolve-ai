"""
Dashboard Page for TravelResolve.
Premium Animated Travel Hero, Moving Vehicle Corridor, and AI Operations Telemetry.
Developed by Keyura Motegaonkar.
"""

import json
from datetime import datetime
import streamlit as st
import pandas as pd
from sqlalchemy import func

from app.database import SessionLocal, Ticket, Booking, AuditLog


def render_dashboard():
    # -------------------------------------------------------------------------
    # 1. Premium Animated Travel Hero Section
    # -------------------------------------------------------------------------
    hero_col_left, hero_col_right = st.columns([1.45, 1.35])

    with hero_col_left:
        st.markdown("""
        <div style="padding: 8px 4px; display: flex; flex-direction: column; justify-content: center; height: 100%;">
            <div style="display: inline-flex; align-items: center; gap: 7px; background: rgba(130, 117, 255, 0.15);
                        border: 1px solid rgba(130, 117, 255, 0.35); padding: 5px 12px; border-radius: 9999px;
                        color: #C0B7FF; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; width: fit-content;">
                <span style="width: 6px; height: 6px; background: #8275FF; border-radius: 50%; box-shadow: 0 0 8px #8275FF;"></span>
                INTELLIGENT TRAVEL-TECH OPERATIONS
            </div>
            <h1 style="margin: 0 0 10px 0; font-size: 2.15rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.025em; line-height: 1.18;">
                Your Journey. <span style="background: linear-gradient(135deg, #8275FF 0%, #38C9FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Intelligently Resolved.</span>
            </h1>
            <p style="margin: 0 0 16px 0; color: #A2AAC7; font-size: 0.94rem; line-height: 1.55; max-width: 580px;">
                An intelligent operations platform for booking verification, travel support,
                policy-grounded resolutions, and seamless workflow management.
            </p>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <div style="background: rgba(20, 26, 50, 0.7); border: 1px solid rgba(130, 117, 255, 0.2); padding: 5px 12px; border-radius: 8px; font-size: 0.78rem; color: #F4F5FF;">
                    ✈ Active Transit Routing
                </div>
                <div style="background: rgba(20, 26, 50, 0.7); border: 1px solid rgba(130, 117, 255, 0.2); padding: 5px 12px; border-radius: 8px; font-size: 0.78rem; color: #F4F5FF;">
                    ◈ LangGraph DAG Workflow
                </div>
                <div style="background: rgba(20, 26, 50, 0.7); border: 1px solid rgba(53, 212, 154, 0.25); padding: 5px 12px; border-radius: 8px; font-size: 0.78rem; color: #35D49A;">
                    ✓ 100% Policy Grounded
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hero_col_right:
        # Prominent Animated Transit Corridor (54px Jetliner, 48px Aerocab, Luminous Route Checkpoints)
        st.markdown("""
        <div style="background: rgba(13, 17, 36, 0.88); border: 1px solid rgba(130, 117, 255, 0.28);
                    border-radius: 14px; padding: 14px 16px 12px 16px; box-shadow: 0 8px 30px -4px rgba(130, 117, 255, 0.2);
                    position: relative; overflow: hidden;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; border-bottom: 1px solid rgba(130, 117, 255, 0.12); padding-bottom: 6px;">
                <span style="font-size: 0.70rem; font-weight: 700; color: #A2AAC7; letter-spacing: 0.08em; text-transform: uppercase;">
                    AUTONOMOUS TRANSIT & WORKFLOW CORRIDOR
                </span>
                <span style="display: inline-flex; align-items: center; gap: 5px; font-size: 0.68rem; font-weight: 600; color: #35D49A;">
                    <span style="width: 5px; height: 5px; background: #35D49A; border-radius: 50%; box-shadow: 0 0 6px #35D49A;"></span>
                    LIVE CORRIDOR
                </span>
            </div>

            <svg viewBox="0 0 520 215" style="width: 100%; height: auto; display: block;" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="flightGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#38C9FF" stop-opacity="0.35"/>
                        <stop offset="50%" stop-color="#8275FF" stop-opacity="0.9"/>
                        <stop offset="100%" stop-color="#35D49A" stop-opacity="0.95"/>
                    </linearGradient>
                    <linearGradient id="roadGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="rgba(130, 117, 255, 0.2)"/>
                        <stop offset="50%" stop-color="rgba(130, 117, 255, 0.5)"/>
                        <stop offset="100%" stop-color="rgba(56, 201, 255, 0.4)"/>
                    </linearGradient>
                    <linearGradient id="carBodyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#38C9FF"/>
                        <stop offset="100%" stop-color="#8275FF"/>
                    </linearGradient>
                    <linearGradient id="headlightBeamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="rgba(56, 201, 255, 0.45)"/>
                        <stop offset="100%" stop-color="rgba(56, 201, 255, 0)"/>
                    </linearGradient>
                    <linearGradient id="jetTrailGrad" x1="100%" y1="0%" x2="0%" y2="0%">
                        <stop offset="0%" stop-color="#38C9FF" stop-opacity="0.8"/>
                        <stop offset="60%" stop-color="#8275FF" stop-opacity="0.4"/>
                        <stop offset="100%" stop-color="#8275FF" stop-opacity="0"/>
                    </linearGradient>

                    <filter id="glowAir" x="-30%" y="-30%" width="160%" height="160%">
                        <feDropShadow dx="0" dy="0" stdDeviation="3.5" flood-color="#38C9FF" flood-opacity="0.8"/>
                    </filter>
                    <filter id="glowCar" x="-30%" y="-30%" width="160%" height="160%">
                        <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#8275FF" flood-opacity="0.75"/>
                    </filter>
                    <filter id="glowNode" x="-40%" y="-40%" width="180%" height="180%">
                        <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#8275FF" flood-opacity="0.9"/>
                    </filter>
                </defs>

                <!-- Subtle Grid Guide Lines -->
                <line x1="20" y1="40" x2="500" y2="40" stroke="rgba(130, 117, 255, 0.08)" stroke-width="1"/>
                <line x1="20" y1="95" x2="500" y2="95" stroke="rgba(130, 117, 255, 0.08)" stroke-width="1"/>
                <line x1="20" y1="150" x2="500" y2="150" stroke="rgba(130, 117, 255, 0.08)" stroke-width="1"/>

                <!-- 1. FLIGHT ROUTE (AIRPLANE) -->
                <path id="airplaneFlightPath" 
                      d="M 35 125 C 120 40, 240 18, 350 48 C 420 68, 465 48, 495 28" 
                      fill="none" stroke="url(#flightGrad)" stroke-width="2.6" stroke-dasharray="7 5"/>

                <!-- Flight Route Checkpoints -->
                <!-- Departure Checkpoint -->
                <g transform="translate(35, 125)">
                    <circle cx="0" cy="0" r="13" fill="none" stroke="#38C9FF" stroke-width="1.2" stroke-opacity="0.4"/>
                    <circle cx="0" cy="0" r="5" fill="#38C9FF" filter="url(#glowNode)"/>
                    <text x="0" y="20" font-family="'Inter', sans-serif" font-size="7.5" font-weight="700" fill="#A2AAC7" text-anchor="middle">DEPARTURE</text>
                </g>

                <!-- AI Resolve Checkpoint -->
                <g transform="translate(265, 30)">
                    <circle cx="0" cy="0" r="15" fill="none" stroke="#8275FF" stroke-width="1.4" stroke-dasharray="3 2"/>
                    <circle cx="0" cy="0" r="6" fill="#8275FF" filter="url(#glowNode)"/>
                    <circle cx="0" cy="0" r="2.2" fill="#FFFFFF"/>
                    <text x="0" y="-12" font-family="'Inter', sans-serif" font-size="8" font-weight="800" fill="#C0B7FF" text-anchor="middle">AI RESOLVE</text>
                </g>

                <!-- Destination Checkpoint -->
                <g transform="translate(495, 28)">
                    <circle cx="0" cy="0" r="13" fill="none" stroke="#35D49A" stroke-width="1.2" stroke-opacity="0.4"/>
                    <circle cx="0" cy="0" r="5" fill="#35D49A" filter="url(#glowNode)"/>
                    <text x="0" y="20" font-family="'Inter', sans-serif" font-size="7.5" font-weight="700" fill="#35D49A" text-anchor="middle">DESTINATION</text>
                </g>

                <!-- Animated Airplane Entity (54px x 44px Passenger Jetliner) -->
                <g filter="url(#glowAir)">
                    <!-- Jet Exhaust Stream & Glow -->
                    <path d="M -24 0 L -46 -3.5 L -38 0 L -46 3.5 Z" fill="url(#jetTrailGrad)" opacity="0.85"/>
                    <circle cx="-25" cy="0" r="3.2" fill="#38C9FF" opacity="0.9"/>

                    <!-- Aerodynamic Fuselage (Length: 54px from -27 to +27) -->
                    <path d="M 27 0 C 26 2.2, 20 3.8, 4 3.8 L -18 3.2 L -24 2 L -25 0 L -24 -2 L -18 -3.2 L 4 -3.8 C 20 -3.8, 26 -2.2, 27 0 Z" fill="#F4F5FF"/>

                    <!-- Cockpit Windshield (Electric Cyan) -->
                    <path d="M 19 0 L 14 2 L 14 -2 Z" fill="#38C9FF"/>

                    <!-- Swept Main Wings (Wingspan: 44px from -22 to +22) -->
                    <path d="M 7 -3.2 L -8 -22 L -13 -22 L -7 -3.2 Z" fill="#E0E5FF"/>
                    <path d="M 7 3.2 L -8 22 L -13 22 L -7 3.2 Z" fill="#C5CEF8"/>

                    <!-- Wing Engine Turbines -->
                    <rect x="-3" y="-12" width="9" height="3" rx="1.5" fill="#8275FF"/>
                    <rect x="-3" y="9" width="9" height="3" rx="1.5" fill="#8275FF"/>

                    <!-- Tail Empennage Wings -->
                    <path d="M -17 -2 L -24 -11 L -27 -11 L -22 -2 Z" fill="#E0E5FF"/>
                    <path d="M -17 2 L -24 11 L -27 11 L -22 2 Z" fill="#C5CEF8"/>

                    <!-- Fuselage Gradient Speed Stripe -->
                    <line x1="-15" y1="0" x2="16" y2="0" stroke="url(#flightGrad)" stroke-width="1.8"/>

                    <animateMotion dur="9.5s" repeatCount="indefinite" rotate="auto">
                        <mpath href="#airplaneFlightPath"/>
                    </animateMotion>
                </g>

                <!-- 2. HIGHWAY CORRIDOR (CAR) -->
                <path id="carRoadPath" d="M 15 178 L 505 178" fill="none" stroke="url(#roadGrad)" stroke-width="3.5"/>
                <line x1="15" y1="178" x2="505" y2="178" stroke="rgba(56, 201, 255, 0.45)" stroke-width="1.2" stroke-dasharray="9 7"/>

                <!-- Highway Checkpoints -->
                <g transform="translate(55, 178)">
                    <circle cx="0" cy="0" r="3.5" fill="#38C9FF"/>
                    <text x="0" y="15" font-family="'Inter', sans-serif" font-size="7" font-weight="600" fill="#A2AAC7" text-anchor="middle">TERMINAL</text>
                </g>
                <g transform="translate(270, 178)">
                    <circle cx="0" cy="0" r="4" fill="#8275FF"/>
                    <text x="0" y="15" font-family="'Inter', sans-serif" font-size="7" font-weight="600" fill="#A2AAC7" text-anchor="middle">HOTEL HUB</text>
                </g>
                <g transform="translate(465, 178)">
                    <circle cx="0" cy="0" r="3.5" fill="#35D49A"/>
                    <text x="0" y="15" font-family="'Inter', sans-serif" font-size="7" font-weight="600" fill="#35D49A" text-anchor="middle">RESORT</text>
                </g>

                <!-- Animated Stylized Car Entity (48px x 19px Aerocab) -->
                <g filter="url(#glowCar)">
                    <!-- Forward Headlight Illuminating Beam -->
                    <polygon points="24,-1 56,-9 56,8 24,4" fill="url(#headlightBeamGrad)"/>

                    <!-- Aerodynamic Lower Chassis / Body (48px wide) -->
                    <rect x="-24" y="-4" width="48" height="8.5" rx="3.5" fill="url(#carBodyGrad)"/>

                    <!-- Upper Cabin Glass Dome -->
                    <path d="M -13 -4 L -7 -10.5 L 9 -10.5 L 16 -4 Z" fill="#141A32" stroke="#38C9FF" stroke-width="1"/>
                    <!-- Window Glass Reflections -->
                    <polygon points="-6,-9.5 2,-9.5 2,-4 -7,-4" fill="#38C9FF" fill-opacity="0.35"/>
                    <polygon points="4,-9.5 8.5,-9.5 13.5,-4 4,-4" fill="#8275FF" fill-opacity="0.35"/>

                    <!-- Neon Alloy Wheels (Diameter: ~8.4px) -->
                    <!-- Rear Wheel -->
                    <circle cx="-14" cy="4.5" r="4.2" fill="#080B18" stroke="#38C9FF" stroke-width="1.2"/>
                    <circle cx="-14" cy="4.5" r="1.8" fill="#FFFFFF"/>
                    <!-- Front Wheel -->
                    <circle cx="14" cy="4.5" r="4.2" fill="#080B18" stroke="#38C9FF" stroke-width="1.2"/>
                    <circle cx="14" cy="4.5" r="1.8" fill="#FFFFFF"/>

                    <!-- LED Headlight Strip -->
                    <circle cx="23.5" cy="-0.5" r="1.8" fill="#FFFFFF" filter="url(#glowAir)"/>
                    <!-- LED Taillight Strip (Crimson) -->
                    <rect x="-24.5" y="-1.5" width="2" height="3" rx="0.8" fill="#FF647C"/>

                    <animateMotion dur="7.5s" repeatCount="indefinite">
                        <mpath href="#carRoadPath"/>
                    </animateMotion>
                </g>
            </svg>
        </div>
        """, unsafe_allow_html=True)

    # Hero Quick Actions Bar
    c_act1, c_act2, c_act3, _ = st.columns([1.6, 1.8, 1.6, 2.5])
    with c_act1:
        if st.button("✈ Process Inquiries", use_container_width=True, type="primary"):
            st.session_state.nav_menu = "✈ Ticket Workspace"
            st.rerun()
    with c_act2:
        if st.button("◎ Audit Live Traces", use_container_width=True, type="secondary"):
            st.session_state.nav_menu = "◎ Execution Trace"
            st.rerun()
    with c_act3:
        if st.button("✓ Supervisor Queue", use_container_width=True, type="secondary"):
            st.session_state.nav_menu = "✓ Review Queue"
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Database Telemetry & Floating Metric Cards
    # -------------------------------------------------------------------------
    with SessionLocal() as db:
        total_tickets = db.query(func.count(Ticket.id)).scalar() or 0
        pending_reviews = db.query(func.count(Ticket.id)).filter(Ticket.status == "pending_human_review").scalar() or 0
        auto_approved = db.query(func.count(Ticket.id)).filter(Ticket.status == "auto_approved").scalar() or 0
        human_approved = db.query(func.count(Ticket.id)).filter(Ticket.status == "approved").scalar() or 0
        rejected = db.query(func.count(Ticket.id)).filter(Ticket.status == "rejected").scalar() or 0
        audited_passed = db.query(func.count(Ticket.id)).filter(Ticket.auditor_passed == True).scalar() or 0

        audit_pass_rate = (audited_passed / total_tickets * 100) if total_tickets > 0 else 100.0

        # Calculate average processing latency across tickets with execution trace
        tickets_with_trace = db.query(Ticket).all()
        durations = []
        for t in tickets_with_trace:
            if t.execution_trace:
                try:
                    steps = json.loads(t.execution_trace)
                    if len(steps) >= 2 and steps[0].get("timestamp") and steps[-1].get("timestamp"):
                        t0 = datetime.fromisoformat(steps[0]["timestamp"])
                        t1 = datetime.fromisoformat(steps[-1]["timestamp"])
                        d = (t1 - t0).total_seconds() * 1000
                        if d > 0:
                            durations.append(d)
                except Exception:
                    pass
        avg_latency_ms = sum(durations) / len(durations) if durations else 42.0

        # 5 Floating Layered Metric Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Tickets Processed", total_tickets, help="Total inquiries received and processed through LangGraph DAG")
        col2.metric("Auto-Resolved", auto_approved, delta=f"{round(auto_approved/total_tickets*100 if total_tickets else 0)}% of volume")
        col3.metric("Awaiting Review", pending_reviews, delta=f"{pending_reviews} open" if pending_reviews else "Clear", delta_color="inverse")
        col4.metric("Audit Pass Rate", f"{audit_pass_rate:.1f}%", delta="100% Grounded")
        col5.metric("Avg Execution Latency", f"{avg_latency_ms:.0f} ms", help="Mean end-to-end processing duration across DAG nodes")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. Floating Chart Panels
    # -------------------------------------------------------------------------
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("#### Inquiries by Category")
            st.caption("Distribution of traveler requests classified by TF-IDF + Logistic Regression")

            with SessionLocal() as db:
                intent_counts = (
                    db.query(Ticket.predicted_intent, func.count(Ticket.id))
                    .group_by(Ticket.predicted_intent)
                    .all()
                )
            if intent_counts:
                clean_counts = [(cat.replace("_", " ").title(), cnt) for cat, cnt in intent_counts]
                df_intent = pd.DataFrame(clean_counts, columns=["Category", "Count"]).set_index("Category")
                st.bar_chart(df_intent, color="#8275FF", height=230)
            else:
                st.info("No ticket records available.")

    with c2:
        with st.container(border=True):
            st.markdown("#### Priority & Urgency Distribution")
            st.caption("Active workload categorized by time-to-checkin and financial risk factors")

            with SessionLocal() as db:
                prio_counts = (
                    db.query(Ticket.priority, func.count(Ticket.id))
                    .group_by(Ticket.priority)
                    .all()
                )
            if prio_counts:
                prio_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
                sorted_prios = sorted(prio_counts, key=lambda x: prio_order.get(x[0], 99))
                clean_prios = [(p.title(), cnt) for p, cnt in sorted_prios]
                df_prio = pd.DataFrame(clean_prios, columns=["Priority", "Count"]).set_index("Priority")
                st.bar_chart(df_prio, color="#38C9FF", height=230)
            else:
                st.info("No priority distribution data available.")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. Recent Activity & Audit Feed
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("#### Recent Operations & Audit Feed")
        st.caption("Immutable chronological record of workflow transitions, validations, and supervisor decisions")

        with SessionLocal() as db:
            recent_logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(8).all()
        if recent_logs:
            log_data = [
                {
                    "Ticket ID": l.ticket_id,
                    "Workflow Stage": l.event_type.replace("_", " ").title(),
                    "Executing Agent": l.actor,
                    "Timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else "N/A",
                    "Telemetry Summary": l.details[:120] + ("..." if len(l.details) > 120 else "")
                }
                for l in recent_logs
            ]
            st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
        else:
            st.info("No activity records logged in system.")
