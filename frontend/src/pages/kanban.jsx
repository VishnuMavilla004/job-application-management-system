
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BriefcaseBusiness,
  GripVertical,
  RefreshCw,
} from "lucide-react";

import { applicationsAPI } from "../api/applications.api";

import Sidebar from "../components/dashboard/Sidebar";
import DashboardHeader from "../components/dashboard/DashboardHeader";

import {
  extractList,
  unwrapResponse,
} from "../utils/dashboardFormatters";

import "../styles/kanban.css";

// ============================================================
// CONSTANTS
// ============================================================

const PAGE_SIZE = 100;

const STATUS_COLUMNS = [
  { key: "applied", label: "Applied", color: "blue" },
  { key: "assessment", label: "Assessment", color: "purple" },
  { key: "interview", label: "Interview", color: "amber" },
  { key: "offer", label: "Offer", color: "green" },
  { key: "rejected", label: "Rejected", color: "red" },
  { key: "withdrawn", label: "Withdrawn", color: "gray" },
];

const ALLOWED_STATUS_TRANSITIONS = {
  applied: ["assessment", "interview", "rejected", "withdrawn"],
  assessment: ["interview", "rejected", "withdrawn"],
  interview: ["offer", "rejected", "withdrawn"],
  offer: ["withdrawn"],
  rejected: [],
  withdrawn: [],
};

// ============================================================
// RESPONSE HELPERS
// ============================================================

function normalizeResponse(response) {
  const unwrapped = unwrapResponse(response);

  if (
    unwrapped &&
    typeof unwrapped === "object" &&
    !Array.isArray(unwrapped) &&
    unwrapped.data !== undefined
  ) {
    return unwrapped.data;
  }

  return unwrapped;
}

function getErrorMessage(err, fallback) {
  const data = err.response?.data;

  if (data?.message) return data.message;
  if (data?.detail) return data.detail;

  if (data && typeof data === "object") {
    return Object.entries(data)
      .map(([key, value]) => {
        const message = Array.isArray(value)
          ? value.join(", ")
          : String(value);

        return `${key}: ${message}`;
      })
      .join(" | ");
  }

  return fallback;
}

function getApplicationId(application) {
  return application.id ?? application.pk;
}

function getApplicationTitle(application) {
  return (
    application.job_title ||
    application.title ||
    application.position ||
    "Untitled position"
  );
}

function getCompanyName(application) {
  if (typeof application.company === "string") {
    return application.company;
  }

  return (
    application.company?.name ||
    application.company_name ||
    "Company not specified"
  );
}

function formatDate(value) {
  if (!value) return "Not specified";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Not specified";
  }

  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

// ============================================================
// KANBAN PAGE
// ============================================================

