import { useEffect, useRef, useState } from "react";
import { Bell, Menu, Search, CheckCheck, X } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { notificationsAPI } from "../../api/notifications.api";

function getNotificationData(response) {
  const body = response?.data ?? {};
  const payload = body?.data ?? body;

  const notifications = Array.isArray(payload)
    ? payload
    : payload?.results ?? [];

  const unreadCount = Number(
    body?.unread_count ??
    payload?.unread_count ??
    0
  );

  return { notifications, unreadCount };
}

function formatNotificationDate(value) {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "";

  return date.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function DashboardHeader({
  onMenuClick,
  unreadCount = 0,
  onUnreadCountChange,
}) {
  const { user } = useAuth();

  const [notifications, setNotifications] = useState([]);
  const [localUnreadCount, setLocalUnreadCount] = useState(unreadCount);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [notificationLoading, setNotificationLoading] = useState(false);
  const [notificationError, setNotificationError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);
  const [markingAll, setMarkingAll] = useState(false);

  const notificationRef = useRef(null);

  useEffect(() => {
    setLocalUnreadCount(Number(unreadCount) || 0);
  }, [unreadCount]);

  useEffect(() => {
    function handleOutsideClick(event) {
      if (
        notificationRef.current &&
        !notificationRef.current.contains(event.target)
      ) {
        setNotificationOpen(false);
      }
    }

    function handleEscape(event) {
      if (event.key === "Escape") {
        setNotificationOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  const updateUnreadCount = (count) => {
    const safeCount = Math.max(0, Number(count) || 0);

    setLocalUnreadCount(safeCount);
    onUnreadCountChange?.(safeCount);
  };

  const loadNotifications = async () => {
    setNotificationLoading(true);
    setNotificationError("");

    try {
      const response = await notificationsAPI.getAll({
        page: 1,
        page_size: 20,
      });

      const result = getNotificationData(response);

      setNotifications(result.notifications);
      updateUnreadCount(result.unreadCount);
    } catch (error) {
      setNotificationError(
        error.response?.data?.message ||
        error.response?.data?.detail ||
        "Unable to load notifications."
      );
    } finally {
      setNotificationLoading(false);
    }
  };

  const handleNotificationToggle = () => {
    const nextOpen = !notificationOpen;

    setNotificationOpen(nextOpen);

    if (nextOpen) {
      loadNotifications();
    }
  };

  const handleMarkAsRead = async (notification) => {
    if (notification.is_read || updatingId === notification.id) {
      return;
    }

    setUpdatingId(notification.id);

    try {
      await notificationsAPI.markAsRead(notification.id);

      setNotifications((previous) =>
        previous.map((item) =>
          item.id === notification.id
            ? { ...item, is_read: true }
            : item
        )
      );

      updateUnreadCount(localUnreadCount - 1);
    } catch (error) {
      setNotificationError(
        error.response?.data?.message ||
        error.response?.data?.detail ||
        "Unable to update notification."
      );
    } finally {
      setUpdatingId(null);
    }
  };

  const handleMarkAllAsRead = async () => {
    if (localUnreadCount === 0 || markingAll) return;

    setMarkingAll(true);
    setNotificationError("");

    try {
      await notificationsAPI.markAllAsRead();

      setNotifications((previous) =>
        previous.map((item) => ({
          ...item,
          is_read: true,
        }))
      );

      updateUnreadCount(0);
    } catch (error) {
      setNotificationError(
        error.response?.data?.message ||
        error.response?.data?.detail ||
        "Unable to mark notifications as read."
      );
    } finally {
      setMarkingAll(false);
    }
  };

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
        <div className="notification-wrapper" ref={notificationRef}>
          <button
            className="notification-button"
            onClick={handleNotificationToggle}
            aria-label={`${localUnreadCount} unread notifications`}
            aria-expanded={notificationOpen}
            aria-haspopup="true"
            title="Notifications"
          >
            <Bell size={20} />

            {localUnreadCount > 0 && (
              <span className="notification-dot">
                {localUnreadCount > 9 ? "9+" : localUnreadCount}
              </span>
            )}
          </button>

          {notificationOpen && (
            <div className="notification-panel">
              <div className="notification-panel-header">
                <div>
                  <h3>Notifications</h3>
                  <span>
                    {localUnreadCount} unread
                  </span>
                </div>

                <div className="notification-panel-actions">
                  {localUnreadCount > 0 && (
                    <button
                      type="button"
                      className="mark-all-button"
                      onClick={handleMarkAllAsRead}
                      disabled={markingAll}
                      title="Mark all as read"
                    >
                      <CheckCheck size={16} />
                      {markingAll ? "Updating..." : "Mark all read"}
                    </button>
                  )}

                  <button
                    type="button"
                    className="close-notification-button"
                    onClick={() => setNotificationOpen(false)}
                    aria-label="Close notifications"
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>

              {notificationError && (
                <div className="notification-error">
                  {notificationError}
                  <button onClick={loadNotifications}>
                    Retry
                  </button>
                </div>
              )}

              {notificationLoading ? (
                <div className="notification-state">
                  Loading notifications...
                </div>
              ) : notifications.length === 0 ? (
                <div className="notification-state">
                  <Bell size={26} />
                  <strong>No notifications yet</strong>
                  <span>
                    Updates about your applications will appear here.
                  </span>
                </div>
              ) : (
                <div className="notification-list">
                  {notifications.map((notification) => (
                    <article
                      key={notification.id}
                      className={`notification-item ${
                        notification.is_read ? "read" : "unread"
                      }`}
                    >
                      <div className="notification-item-content">
                        <div className="notification-item-title">
                          {!notification.is_read && (
                            <span className="notification-unread-dot" />
                          )}

                          <strong>
                            {notification.title}
                          </strong>
                        </div>

                        <p>{notification.message}</p>

                        {notification.application_job_title && (
                          <span className="notification-job-title">
                            {notification.application_job_title}
                          </span>
                        )}

                        <time>
                          {formatNotificationDate(
                            notification.created_at
                          )}
                        </time>
                      </div>

                      {!notification.is_read && (
                        <button
                          type="button"
                          className="notification-read-button"
                          onClick={() =>
                            handleMarkAsRead(notification)
                          }
                          disabled={updatingId === notification.id}
                          title="Mark as read"
                        >
                          {updatingId === notification.id
                            ? "..."
                            : "Mark read"}
                        </button>
                      )}
                    </article>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

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