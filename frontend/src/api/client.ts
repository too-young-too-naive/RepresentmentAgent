const BASE = "/api";

export interface ChargebackCase {
  id: number;
  case_id: string;
  bank_name: string;
  cardholder_name: string;
  card_last_four: string;
  transaction_amount: number;
  transaction_date: string;
  reason_code: string;
  cardholder_statement: string;
  status: string;
  decision: string | null;
  representment_note: string | null;
  evidence_summary: string | null;
  created_at: string;
  resolved_at: string | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || res.statusText);
  }
  return res.json();
}

export function listChargebacks(): Promise<ChargebackCase[]> {
  return request("/chargebacks");
}

export function getChargeback(caseId: string): Promise<ChargebackCase> {
  return request(`/chargebacks/${caseId}`);
}

export function simulateIncomingChargeback(
  scenario: "defend" | "accept" = "defend"
): Promise<ChargebackCase> {
  return request(`/bank/webhook?scenario=${scenario}`, { method: "POST" });
}
