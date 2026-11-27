
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  FileText,
  Upload,
  Download,
  Trash2,
  Star,
  UserRound,
  Save,
  RefreshCw,
  LockKeyhole,
  Eye,
  EyeOff,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { authAPI } from "../api/auth.api";
import { resumesAPI } from "../api/resumes.api";
import { notificationsAPI } from "../api/notifications.api";

import Sidebar from "../components/dashboard/Sidebar";
import DashboardHeader from "../components/dashboard/DashboardHeader";

import "../styles/profile.css";

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ALLOWED_EXTENSIONS = [".pdf", ".doc", ".docx"];

const INITIAL_PASSWORD_DATA = {
  old_password: "",
  new_password: "",
  confirm_password: "",
};

function unwrap(response) {
  return response?.data?.data ?? response?.data ?? {};
}

function formatErrorValue(value) {
  if (Array.isArray(value)) {
    return value.map(formatErrorValue).join(" ");
  }

  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${formatErrorValue(item)}`)
      .join(" ");
  }

  return String(value);
}

function getError(error, fallback) {
  const body = error?.response?.data;

  if (typeof body?.message === "string") {
    return body.message;
  }

  if (typeof body?.detail === "string") {
    return body.detail;
  }

  if (body?.errors) {
    return formatErrorValue(body.errors);
  }

  if (body && typeof body === "object") {
    const message = Object.entries(body)
      .map(([key, value]) => `${key}: ${formatErrorValue(value)}`)
      .join(" ");

    if (message) return message;
  }

  return error?.message || fallback;
}

function getResumeList(response) {
  const payload = unwrap(response);

  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;

  return [];
}

export default function Profile() {
  const { refreshProfile, clearSession } = useAuth();
  const navigate = useNavigate();

  const fileInputRef = useRef(null);

  const [profile, setProfile] = useState({
    first_name: "",
    last_name: "",
    phone_number: "",
    email: "",
    date_joined: "",
  });

  const [resumes, setResumes] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const [passwordData, setPasswordData] = useState(
    INITIAL_PASSWORD_DATA
  );

  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [actionId, setActionId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Load profile, resumes, and notification count.
  const loadPage = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [
        profileResult,
        resumeResult,
        notificationResult,
      ] = await Promise.allSettled([
        authAPI.getProfile(),
        resumesAPI.getAll(),
        notificationsAPI.getAll({
          page: 1,
          page_size: 1,
        }),
      ]);

      if (profileResult.status === "rejected") {
        throw profileResult.reason;
      }

      const profileData = profileResult.value?.user ??
        profileResult.value;

      setProfile({
        first_name: profileData.first_name ?? "",
        last_name: profileData.last_name ?? "",
        phone_number: profileData.phone_number ?? "",
        email: profileData.email ?? "",
        date_joined: profileData.date_joined ?? "",
      });

      if (resumeResult.status === "fulfilled") {
        setResumes(getResumeList(resumeResult.value));
      } else {
        setError(
          getError(
            resumeResult.reason,
            "Unable to load your resumes."
          )
        );
      }

      if (notificationResult.status === "fulfilled") {
        const notificationData = unwrap(
          notificationResult.value
        );

        setUnreadCount(
          Number(
            notificationData.unread_count ??
            notificationResult.value?.unread_count ??
            0
          )
        );
      }
    } catch (err) {
      setError(
        getError(err, "Unable to load your profile.")
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPage();
  }, [loadPage]);

  // Profile form.
  const handleProfileChange = (event) => {
    const { name, value } = event.target;

    setProfile((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSaveProfile = async (event) => {
    event.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      await authAPI.updateProfile({
        first_name: profile.first_name.trim(),
        last_name: profile.last_name.trim(),
        phone_number: profile.phone_number.trim(),
      });

      await refreshProfile();

      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError(
        getError(err, "Unable to update your profile.")
      );
    } finally {
      setSaving(false);
    }
  };

  // Password management.
  const handlePasswordChange = (event) => {
    const { name, value } = event.target;

    setPasswordData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords((previous) => ({
      ...previous,
      [field]: !previous[field],
    }));
  };

  const handleChangePassword = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    const {
      old_password,
      new_password,
      confirm_password,
    } = passwordData;

    if (!old_password || !new_password || !confirm_password) {
      setError("Please complete all password fields.");
      return;
    }

    if (new_password !== confirm_password) {
      setError(
        "New password and confirmation do not match."
      );
      return;
    }

    if (old_password === new_password) {
      setError(
        "New password must differ from your current password."
      );
      return;
    }

    setChangingPassword(true);

    try {
      await authAPI.changePassword(passwordData);

      setPasswordData(INITIAL_PASSWORD_DATA);

      // The backend has already revoked outstanding refresh tokens.
      // Clear the local session without making another logout request.
      clearSession();

      navigate("/login", {
        replace: true,
        state: {
          message:
            "Password changed successfully. Please log in again.",
        },
      });
    } catch (err) {
      setError(
        getError(err, "Unable to change your password.")
      );
    } finally {
      setChangingPassword(false);
    }
  };

  // Resume upload.
  const handleUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setError("");
    setSuccess("");

    const extension = file.name
      .slice(file.name.lastIndexOf("."))
      .toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setError(
        "Only PDF, DOC and DOCX files are supported."
      );
      event.target.value = "";
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError(
        "Resume file size cannot exceed 5 MB."
      );
      event.target.value = "";
      return;
    }

    const formData = new FormData();

    formData.append(
      "title",
      file.name.replace(/\.[^/.]+$/, "")
    );

    formData.append("file", file);

    setUploading(true);

    try {
      await resumesAPI.upload(formData);

      const response = await resumesAPI.getAll();

      setResumes(getResumeList(response));
      setSuccess("Resume uploaded successfully.");
    } catch (err) {
      setError(
        getError(err, "Unable to upload your resume.")
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  // Set default resume.
  const handleSetDefault = async (id) => {
    setActionId(id);
    setError("");
    setSuccess("");

    try {
      await resumesAPI.setDefault(id);

      const response = await resumesAPI.getAll();

      setResumes(getResumeList(response));
      setSuccess("Default resume updated.");
    } catch (err) {
      setError(
        getError(err, "Unable to change default resume.")
      );
    } finally {
      setActionId(null);
    }
  };

  // Download resume.
  const handleDownload = async (resume) => {
    setActionId(resume.id);
    setError("");

    try {
      const response = await resumesAPI.download(resume.id);

      const blob = new Blob([response.data], {
        type: response.headers?.["content-type"] ||
          "application/octet-stream",
      });

      const blobUrl = window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = blobUrl;
      link.download =
        resume.file?.split("/").pop() ||
        `${resume.title || "resume"}.pdf`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.setTimeout(() => {
        window.URL.revokeObjectURL(blobUrl);
      }, 1000);
    } catch (err) {
      setError(
        getError(err, "Unable to download resume.")
      );
    } finally {
      setActionId(null);
    }
  };

  // Delete resume.
  const handleDelete = async (resume) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${resume.title}"?`
    );

    if (!confirmed) return;

    setActionId(resume.id);
    setError("");
    setSuccess("");

    try {
      // Supports either API method name without assuming
      // which one your resumes.api.js currently exports.
      const deleteMethod =
        resumesAPI.delete ?? resumesAPI.remove;

      if (typeof deleteMethod !== "function") {
        throw new Error(
          "Resume deletion is not configured in resumes.api.js."
        );
      }

      await deleteMethod.call(resumesAPI, resume.id);

      const response = await resumesAPI.getAll();

      setResumes(getResumeList(response));
      setSuccess("Resume deleted successfully.");
    } catch (err) {
      setError(
        getError(err, "Unable to delete your resume.")
      );
    } finally {
      setActionId(null);
    }
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
          unreadCount={unreadCount}
          onUnreadCountChange={setUnreadCount}
        />

        <div className="dashboard-content profile-page">
          {/* Page heading */}
          <div className="dashboard-title-row">
            <div>
              <p className="dashboard-eyebrow">ACCOUNT</p>

              <h1>Profile & Resumes</h1>

              <p className="dashboard-subtitle">
                Manage your personal information, password,
                and resume documents.
              </p>
            </div>

            <button
              type="button"
              className="refresh-button"
              onClick={loadPage}
              disabled={loading}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          {/* Global messages */}
          {error && (
            <div
              className="profile-alert profile-alert-error"
              role="alert"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              className="profile-alert profile-alert-success"
              role="status"
            >
              {success}
            </div>
          )}

          {loading ? (
            <div className="profile-loading">
              Loading profile...
            </div>
          ) : (
            <>
              {/* Personal information */}
              <section className="profile-card">
                <div className="profile-section-heading">
                  <div className="profile-section-icon">
                    <UserRound size={21} />
                  </div>

                  <div>
                    <h2>Personal information</h2>
                    <p>Update your account details.</p>
                  </div>
                </div>

                <form onSubmit={handleSaveProfile}>
                  <div className="profile-form-grid">
                    <label>
                      First name

                      <input
                        name="first_name"
                        value={profile.first_name}
                        onChange={handleProfileChange}
                        maxLength={150}
                        required
                      />
                    </label>

                    <label>
                      Last name

                      <input
                        name="last_name"
                        value={profile.last_name}
                        onChange={handleProfileChange}
                        maxLength={150}
                      />
                    </label>

                    <label>
                      Email address

                      <input
                        type="email"
                        value={profile.email}
                        readOnly
                        disabled
                      />
                    </label>

                    <label>
                      Phone number

                      <input
                        name="phone_number"
                        value={profile.phone_number}
                        onChange={handleProfileChange}
                        maxLength={20}
                      />
                    </label>
                  </div>

                  <div className="profile-account-meta">
                    <span>
                      Account created:{" "}
                      {profile.date_joined
                        ? new Date(
                            profile.date_joined
                          ).toLocaleDateString("en-IN")
                        : "Unavailable"}
                    </span>
                  </div>

                  <button
                    className="profile-primary-button"
                    type="submit"
                    disabled={saving}
                  >
                    <Save size={16} />

                    {saving
                      ? "Saving..."
                      : "Save changes"}
                  </button>
                </form>
              </section>

              {/* Password management */}
              <section className="profile-card password-card">
                <div className="profile-section-heading">
                  <div className="profile-section-icon">
                    <LockKeyhole size={21} />
                  </div>

                  <div>
                    <h2>Password management</h2>

                    <p>
                      Update your password to keep your
                      account secure.
                    </p>
                  </div>
                </div>

                <form
                  className="password-form"
                  onSubmit={handleChangePassword}
                >
                  <div className="password-fields-grid">
                    {/* Current password */}
                    <label>
                      Current password

                      <div className="password-input-wrapper">
                        <input
                          type={
                            showPasswords.old
                              ? "text"
                              : "password"
                          }
                          name="old_password"
                          value={passwordData.old_password}
                          onChange={handlePasswordChange}
                          autoComplete="current-password"
                          placeholder="Enter current password"
                          required
                        />

                        <button
                          type="button"
                          className="password-visibility-button"
                          onClick={() =>
                            togglePasswordVisibility("old")
                          }
                          aria-label={
                            showPasswords.old
                              ? "Hide current password"
                              : "Show current password"
                          }
                        >
                          {showPasswords.old ? (
                            <EyeOff size={18} />
                          ) : (
                            <Eye size={18} />
                          )}
                        </button>
                      </div>
                    </label>

                    {/* New password */}
                    <label>
                      New password

                      <div className="password-input-wrapper">
                        <input
                          type={
                            showPasswords.new
                              ? "text"
                              : "password"
                          }
                          name="new_password"
                          value={passwordData.new_password}
                          onChange={handlePasswordChange}
                          autoComplete="new-password"
                          placeholder="Enter new password"
                          required
                        />

                        <button
                          type="button"
                          className="password-visibility-button"
                          onClick={() =>
                            togglePasswordVisibility("new")
                          }
                          aria-label={
                            showPasswords.new
                              ? "Hide new password"
                              : "Show new password"
                          }
                        >
                          {showPasswords.new ? (
                            <EyeOff size={18} />
                          ) : (
                            <Eye size={18} />
                          )}
                        </button>
                      </div>
                    </label>

                    {/* Confirm password */}
                    <label className="password-confirm-field">
                      Confirm new password

                      <div className="password-input-wrapper">
                        <input
                          type={
                            showPasswords.confirm
                              ? "text"
                              : "password"
                          }
                          name="confirm_password"
                          value={passwordData.confirm_password}
                          onChange={handlePasswordChange}
                          autoComplete="new-password"
                          placeholder="Confirm new password"
                          required
                        />

                        <button
                          type="button"
                          className="password-visibility-button"
                          onClick={() =>
                            togglePasswordVisibility("confirm")
                          }
                          aria-label={
                            showPasswords.confirm
                              ? "Hide confirmation password"
                              : "Show confirmation password"
                          }
                        >
                          {showPasswords.confirm ? (
                            <EyeOff size={18} />
                          ) : (
                            <Eye size={18} />
                          )}
                        </button>
                      </div>
                    </label>
                  </div>

                  <p className="password-help-text">
                    Your new password must satisfy the
                    password validation rules configured
                    by the server.
                  </p>

                  <button
                    className="profile-primary-button"
                    type="submit"
                    disabled={changingPassword}
                  >
                    <LockKeyhole size={16} />

                    {changingPassword
                      ? "Changing password..."
                      : "Change password"}
                  </button>
                </form>
              </section>

              {/* Resume management */}
              <section className="profile-card">
                <div className="resume-heading-row">
                  <div className="profile-section-heading">
                    <div className="profile-section-icon">
                      <FileText size={21} />
                    </div>

                    <div>
                      <h2>My resumes</h2>

                      <p>
                        Upload and manage your job
                        application resumes.
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="profile-primary-button"
                    onClick={() =>
                      fileInputRef.current?.click()
                    }
                    disabled={uploading}
                  >
                    <Upload size={16} />

                    {uploading
                      ? "Uploading..."
                      : "Upload resume"}
                  </button>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx"
                  hidden
                  onChange={handleUpload}
                />

                <p className="resume-upload-hint">
                  PDF, DOC or DOCX · Maximum file size: 5 MB
                </p>

                {resumes.length === 0 ? (
                  <div className="resume-empty-state">
                    <FileText size={34} />

                    <strong>No resumes uploaded</strong>

                    <span>
                      Upload your first resume to get started.
                    </span>
                  </div>
                ) : (
                  <div className="resume-list">
                    {resumes.map((resume) => (
                      <article
                        className="resume-item"
                        key={resume.id}
                      >
                        <div className="resume-item-icon">
                          <FileText size={22} />
                        </div>

                        <div className="resume-item-details">
                          <div className="resume-title-row">
                            <strong>{resume.title}</strong>

                            {resume.is_default && (
                              <span className="resume-default-badge">
                                <Star size={13} />
                                Default
                              </span>
                            )}
                          </div>

                          <span>
                            Uploaded{" "}
                            {resume.uploaded_at
                              ? new Date(
                                  resume.uploaded_at
                                ).toLocaleDateString("en-IN")
                              : "date unavailable"}
                          </span>
                        </div>

                        <div className="resume-item-actions">
                          {!resume.is_default && (
                            <button
                              type="button"
                              title="Set as default"
                              aria-label={`Set ${resume.title} as default`}
                              onClick={() =>
                                handleSetDefault(resume.id)
                              }
                              disabled={actionId === resume.id}
                            >
                              <Star size={17} />
                            </button>
                          )}

                          <button
                            type="button"
                            title="Download resume"
                            aria-label={`Download ${resume.title}`}
                            onClick={() =>
                              handleDownload(resume)
                            }
                            disabled={actionId === resume.id}
                          >
                            <Download size={17} />
                          </button>

                          <button
                            type="button"
                            className="resume-delete-button"
                            title="Delete resume"
                            aria-label={`Delete ${resume.title}`}
                            onClick={() =>
                              handleDelete(resume)
                            }
                            disabled={actionId === resume.id}
                          >
                            <Trash2 size={17} />
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
