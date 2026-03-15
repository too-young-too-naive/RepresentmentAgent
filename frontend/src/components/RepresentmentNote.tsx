export default function RepresentmentNote({ note }: { note: string | null }) {
  if (!note) {
    return (
      <div className="text-center py-8 text-slate-400 text-sm">
        No representment note yet. Resolve the case to generate one.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm">
      <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
        <h3 className="font-semibold text-navy-800 text-sm">
          Representment Note
        </h3>
        <span className="text-[10px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded">
          FORMAL LETTER
        </span>
      </div>
      <div className="p-5">
        <pre className="whitespace-pre-wrap text-sm text-slate-700 font-serif leading-relaxed">
          {note}
        </pre>
      </div>
    </div>
  );
}
