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


import random

_DEFEND_SCENARIOS = [
    {
        "bank_name": "Chase",
        "cardholder_name": "John Smith",
        "card_last_four": "4532",
        "transaction_amount": 1249.99,
        "transaction_date": datetime(2026, 2, 15),
        "reason_code": "10.4 - Other Fraud (Card Not Present)",
        "cardholder_statement": (
            "I did not make this purchase. I do not recognize this "
            "transaction to Acme Electronics."
        ),
    },
    {
        "bank_name": "Chase",
        "cardholder_name": "Jane Doe",
        "card_last_four": "8821",
        "transaction_amount": 599.99,
        "transaction_date": datetime(2026, 1, 10),
        "reason_code": "10.4 - Other Fraud (Card Not Present)",
        "cardholder_statement": (
            "I did not authorize this charge from Acme Electronics for $599.99. "
            "Someone must have stolen my card information."
        ),
    },
]

_ACCEPT_SCENARIOS = [
    {
        "bank_name": "Chase",
        "cardholder_name": "Michael Chen",
        "card_last_four": "7291",
        "transaction_amount": 799.99,
        "transaction_date": datetime(2026, 1, 25),
        "reason_code": "13.3 - Not as Described or Defective (Goods Not Received)",
        "cardholder_statement": (
            "I ordered AirPods Max from Acme Electronics on January 25 but never "
            "received the package. Tracking shows it was lost in transit. I contacted "
            "the merchant but they refused to refund or reship."
        ),
    },
    {
        "bank_name": "Bank of America",
        "cardholder_name": "Sarah Williams",
        "card_last_four": "3156",
        "transaction_amount": 429.99,
        "transaction_date": datetime(2026, 2, 5),
        "reason_code": "12.1 - Processing Error (Late Presentment / Duplicate)",
        "cardholder_statement": (
            "I was charged twice for the same purchase of Bose QuietComfort Ultra "
            "Earbuds on February 5th. I only made one order but my statement shows "
            "two charges of $429.99 from Acme Electronics."
        ),
    },
]


def receive_chargeback(scenario: str = "defend") -> ChargebackRequest:
    """Simulate a bank sending a chargeback notification.

    Args:
        scenario: 'defend' for cases with strong merchant evidence,
                  'accept' for cases the merchant should accept.
    """
    pool = _DEFEND_SCENARIOS if scenario == "defend" else _ACCEPT_SCENARIOS
    data = random.choice(pool)
    return ChargebackRequest(
        case_id=f"CB-{datetime.now().strftime('%Y-%m%d')}-{uuid.uuid4().hex[:6].upper()}",
        **data,
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
