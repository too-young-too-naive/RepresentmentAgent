import { Link } from "react-router-dom";
import type { ChargebackCase } from "../api/client";
import StatusBadge from "./StatusBadge";

export default function ChargebackCard({ cb }: { cb: ChargebackCase }) {
  return (
    <Link
      to={`/case/${cb.case_id}`}
      className="block bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-mono text-sm text-slate-500">{cb.case_id}</p>
          <p className="text-lg font-semibold text-navy-800 mt-0.5">
            ${cb.transaction_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </p>
        </div>
        <StatusBadge status={cb.status} />
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-slate-600">
        <div>
          <span className="text-slate-400">Bank:</span> {cb.bank_name}
        </div>
        <div>
          <span className="text-slate-400">Card:</span> ****{cb.card_last_four}
        </div>
        <div>
          <span className="text-slate-400">Cardholder:</span>{" "}
          {cb.cardholder_name}
        </div>
        <div>
          <span className="text-slate-400">Date:</span>{" "}
          {new Date(cb.transaction_date).toLocaleDateString()}
        </div>
      </div>

      <p className="mt-3 text-xs text-slate-400 truncate">
        {cb.reason_code}
      </p>
    </Link>
  );
}
