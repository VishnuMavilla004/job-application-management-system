
import { Bell, Menu, Search } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function DashboardHeader({
  onMenuClick,
  unreadCount,
}) {
  const { user } = useAuth();

  const initials = [user?.first_name, user?.last_name]
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return (
    <header className="dashboard-header">
      <button
        className="mobile-menu-button"
        onClick={onMenuClick}
        aria-label="Open navigation"
      >
        <Menu size={22} />
      </button>

      <div className="header-search">
        <Search size={18} />
        <span>Job application workspace</span>
      </div>

      <div className="header-actions">
        <button
          className="notification-button"
          aria-label={`${unreadCount} unread notifications`}
          title={`${unreadCount} unread notifications`}
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="notification-dot">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </button>

        <div className="header-user">
          <div className="user-avatar">
            {initials || user?.email?.[0]?.toUpperCase() || "U"}
          </div>

          <div className="header-user-details">
            <strong>
              {user?.first_name || user?.email || "User"}
            </strong>
            <span>My workspace</span>
          </div>
        </div>
      </div>
    </header>
  );
}
