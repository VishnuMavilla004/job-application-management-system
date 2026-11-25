
import { useCallback, useEffect, useState } from "react";
import { Plus, RefreshCw, BriefcaseBusiness } from "lucide-react";

import { applicationsAPI } from "../api/applications.api";
import { companiesAPI } from "../api/companies.api";

import Sidebar from "../components/dashboard/Sidebar";
import DashboardHeader from "../components/dashboard/DashboardHeader";

import ApplicationModal from "../components/applications/ApplicationModal";
import ApplicationForm from "../components/applications/ApplicationForm";
import ApplicationTable from "../components/applications/ApplicationTable";
import ApplicationDetails from "../components/applications/ApplicationDetails";
import DeleteConfirmation from "../components/applications/DeleteConfirmation";

import {
  extractList,
  unwrapResponse,
} from "../utils/dashboardFormatters";

import "../styles/applications.css";

export default function Applications() {
  const [applications, setApplications] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [modal, setModal] = useState(null);
  const [selectedApplication, setSelectedApplication] = useState(null);

  const [sidebarOpen, setSidebarOpen] = useState(false);

  const loadApplications = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await applicationsAPI.getAll({
        page: 1,
        page_size: 100,
        ordering: "-created_at",
      });

      const data = unwrapResponse(response);
      setApplications(extractList(data));
    } catch (err) {
      setError(
        err.response?.data?.message ||
        err.response?.data?.detail ||
        "Unable to load applications."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const loadCompanies = useCallback(async () => {
    try {
      const response = await companiesAPI.getAll({
        page: 1,
        page_size: 100,
      });

      const data = unwrapResponse(response);
      setCompanies(extractList(data));
    } catch (err) {
      console.error("Unable to load companies:", err);
      setCompanies([]);
    }
  }, []);

  useEffect(() => {
    loadApplications();
    loadCompanies();
  }, [loadApplications, loadCompanies]);

  const handleCreate = async (payload) => {
    setSubmitting(true);
    setError("");

    try {
      await applicationsAPI.create(payload);

      setModal(null);
      setSuccess("Application created successfully.");
      await loadApplications();
    } catch (err) {
      const data = err.response?.data;
      const message =
        data?.message ||
        data?.detail ||
        (data ? Object.entries(data)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
          .join(" | ") : null);

      setError(message || "Unable to create application.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (payload) => {
    if (!selectedApplication) return;

    setSubmitting(true);
    setError("");

    try {
      await applicationsAPI.update(
        selectedApplication.id,
        payload
      );

      setModal(null);
      setSelectedApplication(null);
      setSuccess("Application updated successfully.");
      await loadApplications();
    } catch (err) {
      const data = err.response?.data;
      const message =
        data?.message ||
        data?.detail ||
        (data ? Object.entries(data)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
          .join(" | ") : null);

      setError(message || "Unable to update application.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedApplication) return;

    setDeleting(true);
    setError("");

    try {
      await applicationsAPI.delete(selectedApplication.id);

      setModal(null);
      setSelectedApplication(null);
      setSuccess("Application deleted successfully.");
      await loadApplications();
    } catch (err) {
      setError(
        err.response?.data?.message ||
        err.response?.data?.detail ||
        "Unable to delete application."
      );
    } finally {
      setDeleting(false);
    }
  };

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

          <section className="applications-summary">
            <div className="applications-summary-icon">
              <BriefcaseBusiness size={23} />
            </div>

            <div>
              <span>Total applications</span>
              <strong>{applications.length}</strong>
            </div>
          </section>

          <section className="applications-panel">
            <div className="applications-panel-heading">
              <div>
                <h2>All applications</h2>
                <p>View and manage your submitted applications.</p>
              </div>

              <button
                type="button"
                className="refresh-button"
                onClick={loadApplications}
                disabled={loading}
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>

            {loading ? (
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
          </section>

          {companies.length === 0 && !loading && (
            <p className="company-warning">
              No companies are available. Add a company through your
              existing company API or admin interface before creating
              an application.
            </p>
          )}
        </div>
      </main>

      {modal === "create" && (
        <ApplicationModal
          title="Create job application"
          onClose={closeModal}
          size="large"
        >{error && (
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

      {modal === "view" && selectedApplication && (
        <ApplicationModal
          title="Application details"
          onClose={closeModal}
          size="large"
        >
          <ApplicationDetails application={selectedApplication} />
        </ApplicationModal>
      )}

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
