
import {
  BriefcaseBusiness,
  ChartNoAxesCombined,
  ClipboardList,
  LayoutDashboard,
  Settings,
  UserRound,
  X,
} from "lucide-react";

import { NavLink, Link } from "react-router-dom";

const navigation = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Applications", path: "/applications", icon: BriefcaseBusiness },
  { label: "Kanban Board", path: "/kanban", icon: ClipboardList },
  { label: "Analytics", path: "/analytics", icon: ChartNoAxesCombined },
  { label: "Profile", path: "/profile", icon: UserRound },
  { label: "Settings", path: "/settings", icon: Settings },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && (
        <button
          type="button"
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={onClose}
        />
      )}

      <aside
        className={`dashboard-sidebar ${open ? "sidebar-open" : ""}`}
      >
        <div className="sidebar-brand">
          <Link
            to="/dashboard"
            className="sidebar-brand-link"
            onClick={onClose}
            aria-label="CareerTrack dashboard"
          >
            <BriefcaseBusiness size={25} />
            <span>CareerTrack</span>
          </Link>

          <button
            type="button"
            className="sidebar-close"
            aria-label="Close navigation"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>

        <p className="sidebar-label">WORKSPACE</p>

        <nav className="sidebar-nav" aria-label="Main navigation">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/dashboard"}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
              onClick={onClose}
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <Link
          to="/dashboard"
          className="sidebar-footer"
          onClick={onClose}
          aria-label="Open CareerTrack job workspace"
        >
          <div className="sidebar-footer-icon">
            <BriefcaseBusiness size={19} />
          </div>

          <div>
            <strong>CareerTrack</strong>
            <p>Job search workspace</p>
          </div>
        </Link>
      </aside>
    </>
  );
}
