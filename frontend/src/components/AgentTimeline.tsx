import type { AgentStep } from "../hooks/useAgentStream";

const TOOL_LABELS: Record<string, string> = {
  lookup_customer: "Customer Lookup",
  get_order_history: "Order History",
  get_payment_history: "Payment History",
  analyze_chargeback: "Chargeback Analysis",
  generate_representment_note: "Generate Representment Note",
  submit_representment_to_bank: "Submit to Bank",
};

const EVENT_ICONS: Record<string, string> = {
  agent_start: "▶",
  tool_start: "⚙",
  tool_end: "✓",
  agent_end: "✔",
  error: "✗",
};

const EVENT_COLORS: Record<string, string> = {
  agent_start: "bg-blue-500",
  tool_start: "bg-amber-500",
  tool_end: "bg-emerald-500",
  agent_end: "bg-emerald-600",
  error: "bg-red-500",
};

function formatInput(input: string | undefined): string {
  if (!input) return "";
  try {
    const parsed = JSON.parse(input);
    if (typeof parsed === "object") {
      return Object.entries(parsed)
        .map(([k, v]) => {
          const val = typeof v === "string" ? v : JSON.stringify(v);
          return `${k}: ${val.length > 120 ? val.slice(0, 120) + "…" : val}`;
        })
        .join("\n");
    }
    return String(parsed);
  } catch {
    return input.length > 300 ? input.slice(0, 300) + "…" : input;
  }
}

export default function AgentTimeline({
  steps,
  isRunning,
}: {
  steps: AgentStep[];
  isRunning: boolean;
}) {
  if (steps.length === 0 && !isRunning) {
    return (
      <div className="text-center py-12 text-slate-400 text-sm">
        Click "Resolve with Agent" to start the investigation
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200" />

      <div className="space-y-4">
        {steps.map((step) => {
          const color = EVENT_COLORS[step.event] ?? "bg-slate-400";
          const icon = EVENT_ICONS[step.event] ?? "•";
          const toolLabel =
            step.tool && TOOL_LABELS[step.tool]
              ? TOOL_LABELS[step.tool]
              : step.tool;

          return (
            <div key={step.id} className="relative pl-10">
              {/* Dot */}
              <div
                className={`absolute left-2.5 top-1.5 w-3 h-3 rounded-full ${color} ring-2 ring-white`}
              />

              <div className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono">{icon}</span>
                  <span className="text-sm font-medium text-navy-700">
                    {step.event === "agent_start"
                      ? "Agent Started"
                      : step.event === "agent_end"
                        ? "Agent Complete"
                        : step.event === "tool_start"
                          ? `Running: ${toolLabel}`
                          : step.event === "tool_end"
                            ? `Completed: ${toolLabel}`
                            : step.event}
                  </span>
                  <span className="ml-auto text-[10px] text-slate-400">
                    {new Date(step.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {step.event === "tool_start" && step.input && (
                  <pre className="mt-1 text-xs text-slate-500 bg-slate-50 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-32 overflow-y-auto">
                    {formatInput(step.input)}
                  </pre>
                )}

                {step.event === "tool_end" && step.output && (
                  <pre className="mt-1 text-xs text-slate-600 bg-emerald-50 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-48 overflow-y-auto">
                    {step.output.length > 800
                      ? step.output.slice(0, 800) + "…"
                      : step.output}
                  </pre>
                )}

                {step.event === "agent_end" && step.output && (
                  <p className="mt-1 text-sm text-slate-600">
                    {(step.output as string).length > 500
                      ? (step.output as string).slice(0, 500) + "…"
                      : step.output}
                  </p>
                )}

                {step.message && (
                  <p className="mt-1 text-xs text-slate-500">{step.message}</p>
                )}
              </div>
            </div>
          );
        })}

        {isRunning && (
          <div className="relative pl-10">
            <div className="absolute left-2.5 top-1.5 w-3 h-3 rounded-full bg-amber-400 ring-2 ring-white animate-pulse" />
            <div className="text-sm text-slate-400 py-2">
              Agent is working...
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
