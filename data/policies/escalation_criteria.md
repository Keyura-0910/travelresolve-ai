# Policy Document: Escalation & Human Review Criteria
Document ID: POL-ESC-007
Category: Escalation Criteria

## 1. Mandatory Escalation Triggers
An AI agent or Tier-1 support representative MUST immediately route a ticket to the Human Review Queue under the following conditions:
- **Low Confidence Classification**: Intent classification confidence score falls below 55% or contains mutually conflicting requests.
- **Auditor Verification Failure**: The proposed draft mentions dates, hotels, prices, or refund amounts that contradict or do not exist in the verified database record.
- **Policy Exceptions**: Customer requests a refund on a non-refundable booking due to medical emergency, bereavement, natural disaster, or airline flight disruption.
- **High Financial Exposure**: Any refund or credit recommendation exceeding $500.00 USD.
- **Hostile or Legal Language**: Explicit threats of litigation, regulatory complaints, credit card chargebacks, or severe harassment.
- **Missing or Mismatched Booking**: Customer provides a booking ID that does not exist in the database, or the customer name does not match the booking owner.

## 2. Human Review SLA
- Critical tickets awaiting human review must be assessed within 2 hours.
- Standard tickets awaiting review must be resolved within 8 business hours.
