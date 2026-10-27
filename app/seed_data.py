"""
Synthetic travel dataset generator and database seeder.
Generates reproducible, realistic bookings, tickets, and audit records with
dates relative to the current execution time.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import Booking, Ticket, AuditLog, HumanReview, init_db, SessionLocal


def generate_seed_data(session: Session) -> dict:
    """Populates the database with realistic synthetic travel records."""
    today = datetime.now(timezone.utc)
    
    # Clear existing data to ensure clean, reproducible seed
    session.query(HumanReview).delete()
    session.query(AuditLog).delete()
    session.query(Ticket).delete()
    session.query(Booking).delete()
    session.commit()

    # ---------------------------------------------------------------------
    # 1. Synthetic Bookings
    # ---------------------------------------------------------------------
    bookings_data = [
        Booking(
            id="TRV1025",
            customer_id="CUST-801",
            customer_name="Elena Rostova",
            customer_email="elena.rostova@example.com",
            customer_tier="Platinum",
            hotel_name="Grand Horizon Resort & Spa",
            hotel_city="Miami, USA",
            check_in_date=(today + timedelta(days=1)).strftime("%Y-%m-%d"),   # Urgent check-in (24 hrs)
            check_out_date=(today + timedelta(days=4)).strftime("%Y-%m-%d"),
            booking_status="confirmed",
            payment_status="paid",
            total_amount=1240.00,
            currency="USD",
            cancellation_eligible=True,
            refund_eligible_amount=1240.00,
            room_type="Ocean View King Suite",
            special_requests="High floor, late check-in requested",
        ),
        Booking(
            id="TRV1026",
            customer_id="CUST-802",
            customer_name="Marcus Vance",
            customer_email="marcus.vance@example.com",
            customer_tier="Standard",
            hotel_name="Alpine Pine Lodge",
            hotel_city="Aspen, USA",
            check_in_date=(today + timedelta(days=2)).strftime("%Y-%m-%d"),   # High priority check-in (48 hrs)
            check_out_date=(today + timedelta(days=6)).strftime("%Y-%m-%d"),
            booking_status="confirmed",
            payment_status="paid",
            total_amount=890.50,
            currency="USD",
            cancellation_eligible=False,  # Non-refundable rate
            refund_eligible_amount=0.0,
            room_type="Standard Double Queen",
            special_requests="Quiet room near elevator",
        ),
        Booking(
            id="TRV1027",
            customer_id="CUST-803",
            customer_name="Priya Sharma",
            customer_email="priya.sharma@example.com",
            customer_tier="Gold",
            hotel_name="The Kyoto Blossom Ryokan",
            hotel_city="Kyoto, Japan",
            check_in_date=(today + timedelta(days=12)).strftime("%Y-%m-%d"),
            check_out_date=(today + timedelta(days=16)).strftime("%Y-%m-%d"),
            booking_status="pending",
            payment_status="pending",
            total_amount=1450.00,
            currency="USD",
            cancellation_eligible=True,
            refund_eligible_amount=0.0,  # Not yet paid
            room_type="Traditional Garden View Room",
            special_requests="Vegetarian breakfast requested",
        ),
        Booking(
            id="TRV1028",
            customer_id="CUST-804",
            customer_name="Liam Gallagher",
            customer_email="liam.g@example.com",
            customer_tier="Silver",
            hotel_name="Canal Bridge Hotel",
            hotel_city="Amsterdam, Netherlands",
            check_in_date=(today - timedelta(days=2)).strftime("%Y-%m-%d"),   # Past check-in, cancelled
            check_out_date=(today + timedelta(days=1)).strftime("%Y-%m-%d"),
            booking_status="cancelled",
            payment_status="refunded",
            total_amount=560.00,
            currency="USD",
            cancellation_eligible=False,
            refund_eligible_amount=0.0,
            room_type="Standard Single",
            special_requests="None",
        ),
        Booking(
            id="TRV1029",
            customer_id="CUST-805",
            customer_name="Sofia Chen",
            customer_email="sofia.chen@example.com",
            customer_tier="Standard",
            hotel_name="Sapphire Bay Resort",
            hotel_city="Cancun, Mexico",
            check_in_date=(today + timedelta(days=20)).strftime("%Y-%m-%d"),
            check_out_date=(today + timedelta(days=25)).strftime("%Y-%m-%d"),
            booking_status="confirmed",
            payment_status="paid",
            total_amount=1820.00,
            currency="USD",
            cancellation_eligible=True,
            refund_eligible_amount=1820.00,
            room_type="Beachfront Villa",
            special_requests="Honeymoon setup",
        ),
        Booking(
            id="TRV1030",
            customer_id="CUST-806",
            customer_name="David Kim",
            customer_email="david.kim@example.com",
            customer_tier="Gold",
            hotel_name="Urban Metropolitan Hotel",
            hotel_city="London, UK",
            check_in_date=(today + timedelta(days=5)).strftime("%Y-%m-%d"),
            check_out_date=(today + timedelta(days=9)).strftime("%Y-%m-%d"),
            booking_status="confirmed",
            payment_status="failed",
            total_amount=780.00,
            currency="USD",
            cancellation_eligible=False,
            refund_eligible_amount=0.0,
            room_type="Executive King",
            special_requests="Early check-in 11 AM",
        ),
    ]
    
    session.add_all(bookings_data)
    session.flush()

    # ---------------------------------------------------------------------
    # 2. Seed Initial Tickets Demonstrating Diverse Workflow States
    # ---------------------------------------------------------------------
    t1_base = today - timedelta(hours=3)
    t2_base = today - timedelta(hours=2)
    t3_base = today - timedelta(hours=1)
    t4_base = today - timedelta(minutes=30)

    import json

    trace_tck1001 = json.dumps([
        {
            "node": "intake_classification",
            "status": "completed",
            "timestamp": (t1_base + timedelta(milliseconds=45)).isoformat(),
            "details": {
                "predicted_intent": "booking_confirmation",
                "confidence": 0.96,
                "detected_booking_id": "TRV1025"
            }
        },
        {
            "node": "booking_investigation",
            "status": "completed",
            "timestamp": (t1_base + timedelta(milliseconds=180)).isoformat(),
            "details": {
                "booking_found": True,
                "booking_id": "TRV1025",
                "priority": "critical",
                "priority_score": 92,
                "priority_reasons": ["Check-in within 24 hours (tomorrow)", "VIP Platinum Tier member", "Late arrival confirmation request"]
            }
        },
        {
            "node": "knowledge_retrieval",
            "status": "completed",
            "timestamp": (t1_base + timedelta(milliseconds=310)).isoformat(),
            "details": {
                "retrieved_count": 3,
                "retrieval_mode": "faiss_vector",
                "retrieved_policies": ["POL-CHECKIN-01", "POL-HOTEL-OPS-03", "POL-VIP-BENEFITS-02"]
            }
        },
        {
            "node": "resolution_drafting",
            "status": "completed",
            "timestamp": (t1_base + timedelta(milliseconds=540)).isoformat(),
            "details": {
                "draft_source": "deterministic_template",
                "draft_preview": "Dear Elena Rostova, your confirmed booking TRV1025 at Grand Horizon Resort & Spa has been noted for late arrival. The front desk operates 24/7..."
            }
        },
        {
            "node": "resolution_auditor",
            "status": "passed",
            "timestamp": (t1_base + timedelta(milliseconds=620)).isoformat(),
            "details": {
                "passed": True,
                "violations_count": 0,
                "violations": [],
                "grounded_claims": ["Booking TRV1025 confirmed", "Grand Horizon Resort & Spa matches record", "Check-in is tomorrow"]
            }
        },
        {
            "node": "routing_decision",
            "status": "auto_approved",
            "timestamp": (t1_base + timedelta(milliseconds=690)).isoformat(),
            "details": {
                "needs_human_review": False,
                "escalation_reason": None,
                "decision": "auto_approved"
            }
        }
    ])

    trace_tck1002 = json.dumps([
        {
            "node": "intake_classification",
            "status": "completed",
            "timestamp": (t2_base + timedelta(milliseconds=50)).isoformat(),
            "details": {
                "predicted_intent": "cancellation",
                "confidence": 0.94,
                "detected_booking_id": "TRV1026"
            }
        },
        {
            "node": "booking_investigation",
            "status": "completed",
            "timestamp": (t2_base + timedelta(milliseconds=195)).isoformat(),
            "details": {
                "booking_found": True,
                "booking_id": "TRV1026",
                "priority": "high",
                "priority_score": 78,
                "priority_reasons": ["Check-in within 48 hours", "Cancellation request on non-refundable reservation"]
            }
        },
        {
            "node": "knowledge_retrieval",
            "status": "completed",
            "timestamp": (t2_base + timedelta(milliseconds=330)).isoformat(),
            "details": {
                "retrieved_count": 3,
                "retrieval_mode": "faiss_vector",
                "retrieved_policies": ["POL-CANCEL-NONREF-01", "POL-COMPASSIONATE-04", "POL-ESC-02"]
            }
        },
        {
            "node": "resolution_drafting",
            "status": "completed",
            "timestamp": (t2_base + timedelta(milliseconds=580)).isoformat(),
            "details": {
                "draft_source": "deterministic_template",
                "draft_preview": "Hello Marcus, we investigated booking TRV1026 for Alpine Pine Lodge. According to the fare rules, this was booked under a non-refundable tier..."
            }
        },
        {
            "node": "resolution_auditor",
            "status": "passed",
            "timestamp": (t2_base + timedelta(milliseconds=660)).isoformat(),
            "details": {
                "passed": True,
                "violations_count": 0,
                "violations": [],
                "grounded_claims": ["TRV1026 non-refundable status verified", "Alpine Pine Lodge verified"]
            }
        },
        {
            "node": "routing_decision",
            "status": "routed_to_human_review",
            "timestamp": (t2_base + timedelta(milliseconds=720)).isoformat(),
            "details": {
                "needs_human_review": True,
                "escalation_reason": "Non-refundable reservation: requires supervisor policy override authorization.",
                "decision": "pending_human_review"
            }
        }
    ])

    trace_tck1003 = json.dumps([
        {
            "node": "intake_classification",
            "status": "completed",
            "timestamp": (t3_base + timedelta(milliseconds=40)).isoformat(),
            "details": {
                "predicted_intent": "payment_issue",
                "confidence": 0.95,
                "detected_booking_id": "TRV1030"
            }
        },
        {
            "node": "booking_investigation",
            "status": "completed",
            "timestamp": (t3_base + timedelta(milliseconds=175)).isoformat(),
            "details": {
                "booking_found": True,
                "booking_id": "TRV1030",
                "priority": "high",
                "priority_score": 75,
                "priority_reasons": ["Payment status is failed", "Check-in in 5 days", "Risk of automated reservation cancellation"]
            }
        },
        {
            "node": "knowledge_retrieval",
            "status": "completed",
            "timestamp": (t3_base + timedelta(milliseconds=305)).isoformat(),
            "details": {
                "retrieved_count": 2,
                "retrieval_mode": "faiss_vector",
                "retrieved_policies": ["POL-PAYMENT-RETRY-02", "POL-GRACE-PERIOD-01"]
            }
        },
        {
            "node": "resolution_drafting",
            "status": "completed",
            "timestamp": (t3_base + timedelta(milliseconds=530)).isoformat(),
            "details": {
                "draft_source": "deterministic_template",
                "draft_preview": "Dear David Kim, your booking TRV1030 at Urban Metropolitan Hotel shows a payment failure for $780.00 USD..."
            }
        },
        {
            "node": "resolution_auditor",
            "status": "passed",
            "timestamp": (t3_base + timedelta(milliseconds=610)).isoformat(),
            "details": {
                "passed": True,
                "violations_count": 0,
                "violations": [],
                "grounded_claims": ["Payment failed verified", "$780.00 USD matches total", "Urban Metropolitan Hotel matches"]
            }
        },
        {
            "node": "routing_decision",
            "status": "auto_approved",
            "timestamp": (t3_base + timedelta(milliseconds=675)).isoformat(),
            "details": {
                "needs_human_review": False,
                "escalation_reason": None,
                "decision": "auto_approved"
            }
        }
    ])

    trace_tck1004 = json.dumps([
        {
            "node": "intake_classification",
            "status": "completed",
            "timestamp": (t4_base + timedelta(milliseconds=38)).isoformat(),
            "details": {
                "predicted_intent": "booking_modification",
                "confidence": 0.29,
                "detected_booking_id": None
            }
        },
        {
            "node": "booking_investigation",
            "status": "completed",
            "timestamp": (t4_base + timedelta(milliseconds=160)).isoformat(),
            "details": {
                "booking_found": False,
                "booking_id": None,
                "priority": "medium",
                "priority_score": 45,
                "priority_reasons": ["Low confidence prediction", "No booking ID provided in inquiry"]
            }
        },
        {
            "node": "knowledge_retrieval",
            "status": "completed",
            "timestamp": (t4_base + timedelta(milliseconds=290)).isoformat(),
            "details": {
                "retrieved_count": 2,
                "retrieval_mode": "faiss_vector",
                "retrieved_policies": ["POL-MODIFICATION-GENERAL-01", "POL-INQUIRY-INFO-02"]
            }
        },
        {
            "node": "resolution_drafting",
            "status": "completed",
            "timestamp": (t4_base + timedelta(milliseconds=490)).isoformat(),
            "details": {
                "draft_source": "deterministic_template",
                "draft_preview": "Hello Claire, thank you for reaching out regarding your travel plans. To assist with reviewing date changes or options, could you please provide your booking reference number?"
            }
        },
        {
            "node": "resolution_auditor",
            "status": "passed",
            "timestamp": (t4_base + timedelta(milliseconds=560)).isoformat(),
            "details": {
                "passed": True,
                "violations_count": 0,
                "violations": [],
                "grounded_claims": ["Clarification request for booking ID"]
            }
        },
        {
            "node": "routing_decision",
            "status": "routed_to_human_review",
            "timestamp": (t4_base + timedelta(milliseconds=630)).isoformat(),
            "details": {
                "needs_human_review": True,
                "escalation_reason": "Low intent classification confidence (29.0% < 35%). Requires human clarification.",
                "decision": "pending_human_review"
            }
        }
    ])

    tickets_data = [
        Ticket(
            id="TCK-1001",
            booking_id="TRV1025",
            customer_id="CUST-801",
            customer_name="Elena Rostova",
            customer_tier="Platinum",
            customer_message="My flight is delayed and I'll arrive after midnight. Can you confirm my late check-in at Grand Horizon Resort?",
            predicted_intent="booking_confirmation",
            intent_confidence=0.96,
            priority="critical",
            priority_score=92,
            priority_reasons='["Check-in within 24 hours (tomorrow)", "VIP Platinum Tier member", "Late arrival confirmation request"]',
            status="auto_approved",
            draft_response="Dear Elena Rostova, your confirmed booking TRV1025 at Grand Horizon Resort & Spa has been noted for late arrival. The front desk operates 24/7 and your Ocean View King Suite will be held for your arrival after midnight.",
            final_response="Dear Elena Rostova, your confirmed booking TRV1025 at Grand Horizon Resort & Spa has been noted for late arrival. The front desk operates 24/7 and your Ocean View King Suite will be held for your arrival after midnight.",
            auditor_passed=True,
            auditor_findings='{"passed": true, "violations": [], "grounded_claims": ["Booking TRV1025 confirmed", "Grand Horizon Resort & Spa matches record", "Check-in is tomorrow"], "hallucination_detected": false}',
            escalation_reason=None,
            human_reviewer=None,
            human_review_notes=None,
            execution_trace=trace_tck1001
        ),
        Ticket(
            id="TCK-1002",
            booking_id="TRV1026",
            customer_id="CUST-802",
            customer_name="Marcus Vance",
            customer_tier="Standard",
            customer_message="I need to cancel my trip to Aspen immediately and get a full refund due to a family emergency.",
            predicted_intent="cancellation",
            intent_confidence=0.94,
            priority="high",
            priority_score=78,
            priority_reasons='["Check-in within 48 hours", "Cancellation request on non-refundable reservation"]',
            status="pending_human_review",
            draft_response="Hello Marcus, we investigated booking TRV1026 for Alpine Pine Lodge. According to the fare rules, this was booked under a non-refundable tier. However, for family emergencies, our policy permits escalating to a supervisor for an exceptional voucher review.",
            final_response=None,
            auditor_passed=True,
            auditor_findings='{"passed": true, "violations": [], "grounded_claims": ["TRV1026 non-refundable status verified", "Alpine Pine Lodge verified"], "hallucination_detected": false}',
            escalation_reason="Sensitive policy override: Non-refundable cancellation requested due to compassionate grounds (family emergency). Requires supervisor review.",
            human_reviewer=None,
            human_review_notes=None,
            execution_trace=trace_tck1002
        ),
        Ticket(
            id="TCK-1003",
            booking_id="TRV1030",
            customer_id="CUST-806",
            customer_name="David Kim",
            customer_tier="Gold",
            customer_message="I received a notification saying my payment failed for Urban Metropolitan Hotel. How can I fix this before my reservation gets cancelled?",
            predicted_intent="payment_issue",
            intent_confidence=0.95,
            priority="high",
            priority_score=75,
            priority_reasons='["Payment status is failed", "Check-in in 5 days", "Risk of automated reservation cancellation"]',
            status="auto_approved",
            draft_response="Dear David Kim, your booking TRV1030 at Urban Metropolitan Hotel shows a payment failure for $780.00 USD. Your reservation is temporarily held for 24 hours. Please access the secure payment update portal in your account to retry or update your card details.",
            final_response="Dear David Kim, your booking TRV1030 at Urban Metropolitan Hotel shows a payment failure for $780.00 USD. Your reservation is temporarily held for 24 hours. Please access the secure payment update portal in your account to retry or update your card details.",
            auditor_passed=True,
            auditor_findings='{"passed": true, "violations": [], "grounded_claims": ["Payment failed verified", "$780.00 USD matches total", "Urban Metropolitan Hotel matches"], "hallucination_detected": false}',
            escalation_reason=None,
            human_reviewer=None,
            human_review_notes=None,
            execution_trace=trace_tck1003
        ),
        Ticket(
            id="TCK-1004",
            booking_id=None,
            customer_id="CUST-807",
            customer_name="Claire Underwood",
            customer_tier="Standard",
            customer_message="Is it possible maybe to reconsider the dates or do something with that trip?",
            predicted_intent="booking_modification",
            intent_confidence=0.29,
            priority="medium",
            priority_score=45,
            priority_reasons='["Low confidence prediction (29%)", "No booking ID provided in inquiry"]',
            status="pending_human_review",
            draft_response="Hello Claire, thank you for reaching out regarding your travel plans. To assist with reviewing date changes or options, could you please provide your booking reference number?",
            final_response=None,
            auditor_passed=True,
            auditor_findings='{"passed": true, "violations": [], "grounded_claims": ["Clarification request for booking ID"], "hallucination_detected": false}',
            escalation_reason="Low intent classification confidence (29.0% < 35%). Requires human clarification.",
            human_reviewer=None,
            human_review_notes=None,
            execution_trace=trace_tck1004
        )
    ]
    
    session.add_all(tickets_data)
    session.flush()

    # ---------------------------------------------------------------------
    # 3. Seed Audit Logs
    # ---------------------------------------------------------------------
    audit_data = [
        AuditLog(
            ticket_id="TCK-1001",
            event_type="INTAKE_CLASSIFICATION",
            actor="ML_Classifier",
            details="Classified as booking_confirmation (conf: 0.96). Priority: CRITICAL (score: 92) due to check-in <24h and Platinum tier.",
        ),
        AuditLog(
            ticket_id="TCK-1001",
            event_type="BOOKING_INVESTIGATION",
            actor="BookingLookupTool",
            details="Successfully retrieved TRV1025. Status: confirmed, Hotel: Grand Horizon Resort & Spa.",
        ),
        AuditLog(
            ticket_id="TCK-1001",
            event_type="AUDITOR_CHECK",
            actor="ResolutionAuditor",
            details="All 5 verification checks passed. Dates and hotel name exactly match verified database record.",
        ),
        AuditLog(
            ticket_id="TCK-1002",
            event_type="INTAKE_CLASSIFICATION",
            actor="ML_Classifier",
            details="Classified as cancellation (conf: 0.94). Priority: HIGH (score: 78).",
        ),
        AuditLog(
            ticket_id="TCK-1002",
            event_type="ROUTING_DECISION",
            actor="LangGraphRouter",
            details="Non-refundable refund exception requested. Routed to Human Review queue for supervisor authorization.",
        ),
    ]
    
    session.add_all(audit_data)
    session.commit()
    
    return {
        "bookings_seeded": len(bookings_data),
        "tickets_seeded": len(tickets_data),
        "audit_logs_seeded": len(audit_data),
    }


if __name__ == "__main__":
    init_db()
    with SessionLocal() as db:
        stats = generate_seed_data(db)
        print(f"Synthetic database successfully seeded: {stats}")
