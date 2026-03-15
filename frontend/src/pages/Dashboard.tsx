import { useEffect, useState } from "react";
import { listChargebacks, simulateIncomingChargeback } from "../api/client";
import type { ChargebackCase } from "../api/client";
import ChargebackCard from "../components/ChargebackCard";

export default function Dashboard() {
  const [cases, setCases] = useState<ChargebackCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState<string | null>(null);

  const fetchCases = async () => {
    try {
      const data = await listChargebacks();
      setCases(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleSimulate = async (scenario: "defend" | "accept") => {
    setSimulating(scenario);
    try {
      await simulateIncomingChargeback(scenario);
      await fetchCases();
    } finally {
      setSimulating(null);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-navy-800">
            Chargeback Cases
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            {cases.length} case{cases.length !== 1 ? "s" : ""} total
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleSimulate("defend")}
            disabled={simulating !== null}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50 transition-colors"
          >
            {simulating === "defend" ? "Receiving..." : "Simulate Chargeback — Defend"}
          </button>
          <button
            onClick={() => handleSimulate("accept")}
            disabled={simulating !== null}
            className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 disabled:opacity-50 transition-colors"
          >
            {simulating === "accept" ? "Receiving..." : "Simulate Chargeback — Accept"}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-6 h-6 border-2 border-navy-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : cases.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <p className="text-lg">No chargeback cases yet</p>
          <p className="text-sm mt-1">
            Use the buttons above to simulate incoming chargebacks
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cases.map((cb) => (
            <ChargebackCard key={cb.case_id} cb={cb} />
          ))}
        </div>
      )}
    </div>
  );
}
