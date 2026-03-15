"""
LangChain-based Representment Agent with tool-calling and SSE step streaming.
Uses the LangChain 1.2+ create_agent API (backed by LangGraph).
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from typing import AsyncGenerator, Dict

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from config import LLM_BASE_URL, LLM_MODEL_NAME, LLM_API_KEY, MERCHANT_NAME
from database.db import SessionLocal
from database.models import Customer, Order, Payment, Chargeback
from mock_bank.bank_api import submit_representment as bank_submit
from mock_bank.schemas import RepresentmentResponse
from agent.prompts import SYSTEM_PROMPT


def _get_db() -> Session:
    return SessionLocal()


# ---------------------------------------------------------------------------
# Agent tools — each one wraps a DB or bank operation
# ---------------------------------------------------------------------------


@tool
def lookup_customer(name: str = "", card_last_four: str = "") -> str:
    """Look up a customer by name or last four digits of their card.
    Provide at least one of: name, card_last_four."""
    db = _get_db()
    try:
        query = db.query(Customer)
        if name:
            query = query.filter(Customer.name.ilike(f"%{name}%"))
        if card_last_four:
            customer_ids = [
                p.customer_id
                for p in db.query(Payment).filter(Payment.card_last_four == card_last_four).all()
            ]
            if customer_ids:
                query = query.filter(Customer.customer_id.in_(customer_ids))
        customers = query.all()
        if not customers:
            return "No customer found matching the given criteria."
        results = []
        for c in customers:
            results.append(
                f"Customer ID: {c.customer_id}, Name: {c.name}, Email: {c.email}, "
                f"Phone: {c.phone}, Address: {c.address}, "
                f"Account Created: {c.account_created_at.strftime('%Y-%m-%d')}"
            )
        return "\n".join(results)
    finally:
        db.close()


@tool
def get_order_history(customer_id: int) -> str:
    """Retrieve all orders for a customer by their customer_id."""
    db = _get_db()
    try:
        orders = db.query(Order).filter(Order.customer_id == customer_id).all()
        if not orders:
            return "No orders found for this customer."
        results = []
        for o in orders:
            delivery = o.delivery_date.strftime("%Y-%m-%d") if o.delivery_date else "N/A"
            results.append(
                f"Order #{o.order_id}: {o.item_description} | "
                f"Amount: ${o.amount:.2f} | Date: {o.order_date.strftime('%Y-%m-%d')} | "
                f"Status: {o.shipping_status} | Tracking: {o.tracking_number} | "
                f"Delivered: {delivery}"
            )
        return "\n".join(results)
    finally:
        db.close()


@tool
def get_payment_history(customer_id: int) -> str:
    """Retrieve all payment records for a customer by their customer_id."""
    db = _get_db()
    try:
        payments = db.query(Payment).filter(Payment.customer_id == customer_id).all()
        if not payments:
            return "No payments found for this customer."
        results = []
        for p in payments:
            results.append(
                f"Payment #{p.payment_id}: Order #{p.order_id} | "
                f"Card: ****{p.card_last_four} ({p.bank_name}) | "
                f"Amount: ${p.amount:.2f} | Status: {p.status} | "
                f"Date: {p.payment_date.strftime('%Y-%m-%d')}"
            )
        return "\n".join(results)
    finally:
        db.close()


@tool
def analyze_chargeback(
    chargeback_reason: str,
    cardholder_statement: str,
    order_evidence: str,
    payment_evidence: str,
    customer_info: str,
) -> str:
    """Analyze the chargeback claim against gathered evidence and recommend defend or accept.

    Args:
        chargeback_reason: The reason code and description from the bank.
        cardholder_statement: What the cardholder claimed.
        order_evidence: Summary of relevant order data.
        payment_evidence: Summary of relevant payment data.
        customer_info: Summary of customer profile.
    """
    return (
        "Evidence compiled. Please analyze the following and decide (defend/accept):\n\n"
        f"CHARGEBACK REASON: {chargeback_reason}\n"
        f"CARDHOLDER STATEMENT: {cardholder_statement}\n\n"
        f"CUSTOMER INFO:\n{customer_info}\n\n"
        f"ORDER EVIDENCE:\n{order_evidence}\n\n"
        f"PAYMENT EVIDENCE:\n{payment_evidence}\n\n"
        "Based on this evidence, state your decision and reasoning."
    )


@tool
def generate_representment_note(
    case_id: str,
    bank_name: str,
    cardholder_name: str,
    amount: float,
    reason_code: str,
    transaction_date: str,
    evidence_body: str,
) -> str:
    """Generate a formal representment note to send to the bank.

    Args:
        case_id: The chargeback case identifier.
        bank_name: The issuing bank name.
        cardholder_name: Name of the cardholder.
        amount: The disputed transaction amount.
        reason_code: The chargeback reason code.
        transaction_date: Date of the original transaction.
        evidence_body: Detailed evidence paragraphs supporting the defense.
    """
    from agent.prompts import REPRESENTMENT_NOTE_TEMPLATE
    note = REPRESENTMENT_NOTE_TEMPLATE.format(
        case_id=case_id,
        date=datetime.now().strftime("%B %d, %Y"),
        reason_code=reason_code,
        cardholder_name=cardholder_name,
        amount=amount,
        transaction_date=transaction_date,
        bank_name=bank_name,
        evidence_body=evidence_body,
    )
    return note


@tool
def submit_representment_to_bank(
    case_id: str,
    decision: str,
    representment_note: str,
    evidence_summary: str,
) -> str:
    """Submit the representment defense (or acceptance) to the bank.

    Args:
        case_id: The chargeback case identifier.
        decision: Either 'defend' or 'accept'.
        representment_note: The full representment letter (if defending).
        evidence_summary: A short summary of the evidence.
    """
    response = RepresentmentResponse(
        case_id=case_id,
        merchant_name=MERCHANT_NAME,
        decision=decision,
        representment_note=representment_note,
        evidence_summary=evidence_summary,
        supporting_documents=[
            "delivery_confirmation.pdf",
            "signed_receipt.pdf",
            "3ds_authentication_log.pdf",
        ] if decision == "defend" else [],
    )
    result = bank_submit(response)

    db = _get_db()
    try:
        cb = db.query(Chargeback).filter(Chargeback.case_id == case_id).first()
        if cb:
            cb.status = "defended" if decision == "defend" else "accepted"
            cb.decision = decision
            cb.representment_note = representment_note
            cb.evidence_summary = evidence_summary
            cb.resolved_at = datetime.now()
            db.commit()
    finally:
        db.close()

    return f"Bank response: {result.message}"


# ---------------------------------------------------------------------------
# Build and run the agent
# ---------------------------------------------------------------------------

ALL_TOOLS = [
    lookup_customer,
    get_order_history,
    get_payment_history,
    analyze_chargeback,
    generate_representment_note,
    submit_representment_to_bank,
]


def _build_agent():
    llm = ChatOpenAI(
        base_url=LLM_BASE_URL,
        model=LLM_MODEL_NAME,
        api_key=LLM_API_KEY,
        temperature=0.1,
    )
    return create_agent(llm, ALL_TOOLS, system_prompt=SYSTEM_PROMPT)


async def resolve_chargeback(case_id: str) -> AsyncGenerator[str, None]:
    """
    Run the agent against a chargeback case and yield SSE events.
    """
    db = _get_db()
    try:
        cb = db.query(Chargeback).filter(Chargeback.case_id == case_id).first()
        if not cb:
            yield _sse("error", {"message": f"Case {case_id} not found"})
            return

        cb.status = "in_progress"
        db.commit()

        chargeback_data = {
            "case_id": cb.case_id,
            "bank_name": cb.bank_name,
            "cardholder_name": cb.cardholder_name,
            "card_last_four": cb.card_last_four,
            "transaction_amount": cb.transaction_amount,
            "transaction_date": cb.transaction_date.strftime("%Y-%m-%d"),
            "reason_code": cb.reason_code,
            "cardholder_statement": cb.cardholder_statement,
        }
    finally:
        db.close()

    yield _sse("agent_start", {
        "case_id": case_id,
        "message": "Agent started processing chargeback",
    })

    user_input = (
        f"A chargeback has been filed. Please investigate and resolve it.\n\n"
        f"Case ID: {chargeback_data['case_id']}\n"
        f"Bank: {chargeback_data['bank_name']}\n"
        f"Cardholder: {chargeback_data['cardholder_name']}\n"
        f"Card: Visa ending {chargeback_data['card_last_four']}\n"
        f"Amount: ${chargeback_data['transaction_amount']:.2f}\n"
        f"Transaction Date: {chargeback_data['transaction_date']}\n"
        f"Reason Code: {chargeback_data['reason_code']}\n"
        f"Cardholder Statement: \"{chargeback_data['cardholder_statement']}\"\n\n"
        f"Use the tools available to investigate this case, decide whether to "
        f"defend or accept, and if defending, generate and submit a representment note."
    )

    agent = _build_agent()
    t0 = time.perf_counter()

    print(f"[AGENT] {case_id}: Started, calling LLM at {LLM_BASE_URL} (model: {LLM_MODEL_NAME})", flush=True)

    try:
        step_count = 0
        tool_start_time = None
        async for event in agent.astream_events(
            {"messages": [{"role": "user", "content": user_input}]},
            version="v2",
        ):
            kind = event.get("event", "")

            if kind == "on_tool_start":
                step_count += 1
                tool_start_time = time.perf_counter()
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                elapsed = time.perf_counter() - t0
                print(f"[AGENT] {case_id}: Tool {step_count} {tool_name} (elapsed {elapsed:.1f}s)", flush=True)
                yield _sse("tool_start", {
                    "step": step_count,
                    "tool": tool_name,
                    "input": _safe_serialize(tool_input),
                })

            elif kind == "on_tool_end":
                tool_name = event.get("name", "unknown")
                output = event.get("data", {}).get("output", "")
                if hasattr(output, "content"):
                    output = output.content
                tool_elapsed = time.perf_counter() - tool_start_time if tool_start_time else 0
                print(f"[AGENT] {case_id}: Tool {tool_name} done ({tool_elapsed:.1f}s), waiting for LLM...", flush=True)
                yield _sse("tool_end", {
                    "step": step_count,
                    "tool": tool_name,
                    "output": str(output)[:2000],
                })

            elif kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk", None)
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield _sse("llm_token", {
                        "token": chunk.content,
                    })

        total_elapsed = time.perf_counter() - t0
        print(f"[AGENT] {case_id}: Completed in {total_elapsed:.1f}s", flush=True)
        yield _sse("agent_end", {
            "case_id": case_id,
            "message": "Agent completed processing",
        })

    except Exception as e:
        print(f"[AGENT] {case_id}: ERROR - {e}", flush=True)
        yield _sse("error", {"message": str(e)})

        db = _get_db()
        try:
            cb = db.query(Chargeback).filter(Chargeback.case_id == case_id).first()
            if cb and cb.status == "in_progress":
                cb.status = "error"
                db.commit()
        finally:
            db.close()


def _sse(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def _safe_serialize(obj) -> str:
    try:
        return json.dumps(obj) if not isinstance(obj, str) else obj
    except (TypeError, ValueError):
        return str(obj)
