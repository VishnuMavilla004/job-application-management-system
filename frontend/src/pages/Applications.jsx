
import { useCallback, useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, BriefcaseBusiness } from "lucide-react";
import { useSearchParams } from "react-router-dom";

import { applicationsAPI } from "../api/applications.api";
import { companiesAPI } from "../api/companies.api";

import Sidebar from "../components/dashboard/Sidebar";
import DashboardHeader from "../components/dashboard/DashboardHeader";

import ApplicationModal from "../components/applications/ApplicationModal";
import ApplicationForm from "../components/applications/ApplicationForm";
import ApplicationTable from "../components/applications/ApplicationTable";
import ApplicationDetails from "../components/applications/ApplicationDetails";
import DeleteConfirmation from "../components/applications/DeleteConfirmation";
import ApplicationFilters from "../components/applications/ApplicationFilters";
import ApplicationPagination from "../components/applications/ApplicationPagination";

import {
  extractList,
  unwrapResponse,
} from "../utils/dashboardFormatters";

import "../styles/applications.css";

// ============================================================
// CONSTANTS
// ============================================================

const URL_FILTER_KEYS = [
  "search",
  "status",
  "statuses",
  "company",
  "employment_type",
  "work_mode",
  "location",
  "applied_after",
  "applied_before",
  "deadline_after",
  "deadline_before",
  "minimum_salary",
  "maximum_salary",
];

const EMPTY_FILTERS = {
  search: "",
  status: "",
  statuses: "",
  company: "",
  employment_type: "",
  work_mode: "",
  location: "",
  applied_after: "",
  applied_before: "",
  deadline_after: "",
  deadline_before: "",
  minimum_salary: "",
  maximum_salary: "",
};

const DEFAULT_ORDERING = "-created_at";
const DEFAULT_PAGE_SIZE = 10;
const ALLOWED_PAGE_SIZES = [10, 20, 50, 100];

// ============================================================
// RESPONSE NORMALIZATION
// ============================================================

