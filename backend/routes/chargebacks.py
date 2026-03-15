from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Chargeback
from mock_bank.schemas import ChargebackOut
from agent.representment_agent import resolve_chargeback

router = APIRouter(tags=["chargebacks"])


@router.get("/chargebacks", response_model=List[ChargebackOut])
def list_chargebacks(db: Session = Depends(get_db)):
    return db.query(Chargeback).order_by(Chargeback.created_at.desc()).all()


@router.get("/chargebacks/{case_id}", response_model=ChargebackOut)
def get_chargeback(case_id: str, db: Session = Depends(get_db)):
    cb = db.query(Chargeback).filter(Chargeback.case_id == case_id).first()
    if not cb:
        raise HTTPException(status_code=404, detail="Case not found")
    return cb


@router.get("/chargebacks/{case_id}/resolve")
async def resolve_case(case_id: str, db: Session = Depends(get_db)):
    """Kick off the representment agent and stream progress via SSE."""
    cb = db.query(Chargeback).filter(Chargeback.case_id == case_id).first()
    if not cb:
        raise HTTPException(status_code=404, detail="Case not found")
    if cb.status in ("defended", "accepted"):
        raise HTTPException(status_code=400, detail="Case already resolved")

    return StreamingResponse(
        resolve_chargeback(case_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
