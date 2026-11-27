import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  UserRound,
  ShieldCheck,
  LogOut,
  ExternalLink,
  RefreshCw,
  Mail,
  CalendarDays,
  Phone,
  BriefcaseBusiness,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { authAPI } from "../api/auth.api";

import Sidebar from "../components/dashboard/Sidebar";
import DashboardHeader from "../components/dashboard/DashboardHeader";

import "../styles/settings.css";

function getError(error) {
  return (
    error?.response?.data?.message ||
    error?.response?.data?.detail ||
    "Unable to load account settings."
  );
}

export default function Settings() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [profile, setProfile] = useState(user || {});
  const [loading, setLoading] = useState(true);
  const [loggingOut, setLoggingOut] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [error, setError] = useState("");

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await authAPI.getProfile();
      const account = data?.user ?? data;

      setProfile(account || {});
    } catch (err) {
      setError(getError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const handleLogout = async () => {
    if (loggingOut) return;

    setLoggingOut(true);

    try {
      await logout();
      navigate("/login", { replace: true });
    } finally {
      setLoggingOut(false);
    }
  };

  const joinedDate = profile?.date_joined
    ? new Date(profile.date_joined).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "long",
        year: "numeric",
      })
    : "Not available";

  return (
    <div className="dashboard-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="dashboard-main">
        <DashboardHeader
          onMenuClick={() => setSidebarOpen(true)}
        />

        <div className="dashboard-content settings-page">
          <div className="dashboard-title-row">
            <div>
              <p className="dashboard-eyebrow">PREFERENCES</p>
              <h1>Settings</h1>
              <p className="dashboard-subtitle">
                Manage your account and workspace access.
              </p>
            </div>

            <button
              type="button"
              className="refresh-button"
              onClick={loadSettings}
              disabled={loading}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          {error && (
            <div className="settings-alert" role="alert">
              {error}
              <button type="button" onClick={loadSettings}>
                Retry
              </button>
            </div>
          )}

          {loading ? (
            <div className="settings-loading">
              Loading account settings...
            </div>
          ) : (
            <>
              <section className="settings-card">
                <div className="settings-card-heading">
                  <div className="settings-icon">
                    <UserRound size={21} />
                  </div>
                  <div>
                    <h2>Account information</h2>
                    <p>Your registered CareerTrack account details.</p>
                  </div>
                </div>

                <div className="settings-info-grid">
                  <div className="settings-info-item">
                    <span><UserRound size={16} /> Full name</span>
                    <strong>
                      {[profile.first_name, profile.last_name]
                        .filter(Boolean)
                        .join(" ") || "Not provided"}
                    </strong>
                  </div>

                  <div className="settings-info-item">
                    <span><Mail size={16} /> Email address</span>
                    <strong>{profile.email || "Not available"}</strong>
                  </div>

                  <div className="settings-info-item">
                    <span><Phone size={16} /> Phone number</span>
                    <strong>{profile.phone_number || "Not provided"}</strong>
                  </div>

                  <div className="settings-info-item">
                    <span><CalendarDays size={16} /> Account created</span>
                    <strong>{joinedDate}</strong>
                  </div>
                </div>

                <Link to="/profile" className="settings-action-link">
                  Edit profile
                  <ExternalLink size={16} />
                </Link>
              </section>

              <section className="settings-card">
                <div className="settings-card-heading">
                  <div className="settings-icon">
                    <ShieldCheck size={21} />
                  </div>
                  <div>
                    <h2>Account security</h2>
                    <p>Manage access to your CareerTrack account.</p>
                  </div>
                </div>

                <div className="settings-security-row">
                  <div>
                    <strong>Authenticated session</strong>
                    <p>
                      You are accessing a protected account using your
                      authenticated session.
                    </p>
                  </div>
                  <span className="settings-status">Active</span>
                </div>

                <div className="settings-security-row">
                  <div>
                    <strong>Password management</strong>
                    <p>
                      Password changes require the backend password-change
                      endpoint to be connected.
                    </p>
                  </div>
                </div>
              </section>

              <section className="settings-card">
                <div className="settings-card-heading">
                  <div className="settings-icon">
                    <BriefcaseBusiness size={21} />
                  </div>
                  <div>
                    <h2>Workspace</h2>
                    <p>Quick access to your job search tools.</p>
                  </div>
                </div>

                <div className="settings-workspace-links">
                  <Link to="/dashboard">Dashboard</Link>
                  <Link to="/applications">Applications</Link>
                  <Link to="/kanban">Kanban Board</Link>
                  <Link to="/analytics">Analytics</Link>
                  <Link to="/profile">Profile & Resumes</Link>
                </div>
              </section>

              <section className="settings-card settings-danger-card">
                <div className="settings-card-heading">
                  <div className="settings-icon settings-danger-icon">
                    <LogOut size={21} />
                  </div>
                  <div>
                    <h2>Sign out</h2>
                    <p>
                      Sign out of your CareerTrack account on this device.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  className="settings-logout-button"
                  onClick={handleLogout}
                  disabled={loggingOut}
                >
                  <LogOut size={17} />
                  {loggingOut ? "Signing out..." : "Sign out"}
                </button>
              </section>
            </>
          )}
        </div>
      </main>
    </div>
  );
}