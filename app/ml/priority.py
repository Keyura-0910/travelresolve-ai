"""
Transparent, rule-based Ticket Priority Engine.
Calculates priority level ('low', 'medium', 'high', 'critical'), a numeric score (0-100),
and explicit, auditable business reasons.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.config import settings
from app.schemas import PriorityResult


def calculate_ticket_priority(
    intent: str,
    booking_context: Optional[Dict[str, Any]] = None,
    customer_tier: Optional[str] = "Standard",
    custom_urgency_flag: bool = False
) -> PriorityResult:
    """
    Computes priority using transparent business heuristics.
    
    Factors:
    - Time-to-checkin (hours remaining)
    - Booking and payment status (e.g., failed payment, pending confirmation)
    - Intent criticality (cancellation, payment_issue vs general query)
    - Customer Loyalty Tier (Platinum / Gold receive VIP priority boosts)
    """
    score = 30  # Baseline baseline score
    reasons: List[str] = []
    time_to_checkin_hours: Optional[float] = None

    # 1. Evaluate Time Remaining Until Check-In
    if booking_context and booking_context.get("check_in_date"):
        try:
            check_in_str = booking_context["check_in_date"]
            check_in_dt = datetime.strptime(check_in_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            now_dt = datetime.now(timezone.utc)
            delta = check_in_dt - now_dt
            time_to_checkin_hours = delta.total_seconds() / 3600.0

            if time_to_checkin_hours <= settings.PRIORITY_CRITICAL_CHECKIN_HOURS:
                if time_to_checkin_hours < 0:
                    score += 20
                    reasons.append("Check-in date is in the past / currently ongoing stay.")
                else:
                    score += 45
                    reasons.append(
                        f"Imminent check-in: arriving in {round(time_to_checkin_hours, 1)} hours "
                        f"(within {settings.PRIORITY_CRITICAL_CHECKIN_HOURS}h threshold)."
                    )
            elif time_to_checkin_hours <= settings.PRIORITY_HIGH_CHECKIN_HOURS:
                score += 25
                reasons.append(
                    f"Upcoming check-in: arriving in {round(time_to_checkin_hours / 24, 1)} days "
                    f"(within {settings.PRIORITY_HIGH_CHECKIN_HOURS}h window)."
                )
            else:
                reasons.append(f"Check-in is in {round(time_to_checkin_hours / 24, 1)} days (standard lead time).")
        except Exception:
            reasons.append("Check-in date format unparseable; standard schedule assumed.")

    # 2. Evaluate Booking and Payment Status
    if booking_context:
        payment_status = (booking_context.get("payment_status") or "").lower()
        booking_status = (booking_context.get("booking_status") or "").lower()

        if payment_status == "failed":
            score += 30
            reasons.append("Payment failed: risk of imminent automated booking cancellation.")
        elif payment_status == "pending":
            score += 15
            reasons.append("Payment pending: awaiting settlement confirmation.")

        if booking_status == "cancelled" and intent == "refund":
            score += 15
            reasons.append("Cancelled booking with active refund inquiry.")

    # 3. Intent Inherent Criticality
    intent_weights = {
        "payment_issue": 25,
        "cancellation": 20,
        "refund": 15,
        "booking_modification": 10,
        "booking_confirmation": 5,
        "general_travel_query": 0,
    }
    intent_score = intent_weights.get(intent, 0)
    score += intent_score
    if intent_score > 0:
        reasons.append(f"Intent severity weight (+{intent_score} pts) for '{intent}'.")

    # 4. Customer Loyalty Tier Priority
    tier = (customer_tier or "Standard").strip()
    if tier in settings.VIP_TIERS:
        score += 15
        reasons.append(f"VIP Loyalty Tier ({tier}): prioritized SLA routing.")
    elif tier == "Silver":
        score += 5
        reasons.append(f"Frequent traveler tier ({tier}).")

    if custom_urgency_flag:
        score += 10
        reasons.append("Customer flagged inquiry as urgent.")

    if not reasons:
        reasons.append("Standard default priority baseline applied.")

    # Cap score between 0 and 100
    final_score = max(0, min(100, score))

    # Derive Categorical Priority Level
    if final_score >= 80:
        level = "critical"
    elif final_score >= 60:
        level = "high"
    elif final_score >= 40:
        level = "medium"
    else:
        level = "low"

    return PriorityResult(
        priority=level,
        score=final_score,
        reasons=reasons,
        time_to_checkin_hours=round(time_to_checkin_hours, 1) if time_to_checkin_hours is not None else None
    )
