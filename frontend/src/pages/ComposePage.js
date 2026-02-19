import React from "react";

export default function ComposePage({
  content,
  setContent,
  imageFile,
  setImageFile,
  platforms,
  togglePlatform,
  loading,
  onSubmit,
  connected,
}) {
  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Compose</h1>
          <div className="mt-1 text-sm text-slate-600">Create a post and send it to multiple platforms.</div>
        </div>
        <div className="text-xs text-slate-500">
          Connected: {Object.values(connected).filter(Boolean).length}/3
        </div>
      </div>

      <form className="mt-6 space-y-4" onSubmit={onSubmit}>
        <div>
          <label className="block text-sm font-medium mb-1">Content</label>
          <textarea
            className="w-full min-h-[140px] rounded-xl border border-slate-300 p-4 focus:outline-none focus:ring-2 focus:ring-slate-400"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your post..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Image (optional)</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setImageFile(e.target.files?.[0] || null)}
            className="block w-full text-sm"
          />
          {imageFile ? <div className="text-xs text-slate-600 mt-1">Selected: {imageFile.name}</div> : null}
        </div>

        <div>
          <div className="block text-sm font-medium mb-2">Platforms</div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { key: "facebook", label: "Facebook" },
              { key: "instagram", label: "Instagram" },
              { key: "twitter", label: "Twitter" },
            ].map((p) => (
              <label key={p.key} className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3">
                <div className="min-w-0">
                  <div className="text-sm font-medium">{p.label}</div>
                  <div className={`text-xs ${connected[p.key] ? "text-emerald-700" : "text-slate-500"}`}>
                    {connected[p.key] ? "Connected" : "Not connected"}
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={platforms[p.key]}
                  onChange={() => togglePlatform(p.key)}
                />
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center rounded-xl bg-slate-900 text-white px-5 py-3 text-sm font-medium disabled:opacity-60"
        >
          {loading ? "Posting..." : "Send Post"}
        </button>
      </form>

      <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        Tip: Instagram posting requires an image, and the backend must be publicly reachable (ngrok) for Meta to fetch the image URL.
      </div>
    </div>
  );
}