function normalizeResponse(response) {
  const unwrapped = unwrapResponse(response);

  // Supports standard DRF responses and the project's
  // standard { success, message, data } response format.
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

function getPageNumber(value) {
  const parsed = Number(value);

  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1;
}

function getPageSize(value) {
  const parsed = Number(value);

  return ALLOWED_PAGE_SIZES.includes(parsed)
    ? parsed
    : DEFAULT_PAGE_SIZE;
}

// ============================================================
// APPLICATIONS PAGE
// ============================================================

export default function Applications() {
  const [searchParams, setSearchParams] = useSearchParams();

  // ----------------------------------------------------------
  // APPLICATION AND COMPANY DATA
  // ----------------------------------------------------------

  const [applications, setApplications] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [totalCount, setTotalCount] = useState(0);

  // ----------------------------------------------------------
  // URL-DRIVEN FILTER, SORTING AND PAGINATION STATE
  // URL is the single source of truth for these values.
  // ----------------------------------------------------------

  const filters = useMemo(() => {
    return Object.fromEntries(
      URL_FILTER_KEYS.map((key) => [
        key,
        searchParams.get(key) || "",
      ])
    );
  }, [searchParams]);

  const ordering = searchParams.get("ordering") || DEFAULT_ORDERING;

  const page = getPageNumber(searchParams.get("page"));

  const pageSize = getPageSize(searchParams.get("page_size"));

  // ----------------------------------------------------------
  // UI STATES
  // ----------------------------------------------------------

  const [loading, setLoading] = useState(true);
  const [loadingApplications, setLoadingApplications] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [error, setError] = useState("");
  const [applicationsError, setApplicationsError] = useState("");
  const [success, setSuccess] = useState("");

  // ----------------------------------------------------------
  // MODAL AND SIDEBAR STATES
  // ----------------------------------------------------------

  const [modal, setModal] = useState(null);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // ----------------------------------------------------------
  // URL UPDATE HELPER
  // ----------------------------------------------------------

  const updateURL = useCallback(
    (nextFilters, nextOrdering, nextPage, nextPageSize) => {
      const params = new URLSearchParams();

      URL_FILTER_KEYS.forEach((key) => {
        const value = nextFilters[key];

        if (value !== "" && value !== null && value !== undefined) {
          params.set(key, String(value));
        }
      });

      params.set("ordering", nextOrdering);
      params.set("page", String(nextPage));
      params.set("page_size", String(nextPageSize));

      setSearchParams(params);
    },
    [setSearchParams]
  );

  // ----------------------------------------------------------
  // FETCH APPLICATIONS
  // ----------------------------------------------------------

  const fetchApplications = useCallback(async () => {
    setLoadingApplications(true);
    setApplicationsError("");

    try {
      const params = {
        page,
        page_size: pageSize,
        ordering,
      };

      Object.entries(filters).forEach(([key, value]) => {
        if (value !== "" && value !== null && value !== undefined) {
          params[key] = value;
        }
      });

      const response = await applicationsAPI.getAll(params);

      const rawPayload = response.data;
      const payload = normalizeResponse(response);

      const results = extractList(payload);

      setApplications(results);

      const count =
        payload?.count ??
        rawPayload?.data?.count ??
        rawPayload?.count ??
        results.length;

      setTotalCount(Number(count) || 0);
    } catch (err) {
      console.error("Unable to load applications:", err);

      setApplications([]);
      setTotalCount(0);

      setApplicationsError(
        err.response?.data?.message ||
        err.response?.data?.detail ||
        "Unable to load applications. Please try again."
      );
    } finally {
      setLoadingApplications(false);
      setLoading(false);
    }
  }, [filters, ordering, page, pageSize]);

  // Automatically fetch whenever URL-driven parameters change.
  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  // ----------------------------------------------------------
  // FETCH COMPANIES
  // ----------------------------------------------------------

  const loadCompanies = useCallback(async () => {
    try {
      const response = await companiesAPI.getAll({
        page: 1,
        page_size: 100,
      });

      const data = normalizeResponse(response);

      setCompanies(extractList(data));
    } catch (err) {
      console.error("Unable to load companies:", err);
      setCompanies([]);
    }
  }, []);

  useEffect(() => {
    loadCompanies();
  }, [loadCompanies]);

  // ----------------------------------------------------------
  // FILTER HANDLERS
  // ----------------------------------------------------------

  const handleApplyFilters = (nextFilters) => {
    updateURL(nextFilters, ordering, 1, pageSize);
  };

  const handleResetFilters = () => {
    updateURL(EMPTY_FILTERS, ordering, 1, pageSize);
  };

  // ----------------------------------------------------------
  // PAGINATION HANDLERS
  // ----------------------------------------------------------

  const handlePageChange = (nextPage) => {
    updateURL(filters, ordering, nextPage, pageSize);
  };

  const handlePageSizeChange = (nextSize) => {
    const validSize = getPageSize(nextSize);

    updateURL(filters, ordering, 1, validSize);
  };

  // ----------------------------------------------------------
  // SORTING HANDLER
  // ----------------------------------------------------------

  const handleOrderingChange = (event) => {
    const nextOrdering = event.target.value;

    updateURL(filters, nextOrdering, 1, pageSize);
  };

  // ----------------------------------------------------------
  // ERROR MESSAGE HELPER
  // ----------------------------------------------------------

  const getErrorMessage = (err, fallback) => {
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
  };

  // ----------------------------------------------------------
  // CREATE APPLICATION
  // ----------------------------------------------------------

  
const handleCreate = async (payload) => {
  setSubmitting(true);
  setError("");

  try {
    console.log("Submitted applied_date:", payload.applied_date);
    console.log("Browser local date:", new Date().toLocaleDateString("en-CA"));
    console.log("Browser ISO date:", new Date().toISOString().slice(0, 10));
    await applicationsAPI.create(payload);

    // Clear all active filters after successful creation.
    const emptyFilters = {
      search: "",
      status: "",
      statuses: "",
      company: "",
      employment_type: "",
      work_mode: "",
      location: "",
      applied_after: "",
      applied_before: "",
      deadline_after: "",
      deadline_before: "",
      minimum_salary: "",
      maximum_salary: "",
    };

    setFilters(emptyFilters);
    setPage(1);

    // Reset URL query parameters.
    updateURL(emptyFilters, ordering, 1, pageSize);

    setModal(null);
    setSelectedApplication(null);
    setSuccess("Application created successfully.");

    // The filter/page state change triggers the existing fetch effect.
  } catch (err) {
    setError(
      getErrorMessage(err, "Unable to create application.")
    );
  } finally {
    setSubmitting(false);
  }
};


  // ----------------------------------------------------------
  // UPDATE APPLICATION
  // ----------------------------------------------------------

  const handleUpdate = async (payload) => {
    if (!selectedApplication) return;

    setSubmitting(true);
    setError("");

    try {
      await applicationsAPI.update(selectedApplication.id, payload);

      setModal(null);
      setSelectedApplication(null);
      setSuccess("Application updated successfully.");

      await fetchApplications();
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to update application.")
      );
    } finally {
      setSubmitting(false);
    }
  };

  // ----------------------------------------------------------
  // DELETE APPLICATION
  // ----------------------------------------------------------

  const handleDelete = async () => {
    if (!selectedApplication) return;

    setDeleting(true);
    setError("");

    try {
      await applicationsAPI.delete(selectedApplication.id);

      setModal(null);
      setSelectedApplication(null);
      setSuccess("Application deleted successfully.");

      // If the deleted record was the only item on the page,
      // navigate to the previous page.
      if (applications.length === 1 && page > 1) {
        updateURL(filters, ordering, page - 1, pageSize);
      } else {
        await fetchApplications();
      }
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to delete application.")
      );
    } finally {
      setDeleting(false);
    }
  };

  // ----------------------------------------------------------
  // MODAL HANDLERS
  // ----------------------------------------------------------

  const openCreate = () => {
    setSelectedApplication(null);
    setModal("create");
    setError("");
    setSuccess("");
  };

  const openEdit = (application) => {
    setSelectedApplication(application);
    setModal("edit");
    setError("");
    setSuccess("");
  };

  const openView = (application) => {
    setSelectedApplication(application);
    setModal("view");
    setError("");
    setSuccess("");
  };

  const openDelete = (application) => {
    setSelectedApplication(application);
    setModal("delete");
    setError("");
    setSuccess("");
  };

  const closeModal = () => {
    if (submitting || deleting) return;

    setModal(null);
    setSelectedApplication(null);
  };

  // ==========================================================
  // RENDER
  // ==========================================================

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

        <div className="dashboard-content applications-content">

          {/* PAGE HEADING */}
          <div className="applications-page-heading">
            <div>
              <p className="dashboard-eyebrow">WORKSPACE</p>

              <h1>Job Applications</h1>

              <p className="dashboard-subtitle">
                Manage and track all your job opportunities.
              </p>
            </div>

            <button
              type="button"
              className="primary-button create-application-button"
              onClick={openCreate}
              disabled={companies.length === 0}
              title={
                companies.length === 0
                  ? "Add a company before creating an application."
                  : "Create application"
              }
            >
              <Plus size={18} />
              Add application
            </button>
          </div>

          {/* SUCCESS AND ERROR MESSAGES */}
          {error && (
            <div className="applications-alert error-alert">
              {error}
            </div>
          )}

          {success && (
            <div className="applications-alert success-alert">
              {success}
            </div>
          )}

          {/* APPLICATION SUMMARY */}
          <section className="applications-summary">
            <div className="applications-summary-icon">
              <BriefcaseBusiness size={23} />
            </div>

            <div>
              <span>Total applications</span>
              <strong>{totalCount}</strong>
            </div>
          </section>

          {/* APPLICATIONS PANEL */}
          <section className="applications-panel">

            {/* PANEL HEADING */}
            <div className="applications-panel-heading">
              <div>
                <h2>All applications</h2>

                <p>
                  View and manage your submitted applications.
                </p>
              </div>

              <button
                type="button"
                className="refresh-button"
                onClick={fetchApplications}
                disabled={loadingApplications}
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>

            {/* FILTERS */}
            <ApplicationFilters
              companies={companies}
              initialFilters={filters}
              onApply={handleApplyFilters}
              onReset={handleResetFilters}
              loading={loadingApplications}
            />

            {/* SORTING AND RESULT COUNT */}
            <div className="applications-toolbar">
              <div>
                <strong>{totalCount}</strong> applications found
              </div>

              <label>
                Sort by

                <select
                  value={ordering}
                  onChange={handleOrderingChange}
                >
                  <option value="-created_at">Recently added</option>
                  <option value="created_at">Oldest added</option>
                  <option value="job_title">Job title (A–Z)</option>
                  <option value="-job_title">Job title (Z–A)</option>
                  <option value="-applied_date">Applied date (newest)</option>
                  <option value="applied_date">Applied date (oldest)</option>
                  <option value="-deadline">Deadline (latest)</option>
                  <option value="deadline">Deadline (earliest)</option>
                  <option value="company__name">Company (A–Z)</option>
                  <option value="-company__name">Company (Z–A)</option>
                  <option value="-salary_max">Highest salary</option>
                  <option value="salary_min">Lowest salary</option>
                </select>
              </label>
            </div>

            {/* API ERROR */}
            {applicationsError && (
              <div className="applications-error" role="alert">
                {applicationsError}
              </div>
            )}

            {/* APPLICATION TABLE */}
            {loadingApplications || loading ? (
              <div className="applications-loading">
                <div className="spinner" />
                <p>Loading applications...</p>
              </div>
            ) : (
              <ApplicationTable
                applications={applications}
                onView={openView}
                onEdit={openEdit}
                onDelete={openDelete}
              />
            )}

            {/* PAGINATION */}
            <ApplicationPagination
              count={totalCount}
              page={page}
              pageSize={pageSize}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
              loading={loadingApplications}
            />
          </section>

          {/* COMPANY WARNING */}
          {companies.length === 0 && !loading && (
            <p className="company-warning">
              No companies are available. Add a company through your
              existing company API or admin interface before creating
              an application.
            </p>
          )}
        </div>
      </main>

      {/* ======================================================
          CREATE MODAL
      ====================================================== */}

      {modal === "create" && (
        <ApplicationModal
          title="Create job application"
          onClose={closeModal}
          size="large"
        >
          {error && (
            <div className="applications-alert error-alert">
              {error}
            </div>
          )}

          <ApplicationForm
            companies={companies}
            onSubmit={handleCreate}
            onCancel={closeModal}
            submitting={submitting}
          />
        </ApplicationModal>
      )}

      {/* ======================================================
          EDIT MODAL
      ====================================================== */}

      {modal === "edit" && (
        <ApplicationModal
          title="Edit job application"
          onClose={closeModal}
          size="large"
        >
          {error && (
            <div className="applications-alert error-alert">
              {error}
            </div>
          )}

          <ApplicationForm
            initialData={selectedApplication}
            companies={companies}
            onSubmit={handleUpdate}
            onCancel={closeModal}
            submitting={submitting}
          />
        </ApplicationModal>
      )}

      {/* ======================================================
          VIEW MODAL
      ====================================================== */}

      {modal === "view" && selectedApplication && (
        <ApplicationModal
          title="Application details"
          onClose={closeModal}
          size="large"
        >
          <ApplicationDetails
            application={selectedApplication}
          />
        </ApplicationModal>
      )}

      {/* ======================================================
          DELETE MODAL
      ====================================================== */}

      {modal === "delete" && selectedApplication && (
        <ApplicationModal
          title="Confirm deletion"
          onClose={closeModal}
          size="small"
        >
          <DeleteConfirmation
            application={selectedApplication}
            onConfirm={handleDelete}
            onCancel={closeModal}
            deleting={deleting}
          />
        </ApplicationModal>
      )}
    </div>
  );
}
