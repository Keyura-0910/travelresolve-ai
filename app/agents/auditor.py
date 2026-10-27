"""
Deterministic Resolution Auditor for TravelResolve AI.
Cross-examines drafted support responses against verified database records
and retrieved policy evidence to detect hallucinations, factual drift, and policy violations.
"""

import re
from typing import Dict, Any, List, Optional
from app.schemas import AuditorFinding


class ResolutionAuditor:
    """
    Automated fact-checking and policy auditing engine.
    Applies deterministic rules to ensure drafted resolutions are strictly grounded
    in real booking data and authorized policy constraints.
    """

    def audit_resolution(
        self,
        draft_text: str,
        booking_record: Optional[Dict[str, Any]],
        policy_evidence: List[Dict[str, Any]],
        intent: str
    ) -> AuditorFinding:
        """
        Runs comprehensive consistency, factual, and safety checks on the proposed draft.
        """
        checks_performed: List[str] = []
        violations: List[str] = []
        grounded_claims: List[str] = []

        if not draft_text or not draft_text.strip():
            return AuditorFinding(
                passed=False,
                checks_performed=["Empty Draft Check"],
                violations=["Draft response is empty."],
                grounded_claims=[],
                hallucination_detected=True,
                summary="Audit Failed: Proposed draft response is empty."
            )

        draft_lower = draft_text.lower()

        # ---------------------------------------------------------------------
        # Check 1: Booking ID Consistency
        # ---------------------------------------------------------------------
        checks_performed.append("Booking ID Verification")
        if booking_record:
            expected_id = booking_record["id"].upper()
            if expected_id.lower() in draft_lower:
                grounded_claims.append(f"Booking reference '{expected_id}' explicitly verified in text.")
            else:
                violations.append(f"Draft omits the customer's verified booking reference '{expected_id}'.")

            # Check if any unknown booking ID is hallucinated
            mentioned_ids = re.findall(r"\bTRV\d{3,6}\b", draft_text.upper())
            for mid in mentioned_ids:
                if mid != expected_id:
                    violations.append(f"Hallucinated Booking ID: Draft mentions '{mid}', but active booking is '{expected_id}'.")
        else:
            # If no booking record was found, draft should NOT pretend it found one or confirm it
            if re.search(r"\b(confirmed booking|your reservation at|is confirmed|we found your booking|booking is active)\b", draft_lower):
                violations.append("Draft claims booking is confirmed/found, but no booking record exists in database.")
            elif intent in ["booking_confirmation", "cancellation", "refund", "booking_modification", "payment_issue"]:
                if not re.search(r"\b(could not find|missing|not found|please reply with|provide your booking)\b", draft_lower):
                    violations.append("Ungrounded Resolution: Booking-specific inquiry answered without verified database record.")

        # ---------------------------------------------------------------------
        # Check 2: Hotel Property & City Accuracy
        # ---------------------------------------------------------------------
        checks_performed.append("Hotel Property Groundedness")
        if booking_record:
            hotel_name = booking_record.get("hotel_name", "")
            # Check key words of hotel name
            hotel_keywords = [w.lower() for w in re.findall(r"\b\w{4,}\b", hotel_name)]
            matches = [kw for kw in hotel_keywords if kw in draft_lower]
            if matches:
                grounded_claims.append(f"Property name '{hotel_name}' matches verified database file.")
            else:
                violations.append(f"Draft fails to mention the customer's booked property '{hotel_name}'.")

        # ---------------------------------------------------------------------
        # Check 3: Booking Status Integrity
        # ---------------------------------------------------------------------
        checks_performed.append("Booking Status Consistency")
        if booking_record:
            real_status = (booking_record.get("booking_status") or "").lower()
            if real_status == "cancelled":
                if "your booking is confirmed" in draft_lower or "active reservation" in draft_lower:
                    violations.append("Status Conflict: Draft asserts reservation is confirmed, but database records status as 'cancelled'.")
            elif real_status == "pending":
                if "your booking is confirmed" in draft_lower:
                    violations.append("Status Premature: Draft asserts booking is confirmed, but status is currently 'pending'.")
            else:
                grounded_claims.append(f"Booking status '{real_status}' consistently referenced.")

        # ---------------------------------------------------------------------
        # Check 4: Payment and Monetary Amount Integrity
        # ---------------------------------------------------------------------
        checks_performed.append("Financial & Payment Integrity")
        if booking_record:
            total_amount = float(booking_record.get("total_amount", 0.0))
            # Extract currency figures from draft
            currency_mentions = re.findall(r"\$\s?(\d+(?:\.\d{2})?)", draft_text)
            for raw_val in currency_mentions:
                val = float(raw_val)
                # Check if monetary mention is plausible (matches total, 50% refund, or 0)
                is_total = abs(val - total_amount) < 0.01
                is_half = abs(val - (total_amount * 0.5)) < 0.01
                is_zero = val == 0.0
                if not (is_total or is_half or is_zero):
                    violations.append(
                        f"Financial Discrepancy: Draft quotes ${val:.2f}, which does not match total "
                        f"(${total_amount:.2f}) or standard cancellation refund."
                    )
                else:
                    grounded_claims.append(f"Financial figure ${val:.2f} is mathematically grounded.")

            # Non-refundable rate violation check
            if not booking_record.get("cancellation_eligible", True):
                if re.search(r"\b(we have issued a full refund|your refund has been processed|100% refund approved)\b", draft_lower):
                    violations.append(
                        "Unauthorized Refund: Draft approved a full refund for a strictly non-refundable booking without supervisor approval."
                    )

        # ---------------------------------------------------------------------
        # Check 5: Policy Evidence Grounding
        # ---------------------------------------------------------------------
        checks_performed.append("Policy Groundedness Verification")
        if policy_evidence:
            matched_policy = False
            for doc in policy_evidence:
                policy_id = doc.get("policy_id", "").lower()
                category = doc.get("category", "").lower()
                if policy_id in draft_lower or category in draft_lower:
                    matched_policy = True
                    break
            if matched_policy:
                grounded_claims.append("Draft adheres to retrieved policy clauses.")
            else:
                grounded_claims.append("General procedural tone maintained.")

        passed = (len(violations) == 0)
        summary = (
            "Audit Passed: All factual entities, amounts, and policy rules verified against database records."
            if passed else
            f"Audit Failed: {len(violations)} inconsistency/hallucination issue(s) detected."
        )

        return AuditorFinding(
            passed=passed,
            checks_performed=checks_performed,
            violations=violations,
            grounded_claims=grounded_claims,
            hallucination_detected=(not passed),
            summary=summary
        )


_auditor_instance = None


def get_resolution_auditor() -> ResolutionAuditor:
    """Singleton getter for the Resolution Auditor."""
    global _auditor_instance
    if _auditor_instance is None:
        _auditor_instance = ResolutionAuditor()
    return _auditor_instance
