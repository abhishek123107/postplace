import React from "react";
import Sidebar from "./Sidebar";

export default function AppLayout({ connected, children }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="min-h-screen md:flex">
        <Sidebar connected={connected} />

        <main className="flex-1">
          <div className="max-w-6xl mx-auto p-6">
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
              <div className="p-6">{children}</div>
            </div>

            <div className="mt-4 text-xs text-slate-500">API: {process.env.REACT_APP_API_BASE || "http://localhost:8000"}</div>
          </div>
        </main>
      </div>
    </div>
  );
}
