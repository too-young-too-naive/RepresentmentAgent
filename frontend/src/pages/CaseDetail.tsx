import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getChargeback } from "../api/client";
import type { ChargebackCase } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import AgentTimeline from "../components/AgentTimeline";
import RepresentmentNote from "../components/RepresentmentNote";
import { useAgentStream } from "../hooks/useAgentStream";

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const [cb, setCb] = useState<ChargebackCase | null>(null);
  const [loading, setLoading] = useState(true);
  const { steps, isRunning, error, start } = useAgentStream();

  const fetchCase = async () => {
    if (!caseId) return;
    try {
      const data = await getChargeback(caseId);
      setCb(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [caseId]);

  // Re-fetch case data when agent finishes to pick up resolution
  useEffect(() => {
    if (!isRunning && steps.length > 0) {
      const timer = setTimeout(fetchCase, 500);
      return () => clearTimeout(timer);
    }
  }, [isRunning, steps.length]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-navy-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!cb) {
    return (
      <div className="text-center py-20 text-slate-400">
        Case not found.{" "}
        <Link to="/" className="text-navy-600 underline">
          Go back
        </Link>
      </div>
    );
  }

  const isResolved = cb.status === "defended" || cb.status === "accepted";

  return (
    <div>
      {/* Breadcrumb */}
      <div className="mb-4">
        <Link
          to="/"
          className="text-sm text-navy-600 hover:text-navy-800 transition-colors"
        >
          &larr; All Cases
        </Link>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-navy-800 flex items-center gap-3">
            {cb.case_id}
            <StatusBadge status={cb.status} />
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            Filed by {cb.bank_name} on{" "}
            {new Date(cb.created_at).toLocaleDateString()}
          </p>
        </div>

        {!isResolved && (
          <button
            onClick={() => start(cb.case_id)}
            disabled={isRunning}
            className="px-5 py-2.5 bg-navy-600 text-white rounded-lg text-sm font-medium hover:bg-navy-700 disabled:opacity-50 transition-colors"
          >
            {isRunning ? "Agent Running..." : "Resolve with Agent"}
          </button>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left: Chargeback Details */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <h3 className="font-semibold text-navy-800 text-sm mb-4">
              Chargeback Details
            </h3>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate-400 text-xs uppercase tracking-wide">
                  Bank
                </dt>
                <dd className="text-slate-700 font-medium">{cb.bank_name}</dd>
              </div>
              <div>
                <dt className="text-slate-400 text-xs uppercase tracking-wide">
                  Cardholder
                </dt>
                <dd className="text-slate-700 font-medium">
                  {cb.cardholder_name}
                </dd>
              </div>
              <div>
                <dt className="text-slate-400 text-xs uppercase tracking-wide">
                  Card
                </dt>
                <dd className="text-slate-700 font-medium">
                  Visa ending {cb.card_last_four}
                </dd>
              </div>
              <div>
                <dt className="text-slate-400 text-xs uppercase tracking-wide">
                  Amount
                </dt>
                <dd className="text-slate-700 font-semibold text-lg">
                  $
                  {cb.transaction_amount.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                  })}
                </dd>
              </div>
              <div>
                <dt className="text-slate-400 text-xs uppercase tracking-wide">
                  Transaction Date
                </dt>
                <dd className="text-slate-700 font-medium">
                  {new Date(cb.transaction_date).toLocaleDateString()}
                </dd>
              </div>
              <div>
                <dt className="text-slate-400 text-xs uppercase tracking-wide">
                  Reason Code
                </dt>
                <dd className="text-slate-700">{cb.reason_code}</dd>
              </div>
              <div>
                <dt className="text-slate-400 text-xs uppercase tracking-wide">
                  Cardholder Statement
                </dt>
                <dd className="text-slate-700 italic bg-red-50 rounded p-2 text-xs">
                  "{cb.cardholder_statement}"
                </dd>
              </div>
              {cb.decision && (
                <div>
                  <dt className="text-slate-400 text-xs uppercase tracking-wide">
                    Decision
                  </dt>
                  <dd
                    className={`font-bold ${cb.decision === "defend" ? "text-emerald-600" : "text-slate-600"}`}
                  >
                    {cb.decision.toUpperCase()}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        {/* Center: Agent Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <h3 className="font-semibold text-navy-800 text-sm mb-4">
              Agent Process
            </h3>
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
                {error}
              </div>
            )}
            <AgentTimeline steps={steps} isRunning={isRunning} />
          </div>

          {/* Representment Note */}
          <RepresentmentNote note={cb.representment_note} />
        </div>
      </div>
    </div>
  );
}
