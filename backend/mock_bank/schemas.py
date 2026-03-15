from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ChargebackRequest(BaseModel):
    case_id: str
    bank_name: str
    cardholder_name: str
    card_last_four: str
    transaction_amount: float
    transaction_date: datetime
    reason_code: str
    cardholder_statement: str


class RepresentmentResponse(BaseModel):
    case_id: str
    merchant_name: str
    decision: str  # "defend" or "accept"
    representment_note: Optional[str] = None
    evidence_summary: Optional[str] = None
    supporting_documents: List[str] = []


class ChargebackOut(BaseModel):
    id: int
    case_id: str
    bank_name: str
    cardholder_name: str
    card_last_four: str
    transaction_amount: float
    transaction_date: datetime
    reason_code: str
    cardholder_statement: str
    status: str
    decision: Optional[str] = None
    representment_note: Optional[str] = None
    evidence_summary: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BankSubmissionResult(BaseModel):
    case_id: str
    accepted: bool
    message: str
