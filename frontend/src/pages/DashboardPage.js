import React, { useMemo } from "react";
import { Link } from "react-router-dom";

function StatCard({ title, value, hint }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
      {hint ? <div className="mt-1 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

export default function DashboardPage({ connected, history }) {
  const connectedCount = useMemo(() => {
    return [connected.facebook, connected.instagram, connected.twitter].filter(Boolean).length;
  }, [connected]);

  const recent = history.slice(0, 3);

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <div className="mt-1 text-sm text-slate-600">
            A quick overview of your connections and latest posts.
          </div>
        </div>

        <Link
          to="/compose"
          className="inline-flex items-center justify-center rounded-lg bg-slate-900 text-white px-4 py-2 text-sm font-medium"
        >
          New Post
        </Link>
      </div>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Connected Platforms" value={`${connectedCount}/3`} hint="Facebook, Instagram, Twitter" />
        <StatCard title="Posts Sent" value={history.length} hint="Saved locally in this demo" />
        <StatCard title="Last Activity" value={history[0]?.ts ? new Date(history[0].ts).toLocaleString() : "—"} hint="Most recent post" />
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold">Quick Links</div>
          </div>
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Link className="rounded-xl border border-slate-200 hover:bg-slate-50 p-4" to="/connections">
              <div className="text-sm font-medium">Connections</div>
              <div className="text-xs text-slate-500 mt-1">Connect social accounts</div>
            </Link>
            <Link className="rounded-xl border border-slate-200 hover:bg-slate-50 p-4" to="/history">
              <div className="text-sm font-medium">Post History</div>
              <div className="text-xs text-slate-500 mt-1">See success/failure</div>
            </Link>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold">Recent Posts</div>
            <Link to="/history" className="text-sm text-slate-700 hover:underline">
              View all
            </Link>
          </div>

          <div className="mt-4 space-y-3">
            {recent.length === 0 ? (
              <div className="text-sm text-slate-600">No posts yet.</div>
            ) : (
              recent.map((h) => (
                <div key={h.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <div className="text-xs text-slate-500">{new Date(h.ts).toLocaleString()}</div>
                  <div className="mt-1 text-sm line-clamp-2 whitespace-pre-wrap">{h.content}</div>
                  <div className="mt-2 text-xs text-slate-600">Platforms: {h.platforms.join(", ")}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