export default function Kanban() {
  const [applications, setApplications] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [draggedId, setDraggedId] = useState(null);
  const [dragOverStatus, setDragOverStatus] = useState(null);

  const [updatingIds, setUpdatingIds] = useState(() => new Set());

  // ----------------------------------------------------------
  // FETCH ALL APPLICATIONS
  // ----------------------------------------------------------

  const fetchApplications = useCallback(async (showRefresh = false) => {
    if (showRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError("");

    try {
      const firstResponse = await applicationsAPI.getAll({
        page: 1,
        page_size: PAGE_SIZE,
        ordering: "-created_at",
      });

      const rawFirstPayload = firstResponse.data;
      const firstPayload = normalizeResponse(firstResponse);

      const firstResults = extractList(firstPayload);

      const rawCount =
        firstPayload?.count ??
        rawFirstPayload?.data?.count ??
        rawFirstPayload?.count ??
        firstResults.length;

      const totalCount = Number(rawCount) || firstResults.length;

      const totalPages = Math.ceil(totalCount / PAGE_SIZE);

      const allApplications = [...firstResults];

      // Fetch the remaining pages so the board contains
      // every application, not only the first 100.
      for (let page = 2; page <= totalPages; page += 1) {
        const response = await applicationsAPI.getAll({
          page,
          page_size: PAGE_SIZE,
          ordering: "-created_at",
        });

        const results = extractList(normalizeResponse(response));

        allApplications.push(...results);
      }

      setApplications(allApplications);
    } catch (err) {
      console.error("Unable to load Kanban applications:", err);

      setApplications([]);

      setError(
        getErrorMessage(
          err,
          "Unable to load applications. Please try again."
        )
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  // ----------------------------------------------------------
  // GROUP APPLICATIONS BY STATUS
  // ----------------------------------------------------------

  const groupedApplications = useMemo(() => {
    const groups = Object.fromEntries(
      STATUS_COLUMNS.map((column) => [column.key, []])
    );

    applications.forEach((application) => {
      const status = application.status;

      if (groups[status]) {
        groups[status].push(application);
      }
    });

    return groups;
  }, [applications]);

  // ----------------------------------------------------------
  // STATUS UPDATE
  // ----------------------------------------------------------

  const changeApplicationStatus = async (
    application,
    nextStatus
  ) => {
    const id = getApplicationId(application);
    const currentStatus = application.status;

    if (!id) {
      setError("Unable to identify this application.");
      return;
    }

    if (currentStatus === nextStatus) {
      return;
    }

    const allowedTransitions =
      ALLOWED_STATUS_TRANSITIONS[currentStatus] || [];

    if (!allowedTransitions.includes(nextStatus)) {
      setError(
        `Moving from ${
          currentStatus || "unknown"
        } to ${nextStatus} is not allowed.`
      );
      return;
    }

    if (updatingIds.has(id)) {
      return;
    }

    setError("");
    setSuccess("");

    setUpdatingIds((previous) => {
      const next = new Set(previous);
      next.add(id);
      return next;
    });

    try {
      await applicationsAPI.updateStatus(id, {
        status: nextStatus,
        remarks: "Status updated from Kanban board.",
      });

      setApplications((previous) =>
        previous.map((item) =>
          getApplicationId(item) === id
            ? { ...item, status: nextStatus }
            : item
        )
      );

      const destination = STATUS_COLUMNS.find(
        (column) => column.key === nextStatus
      );

      setSuccess(
        `${getApplicationTitle(application)} moved to ${
          destination?.label || nextStatus
        }.`
      );
    } catch (err) {
      console.error("Unable to update application status:", err);

      setError(
        getErrorMessage(
          err,
          "Status update failed. Your application was not moved."
        )
      );
    } finally {
      setUpdatingIds((previous) => {
        const next = new Set(previous);
        next.delete(id);
        return next;
      });

      setDraggedId(null);
      setDragOverStatus(null);
    }
  };

  // ----------------------------------------------------------
  // DRAG AND DROP HANDLERS
  // ----------------------------------------------------------

  const handleDragStart = (event, application) => {
    const id = getApplicationId(application);

    if (!id || updatingIds.has(id)) {
      event.preventDefault();
      return;
    }

    setDraggedId(id);

    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", String(id));
  };

  const handleDragEnd = () => {
    setDraggedId(null);
    setDragOverStatus(null);
  };

  const handleDragOver = (event, destinationStatus) => {
    event.preventDefault();

    const draggedApplication = applications.find(
      (application) =>
        String(getApplicationId(application)) === String(draggedId)
    );

    if (!draggedApplication) return;

    const allowed =
      ALLOWED_STATUS_TRANSITIONS[draggedApplication.status] || [];

    if (allowed.includes(destinationStatus)) {
      event.dataTransfer.dropEffect = "move";
      setDragOverStatus(destinationStatus);
    } else {
      event.dataTransfer.dropEffect = "none";
      setDragOverStatus(null);
    }
  };

  const handleDrop = async (event, destinationStatus) => {
    event.preventDefault();

    const transferredId = event.dataTransfer.getData("text/plain");

    const id = transferredId || draggedId;

    const application = applications.find(
      (item) =>
        String(getApplicationId(item)) === String(id)
    );

    setDraggedId(null);
    setDragOverStatus(null);

    if (!application) return;

    await changeApplicationStatus(application, destinationStatus);
  };

  // ----------------------------------------------------------
  // MANUAL STATUS CHANGE
  // ----------------------------------------------------------

  const handleManualStatusChange = async (
    application,
    event
  ) => {
    const nextStatus = event.target.value;

    event.target.value = "";

    if (!nextStatus) return;

    await changeApplicationStatus(application, nextStatus);
  };

  // ----------------------------------------------------------
  // RENDER
  // ----------------------------------------------------------

  return (
    <div className="dashboard-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="dashboard-main">
        <DashboardHeader
          onMenuClick={() => setSidebarOpen(true)}
          unreadCount={0}
        />

        <div className="dashboard-content kanban-content">
          {/* PAGE HEADING */}

          <div className="kanban-page-heading">
            <div>
              <p className="dashboard-eyebrow">WORKSPACE</p>

              <h1>Kanban Board</h1>

              <p className="dashboard-subtitle">
                Track your job applications across every stage
                of the recruitment process.
              </p>
            </div>

            <button
              type="button"
              className="kanban-refresh-button"
              onClick={() => fetchApplications(true)}
              disabled={loading || refreshing}
            >
              <RefreshCw
                size={16}
                className={refreshing ? "kanban-spinning" : ""}
              />
              Refresh board
            </button>
          </div>

          {/* SUMMARY */}

          <div className="kanban-summary">
            <div className="kanban-summary-icon">
              <BriefcaseBusiness size={22} />
            </div>

            <div>
              <span>Total applications</span>
              <strong>{applications.length}</strong>
            </div>

            <div className="kanban-summary-divider" />

            <div>
              <span>Active applications</span>
              <strong>
                {applications.filter((application) =>
                  ["applied", "assessment", "interview"].includes(
                    application.status
                  )
                ).length}
              </strong>
            </div>
          </div>

          {/* ALERTS */}

          {error && (
            <div className="kanban-alert kanban-error" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="kanban-alert kanban-success" role="status">
              {success}
            </div>
          )}

          {/* BOARD */}

          <section className="kanban-board-section">
            <div className="kanban-board-heading">
              <div>
                <h2>Application pipeline</h2>
                <p>
                  Drag a card to another column or use its status
                  selector. Only valid status transitions are allowed.
                </p>
              </div>

              <span className="kanban-board-count">
                {applications.length} records
              </span>
            </div>

            {loading ? (
              <div className="kanban-loading">
                <div className="spinner" />
                <p>Loading your application board...</p>
              </div>
            ) : error && applications.length === 0 ? (
              <div className="kanban-empty">
                <BriefcaseBusiness size={30} />
                <h3>Unable to display the board</h3>
                <p>Check your connection and try refreshing.</p>

                <button
                  type="button"
                  className="kanban-refresh-button"
                  onClick={() => fetchApplications(true)}
                  disabled={refreshing}
                >
                  Try again
                </button>
              </div>
            ) : (
              <div className="kanban-board">
                {STATUS_COLUMNS.map((column) => {
                  const columnApplications =
                    groupedApplications[column.key] || [];

                  const isDropTarget =
                    dragOverStatus === column.key;

                  return (
                    <section
                      key={column.key}
                      className={`kanban-column kanban-column-${column.color} ${
                        isDropTarget ? "kanban-column-drag-over" : ""
                      }`}
                      onDragOver={(event) =>
                        handleDragOver(event, column.key)
                      }
                      onDragLeave={(event) => {
                        if (
                          !event.currentTarget.contains(
                            event.relatedTarget
                          )
                        ) {
                          setDragOverStatus(null);
                        }
                      }}
                      onDrop={(event) =>
                        handleDrop(event, column.key)
                      }
                    >
                      <div className="kanban-column-heading">
                        <div className="kanban-column-title">
                          <span
                            className={`kanban-status-dot dot-${column.color}`}
                          />

                          <h3>{column.label}</h3>
                        </div>

                        <span className="kanban-column-count">
                          {columnApplications.length}
                        </span>
                      </div>

                      <div className="kanban-column-body">
                        {columnApplications.length === 0 ? (
                          <div className="kanban-column-empty">
                            <p>No applications</p>
                            <span>
                              Applications will appear here.
                            </span>
                          </div>
                        ) : (
                          columnApplications.map((application) => {
                            const id = getApplicationId(application);

                            const isUpdating = updatingIds.has(id);

                            const allowedTransitions =
                              ALLOWED_STATUS_TRANSITIONS[
                                application.status
                              ] || [];

                            return (
                              <article
                                key={id}
                                className={`kanban-card ${
                                  draggedId === id
                                    ? "kanban-card-dragging"
                                    : ""
                                } ${
                                  isUpdating
                                    ? "kanban-card-updating"
                                    : ""
                                }`}
                                draggable={
                                  !isUpdating &&
                                  allowedTransitions.length > 0
                                }
                                onDragStart={(event) =>
                                  handleDragStart(event, application)
                                }
                                onDragEnd={handleDragEnd}
                              >
                                <div className="kanban-card-top">
                                  <span className="kanban-card-company">
                                    {getCompanyName(application)}
                                  </span>

                                  <GripVertical
                                    size={17}
                                    className="kanban-drag-icon"
                                    aria-hidden="true"
                                  />
                                </div>

                                <h4>
                                  {getApplicationTitle(application)}
                                </h4>

                                {application.location && (
                                  <p className="kanban-card-location">
                                    {application.location}
                                  </p>
                                )}

                                <div className="kanban-card-meta">
                                  <div>
                                    <span>Applied</span>
                                    <strong>
                                      {formatDate(
                                        application.applied_date
                                      )}
                                    </strong>
                                  </div>

                                  {application.deadline && (
                                    <div>
                                      <span>Deadline</span>
                                      <strong>
                                        {formatDate(
                                          application.deadline
                                        )}
                                      </strong>
                                    </div>
                                  )}
                                </div>

                                <div className="kanban-card-footer">
                                  <label
                                    className="kanban-status-select-label"
                                    htmlFor={`status-${id}`}
                                  >
                                    Move to
                                  </label>

                                  <select
                                    id={`status-${id}`}
                                    value=""
                                    disabled={
                                      isUpdating ||
                                      allowedTransitions.length === 0
                                    }
                                    onChange={(event) =>
                                      handleManualStatusChange(
                                        application,
                                        event
                                      )
                                    }
                                    aria-label={`Change status for ${getApplicationTitle(
                                      application
                                    )}`}
                                  >
                                    <option value="">
                                      {isUpdating
                                        ? "Updating..."
                                        : allowedTransitions.length === 0
                                          ? "No further moves"
                                          : "Select status"}
                                    </option>

                                    {STATUS_COLUMNS.filter((item) =>
                                      allowedTransitions.includes(item.key)
                                    ).map((item) => (
                                      <option
                                        key={item.key}
                                        value={item.key}
                                      >
                                        {item.label}
                                      </option>
                                    ))}
                                  </select>

                                  {isUpdating && (
                                    <span className="kanban-card-spinner" />
                                  )}
                                </div>
                              </article>
                            );
                          })
                        )}
                      </div>

                      <div className="kanban-column-footer">
                        {columnApplications.length}{" "}
                        {columnApplications.length === 1
                          ? "application"
                          : "applications"}
                      </div>
                    </section>
                  );
                })}
              </div>
            )}
          </section>

          <p className="kanban-board-tip">
            <ArrowRight size={14} />
            Rejected and withdrawn applications are terminal
            statuses. They cannot be moved to another stage.
          </p>
        </div>
      </main>
    </div>
  );
}
