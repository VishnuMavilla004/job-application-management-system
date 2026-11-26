
import { useCallback, useEffect, useRef, useState } from "react";
import {
  FileText,
  Upload,
  Download,
  Trash2,
  Star,
  UserRound,
  Save,
  RefreshCw,
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

function unwrap(response) {
  return response?.data?.data ?? response?.data ?? {};
}

function getError(error, fallback) {
  const body = error?.response?.data;

  if (typeof body?.message === "string") return body.message;
  if (typeof body?.detail === "string") return body.detail;

  if (body?.errors && typeof body.errors === "object") {
    return Object.values(body.errors).flat().join(" ");
  }

  if (body && typeof body === "object") {
    return Object.entries(body)
      .map(([key, value]) => {
        const message = Array.isArray(value)
          ? value.join(" ")
          : String(value);

        return `${key}: ${message}`;
      })
      .join(" ");
  }

  return fallback;
}

function getResumeList(response) {
  const payload = unwrap(response);

  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;

  return [];
}

export default function Profile() {
  const { refreshProfile } = useAuth();

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

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [actionId, setActionId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadPage = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [profileResult, resumeResult, notificationResult] =
        await Promise.allSettled([
          authAPI.getProfile(),
          resumesAPI.getAll(),
          notificationsAPI.getAll({ page: 1, page_size: 1 }),
        ]);

      if (profileResult.status === "rejected") {
        throw profileResult.reason;
      }

      const profileData = profileResult.value;

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
        const body = notificationResult.value?.data ?? {};
        const payload = unwrap(notificationResult.value);

        setUnreadCount(
          Number(
            body.unread_count ??
            payload.unread_count ??
            0
          )
        );
      }
    } catch (err) {
      setError(getError(err, "Unable to load your profile."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPage();
  }, [loadPage]);

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
      setError(getError(err, "Unable to update your profile."));
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setError("");
    setSuccess("");

    const extension = file.name
      .slice(file.name.lastIndexOf("."))
      .toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setError("Only PDF, DOC and DOCX files are supported.");
      event.target.value = "";
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError("Resume file size cannot exceed 5 MB.");
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

      setSuccess("Resume uploaded successfully.");

      const response = await resumesAPI.getAll();
      setResumes(getResumeList(response));
    } catch (err) {
      setError(getError(err, "Unable to upload your resume."));
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

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
    console.error("SET DEFAULT RESUME ERROR:", err);
    console.error("HTTP STATUS:", err?.response?.status);
    console.error("RESPONSE DATA:", err?.response?.data);
    console.error("REQUEST URL:", err?.config?.url);
    console.error("REQUEST METHOD:", err?.config?.method);

    setError(getError(err, "Unable to change default resume."));
  } finally {
    setActionId(null);
  }
};

  const handleDownload = async (resume) => {
    setActionId(resume.id);
    setError("");

    try {
      const response = await resumesAPI.download(resume.id);

      const blobUrl = window.URL.createObjectURL(
        new Blob([response.data])
      );

      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = resume.file?.split("/").pop() ||
        `${resume.title}.pdf`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setError(getError(err, "Unable to download resume."));
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
          <div className="dashboard-title-row">
            <div>
              <p className="dashboard-eyebrow">ACCOUNT</p>
              <h1>Profile & Resumes</h1>
              <p className="dashboard-subtitle">
                Manage your personal information and resume documents.
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={loadPage}
              disabled={loading}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          {error && (
            <div className="profile-alert profile-alert-error">
              {error}
            </div>
          )}

          {success && (
            <div className="profile-alert profile-alert-success">
              {success}
            </div>
          )}

          {loading ? (
            <div className="profile-loading">
              Loading profile...
            </div>
          ) : (
            <>
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
                        ? new Date(profile.date_joined).toLocaleDateString(
                            "en-IN"
                          )
                        : "Unavailable"}
                    </span>
                  </div>

                  <button
                    className="profile-primary-button"
                    type="submit"
                    disabled={saving}
                  >
                    <Save size={16} />
                    {saving ? "Saving..." : "Save changes"}
                  </button>
                </form>
              </section>

              <section className="profile-card">
                <div className="resume-heading-row">
                  <div className="profile-section-heading">
                    <div className="profile-section-icon">
                      <FileText size={21} />
                    </div>

                    <div>
                      <h2>My resumes</h2>
                      <p>
                        Upload and manage your job application resumes.
                      </p>
                    </div>
                  </div>

                  <button
                    className="profile-primary-button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                  >
                    <Upload size={16} />
                    {uploading ? "Uploading..." : "Upload resume"}
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
                            {new Date(
                              resume.uploaded_at
                            ).toLocaleDateString("en-IN")}
                          </span>
                        </div>

                        <div className="resume-item-actions">
                          {!resume.is_default && (
                            <button
                              title="Set as default"
                              onClick={() => handleSetDefault(resume.id)}
                              disabled={actionId === resume.id}
                            >
                              <Star size={17} />
                            </button>
                          )}

                          <button
                            title="Download resume"
                            onClick={() => handleDownload(resume)}
                            disabled={actionId === resume.id}
                          >
                            <Download size={17} />
                          </button>

                          <button
                            className="resume-delete-button"
                            title="Delete resume"
                            onClick={() => handleDelete(resume)}
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
