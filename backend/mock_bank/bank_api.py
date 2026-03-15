"""
Mock Chase Bank API — simulates bank-side chargeback endpoints.
In production these would be real network calls to the issuing bank's dispute platform.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from mock_bank.schemas import (
    ChargebackRequest,
    RepresentmentResponse,
    BankSubmissionResult,
)

# In-memory ledger of representments the "bank" has received
_submitted_representments: dict[str, RepresentmentResponse] = {}


def receive_chargeback() -> ChargebackRequest:
    """Simulate Chase sending a new chargeback notification."""
    return ChargebackRequest(
        case_id=f"CB-{datetime.now().strftime('%Y-%m%d')}-{uuid.uuid4().hex[:6].upper()}",
        bank_name="Chase",
        cardholder_name="John Smith",
        card_last_four="4532",
        transaction_amount=1249.99,
        transaction_date=datetime(2026, 2, 15),
        reason_code="10.4 - Other Fraud (Card Not Present)",
        cardholder_statement=(
            "I did not make this purchase. I do not recognize this "
            "transaction to Acme Electronics."
        ),
    )


def submit_representment(response: RepresentmentResponse) -> BankSubmissionResult:
    """Simulate submitting a representment defense to Chase's dispute platform."""
    _submitted_representments[response.case_id] = response
    return BankSubmissionResult(
        case_id=response.case_id,
        accepted=True,
        message=(
            f"Representment for case {response.case_id} received by Chase. "
            f"Decision: {response.decision}. Under review."
        ),
    )


def get_submission_status(case_id: str) -> dict:
    """Check whether a representment was submitted for a given case."""
    if case_id in _submitted_representments:
        return {"case_id": case_id, "submitted": True, "status": "under_review"}
    return {"case_id": case_id, "submitted": False, "status": "pending"}
