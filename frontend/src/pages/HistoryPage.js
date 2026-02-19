import React from "react";

export default function HistoryPage({ history }) {
  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">History</h1>
          <div className="mt-1 text-sm text-slate-600">Review your previously sent posts.</div>
        </div>
        <div className="text-xs text-slate-500">Total: {history.length}</div>
      </div>

      <div className="mt-6 space-y-4">
        {history.length === 0 ? (
          <div className="text-sm text-slate-600">No posts yet.</div>
        ) : (
          history.map((h) => (
            <div key={h.id} className="rounded-xl border border-slate-200 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-xs text-slate-500">{new Date(h.ts).toLocaleString()}</div>
                  <div className="mt-2 text-sm whitespace-pre-wrap">{h.content}</div>
                  <div className="mt-2 text-xs text-slate-600">Platforms: {h.platforms.join(", ")}</div>
                </div>
                <div className="text-xs text-slate-500">#{h.id}</div>
              </div>

              <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-2">
                {h.results.map((r, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between rounded-lg bg-slate-50 border border-slate-200 px-3 py-2"
                  >
                    <div className="text-sm capitalize">{r.platform}</div>
                    <div className={`text-sm font-medium ${r.status === "success" ? "text-emerald-700" : "text-rose-700"}`}>
                      {r.status}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
