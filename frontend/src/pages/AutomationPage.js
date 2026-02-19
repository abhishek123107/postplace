import React, { useEffect, useMemo, useState } from "react";
import { getRecentBlogPosts, getScheduledAutomationPosts } from "../api";

function Badge({ children, tone }) {
  const cls = useMemo(() => {
    if (tone === "success") return "bg-emerald-50 text-emerald-700 border-emerald-200";
    if (tone === "danger") return "bg-rose-50 text-rose-700 border-rose-200";
    return "bg-slate-50 text-slate-700 border-slate-200";
  }, [tone]);

  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${cls}`}>
      {children}
    </span>
  );
}

export default function AutomationPage({ userId }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recent, setRecent] = useState([]);
  const [scheduled, setScheduled] = useState([]);

  const refresh = async () => {
    setError(null);
    setLoading(true);
    try {
      const [r, s] = await Promise.all([
        getRecentBlogPosts(userId, 20),
        getScheduledAutomationPosts(userId, 100),
      ]);
      setRecent(r.items || []);
      setScheduled(s.items || []);
    } catch (e) {
      setError(e?.response?.data || e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line
  }, []);

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Automation</h1>
          <div className="mt-1 text-sm text-slate-600">
            Blog publish webhook → captions + visuals → scheduled posts.
          </div>
          <div className="mt-2 text-xs text-slate-500">User: {userId}</div>
        </div>

        <button
          type="button"
          onClick={refresh}
          disabled={loading}
          className="text-sm rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50 disabled:opacity-60"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error ? (
        <div className="mt-4 text-xs text-rose-700 whitespace-pre-wrap">
          {typeof error === "string" ? error : JSON.stringify(error, null, 2)}
        </div>
      ) : null}

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold">Recent Blog Posts</div>
            <Badge>{recent.length}</Badge>
          </div>

          <div className="mt-4 space-y-3">
            {recent.length === 0 ? (
              <div className="text-sm text-slate-600">No webhook events yet.</div>
            ) : (
              recent.map((p) => (
                <a
                  key={p.id}
                  href={p.url}
                  target="_blank"
                  rel="noreferrer"
                  className="block rounded-lg border border-slate-200 bg-slate-50 p-3 hover:bg-white"
                >
                  <div className="text-sm font-medium line-clamp-2">{p.title}</div>
                  <div className="mt-1 text-xs text-slate-600">{p.url}</div>
                  <div className="mt-2 text-xs text-slate-500">
                    Created: {p.created_at ? new Date(p.created_at * 1000).toLocaleString() : "—"}
                  </div>
                </a>
              ))
            )}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold">Scheduled Posts</div>
            <Badge>{scheduled.length}</Badge>
          </div>

          <div className="mt-4 space-y-3">
            {scheduled.length === 0 ? (
              <div className="text-sm text-slate-600">No scheduled posts yet.</div>
            ) : (
              scheduled.map((s) => (
                <div key={s.id} className="rounded-lg border border-slate-200 p-3">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="text-sm font-medium capitalize">{s.platform}</div>
                      <div className="text-xs text-slate-500">
                        {s.scheduled_at ? new Date(s.scheduled_at * 1000).toLocaleString() : "—"}
                      </div>
                    </div>
                    <div>
                      {s.status === "sent" ? (
                        <Badge tone="success">sent</Badge>
                      ) : s.status === "failed" ? (
                        <Badge tone="danger">failed</Badge>
                      ) : (
                        <Badge>scheduled</Badge>
                      )}
                    </div>
                  </div>

                  {s.error ? (
                    <div className="mt-2 text-xs text-rose-700 whitespace-pre-wrap">{s.error}</div>
                  ) : null}

                  {s.external_id ? (
                    <div className="mt-2 text-xs text-slate-600">External ID: {s.external_id}</div>
                  ) : null}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        Tip: LinkedIn posting requires `LINKEDIN_AUTHOR_URN` in backend env and a valid `linkedin` access token saved in the DB.
      </div>
    </div>
  );
}
