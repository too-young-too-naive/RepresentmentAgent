const STATUS_STYLES: Record<string, string> = {
  new: "bg-blue-100 text-blue-800",
  in_progress: "bg-amber-100 text-amber-800",
  defended: "bg-emerald-100 text-emerald-800",
  accepted: "bg-slate-100 text-slate-600",
  error: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<string, string> = {
  new: "New",
  in_progress: "In Progress",
  defended: "Defended",
  accepted: "Accepted",
  error: "Error",
};

export default function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? "bg-slate-100 text-slate-600";
  const label = STATUS_LABELS[status] ?? status;
  return (
    <span
      className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${style}`}
    >
      {label}
    </span>
  );
}
