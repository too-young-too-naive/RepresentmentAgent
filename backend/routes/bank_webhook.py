from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Chargeback
from mock_bank.bank_api import receive_chargeback, submit_representment, get_submission_status
from mock_bank.schemas import RepresentmentResponse, ChargebackOut

router = APIRouter(tags=["bank"])


@router.post("/webhook", response_model=ChargebackOut)
def bank_webhook(db: Session = Depends(get_db)):
    """Simulate receiving a new chargeback notification from Chase."""
    cb_req = receive_chargeback()
    chargeback = Chargeback(
        case_id=cb_req.case_id,
        bank_name=cb_req.bank_name,
        cardholder_name=cb_req.cardholder_name,
        card_last_four=cb_req.card_last_four,
        transaction_amount=cb_req.transaction_amount,
        transaction_date=cb_req.transaction_date,
        reason_code=cb_req.reason_code,
        cardholder_statement=cb_req.cardholder_statement,
        status="new",
        created_at=datetime.now(),
    )
    db.add(chargeback)
    db.commit()
    db.refresh(chargeback)
    return chargeback


@router.post("/submit-representment")
def submit_representment_endpoint(response: RepresentmentResponse):
    """Mock endpoint: merchant submits representment to the bank."""
    result = submit_representment(response)
    return result


@router.get("/status/{case_id}")
def check_bank_status(case_id: str):
    """Check the bank-side status of a representment submission."""
    return get_submission_status(case_id)
