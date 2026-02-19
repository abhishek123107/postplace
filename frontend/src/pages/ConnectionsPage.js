import React from "react";

export default function ConnectionsPage({ userId, connected, connectLoading, connectError, onConnect, onRefresh }) {
  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Connections</h1>
          <div className="mt-1 text-sm text-slate-600">Connect your social accounts via OAuth.</div>
          <div className="mt-2 text-xs text-slate-500">User: {userId}</div>
        </div>

        <button
          type="button"
          onClick={onRefresh}
          className="text-sm rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50"
        >
          Refresh
        </button>
      </div>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { key: "facebook", label: "Facebook", desc: "Pages posting" },
          { key: "instagram", label: "Instagram", desc: "IG Graph publish" },
          { key: "twitter", label: "Twitter", desc: "Tweet posting" },
          { key: "linkedin", label: "LinkedIn", desc: "UGC post publishing" },
        ].map((p) => (
          <div key={p.key} className="rounded-xl border border-slate-200 p-5">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-sm font-semibold">{p.label}</div>
                <div className="text-xs text-slate-500 mt-1">{p.desc}</div>
              </div>
              <div
                className={`text-xs font-medium ${
                  connected[p.key] ? "text-emerald-700" : "text-slate-500"
                }`}
              >
                {connected[p.key] ? "Connected" : "Not connected"}
              </div>
            </div>

            <button
              type="button"
              disabled={connectLoading}
              onClick={() => onConnect(p.key)}
              className="mt-4 w-full rounded-lg bg-slate-900 text-white px-3 py-2 text-sm font-medium disabled:opacity-60"
            >
              {connectLoading ? "Opening..." : `Connect ${p.label}`}
            </button>
          </div>
        ))}
      </div>

      {connectError ? (
        <div className="mt-4 text-xs text-rose-700 whitespace-pre-wrap">
          {typeof connectError === "string" ? connectError : JSON.stringify(connectError, null, 2)}
        </div>
      ) : null}

      <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        After finishing OAuth in the new tab, come back and click Refresh.
      </div>
    </div>
  );
}
