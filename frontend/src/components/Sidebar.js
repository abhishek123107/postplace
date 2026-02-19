import React from "react";
import { NavLink } from "react-router-dom";

const linkBase =
  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition";

function NavItem({ to, label, sublabel }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `${linkBase} ${
          isActive
            ? "bg-slate-900 text-white"
            : "text-slate-700 hover:bg-slate-100"
        }`
      }
      end
    >
      <div className="min-w-0">
        <div className="truncate">{label}</div>
        {sublabel ? <div className="text-xs opacity-70 truncate">{sublabel}</div> : null}
      </div>
    </NavLink>
  );
}

export default function Sidebar({ connected }) {
  return (
    <aside className="w-full md:w-64 md:min-h-screen bg-white border-r border-slate-200">
      <div className="p-5">
        <div className="text-lg font-semibold tracking-tight">Postify</div>
        <div className="text-xs text-slate-500 mt-1">Social Media Manager</div>
      </div>

      <div className="px-3 pb-4">
        <div className="space-y-1">
          <NavItem to="/" label="Dashboard" sublabel="Overview & quick actions" />
          <NavItem to="/compose" label="Compose" sublabel="Create a post" />
          <NavItem to="/connections" label="Connections" sublabel="Connect accounts" />
          <NavItem to="/automation" label="Automation" sublabel="Blog → scheduled posts" />
          <NavItem to="/history" label="History" sublabel="Past posts & status" />
        </div>

        <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm font-medium">Account Status</div>
          <div className="mt-3 space-y-2 text-xs text-slate-700">
            <div className="flex items-center justify-between">
              <div>Facebook</div>
              <div className={connected.facebook ? "text-emerald-700 font-medium" : "text-slate-500"}>
                {connected.facebook ? "Connected" : "Not"}
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>Instagram</div>
              <div className={connected.instagram ? "text-emerald-700 font-medium" : "text-slate-500"}>
                {connected.instagram ? "Connected" : "Not"}
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>Twitter</div>
              <div className={connected.twitter ? "text-emerald-700 font-medium" : "text-slate-500"}>
                {connected.twitter ? "Connected" : "Not"}
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>LinkedIn</div>
              <div className={connected.linkedin ? "text-emerald-700 font-medium" : "text-slate-500"}>
                {connected.linkedin ? "Connected" : "Not"}
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
