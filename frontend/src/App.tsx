import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CaseDetail from "./pages/CaseDetail";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-navy-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-navy-500 rounded-lg flex items-center justify-center font-bold text-sm">
              AE
            </div>
            <div>
              <h1 className="text-lg font-semibold leading-tight">
                Acme Electronics
              </h1>
              <p className="text-navy-300 text-xs">
                Chargeback Representment Agent
              </p>
            </div>
          </div>
          <span className="text-xs text-navy-300 bg-navy-700 px-3 py-1 rounded-full">
            Demo
          </span>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/case/:caseId" element={<CaseDetail />} />
        </Routes>
      </main>
    </div>
  );
}
