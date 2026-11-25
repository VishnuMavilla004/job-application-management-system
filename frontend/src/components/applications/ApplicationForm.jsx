
import { useEffect, useState } from "react";

const INITIAL_FORM = {
  job_title: "",
  company: "",
  description: "",
  location: "",
  employment_type: "full_time",
  work_mode: "onsite",
  salary_min: "",
  salary_max: "",
  job_url: "",
  status: "applied",
  applied_date: new Date().toISOString().slice(0, 10),
  deadline: "",
  contact_name: "",
  contact_email: "",
};

const EMPLOYMENT_TYPES = [
  ["full_time", "Full Time"],
  ["part_time", "Part Time"],
  ["contract", "Contract"],
  ["internship", "Internship"],
  ["freelance", "Freelance"],
];

const WORK_MODES = [
  ["onsite", "On-site"],
  ["remote", "Remote"],
  ["hybrid", "Hybrid"],
];

const STATUSES = [
  ["applied", "Applied"],
  ["assessment", "Assessment"],
  ["interview", "Interview"],
  ["offer", "Offer"],
  ["rejected", "Rejected"],
  ["withdrawn", "Withdrawn"],
];

export default function ApplicationForm({
  initialData,
  companies = [],
  onSubmit,
  onCancel,
  submitting = false,
}) {
  const [form, setForm] = useState({ ...INITIAL_FORM });
  const [errors, setErrors] = useState({});

  // Initialize create/edit form.
  useEffect(() => {
    if (initialData) {
      setForm({
        ...INITIAL_FORM,
        job_title: initialData.job_title ?? "",
        company: String(
          initialData.company?.id ??
          initialData.company ??
          initialData.company_id ??
          ""
        ),
        description:
          initialData.job_description ??
          initialData.description ??
          "",
        location: initialData.location ?? "",
        employment_type:
          initialData.employment_type ?? "full_time",
        work_mode: initialData.work_mode ?? "onsite",
        salary_min: initialData.salary_min ?? "",
        salary_max: initialData.salary_max ?? "",
        job_url: initialData.job_url ?? "",
        status: initialData.status ?? "applied",
        applied_date: initialData.applied_date ?? "",
        deadline: initialData.deadline ?? "",
        contact_name:
          initialData.contact_person ??
          initialData.contact_name ??
          "",
        contact_email: initialData.contact_email ?? "",
      });
    } else {
      setForm({ ...INITIAL_FORM });
    }

    setErrors({});
  }, [initialData]);

  // Handle input changes.
  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setErrors((previous) => ({
      ...previous,
      [name]: "",
    }));
  };

  // Validate and submit.
  const handleSubmit = async (event) => {
    event.preventDefault();

    const nextErrors = {};

    if (!form.job_title.trim()) {
      nextErrors.job_title = "Job title is required.";
    }

    if (!form.company) {
      nextErrors.company = "Select a company.";
    }

    if (!form.applied_date) {
      nextErrors.applied_date = "Applied date is required.";
    }

    if (
      form.salary_min !== "" &&
      Number(form.salary_min) < 0
    ) {
      nextErrors.salary_min =
        "Salary cannot be negative.";
    }

    if (
      form.salary_max !== "" &&
      Number(form.salary_max) < 0
    ) {
      nextErrors.salary_max =
        "Salary cannot be negative.";
    }

    if (
      form.salary_min !== "" &&
      form.salary_max !== "" &&
      Number(form.salary_max) < Number(form.salary_min)
    ) {
      nextErrors.salary_max =
        "Maximum salary must be greater than or equal to minimum salary.";
    }

    if (
      form.deadline &&
      form.applied_date &&
      form.deadline < form.applied_date
    ) {
      nextErrors.deadline =
        "Deadline cannot be before the applied date.";
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    // Match Django JobApplicationSerializer field names.
    const payload = {
      job_title: form.job_title.trim(),
      company_id: Number(form.company),
      job_description: form.description,
      location: form.location,
      employment_type: form.employment_type,
      work_mode: form.work_mode,

      salary_min:
        form.salary_min === ""
          ? null
          : Number(form.salary_min),

      salary_max:
        form.salary_max === ""
          ? null
          : Number(form.salary_max),

      job_url: form.job_url,
      status: form.status,
      applied_date: form.applied_date,
      deadline: form.deadline || null,
      contact_person: form.contact_name,
      contact_email: form.contact_email,
    };

    try {
      await onSubmit(payload);
    } catch (error) {
      console.error(
        "Application submission failed:",
        error.response?.data ?? error
      );
    }
  };

  return (
    <form
      className="application-form"
      onSubmit={handleSubmit}
    >
      <div className="application-form-grid">

        {/* Job title */}
        <div className="application-field">
          <label htmlFor="job_title">
            Job title *
          </label>

          <input
            id="job_title"
            name="job_title"
            value={form.job_title}
            onChange={handleChange}
            placeholder="Python Backend Developer"
            required
          />

          {errors.job_title && (
            <small className="field-error">
              {errors.job_title}
            </small>
          )}
        </div>

        {/* Company */}
        <div className="application-field">
          <label htmlFor="company">
            Company *
          </label>

          <select
            id="company"
            name="company"
            value={form.company}
            onChange={handleChange}
            required
          >
            <option value="">
              Select company
            </option>

            {companies.map((company) => (
              <option
                key={company.id}
                value={company.id}
              >
                {company.name}
              </option>
            ))}
          </select>

          {errors.company && (
            <small className="field-error">
              {errors.company}
            </small>
          )}
        </div>

        {/* Location */}
        <div className="application-field">
          <label htmlFor="location">
            Location
          </label>

          <input
            id="location"
            name="location"
            value={form.location}
            onChange={handleChange}
            placeholder="Bengaluru, India"
          />
        </div>

        {/* Employment type */}
        <div className="application-field">
          <label htmlFor="employment_type">
            Employment type
          </label>

          <select
            id="employment_type"
            name="employment_type"
            value={form.employment_type}
            onChange={handleChange}
          >
            {EMPLOYMENT_TYPES.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Work mode */}
        <div className="application-field">
          <label htmlFor="work_mode">
            Work mode
          </label>

          <select
            id="work_mode"
            name="work_mode"
            value={form.work_mode}
            onChange={handleChange}
          >
            {WORK_MODES.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Application status */}
        <div className="application-field">
          <label htmlFor="status">
            Application status
          </label>

          <select
            id="status"
            name="status"
            value={form.status}
            onChange={handleChange}
          >
            {STATUSES.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Minimum salary */}
        <div className="application-field">
          <label htmlFor="salary_min">
            Minimum salary
          </label>

          <input
            id="salary_min"
            name="salary_min"
            type="number"
            min="0"
            step="0.01"
            value={form.salary_min}
            onChange={handleChange}
            placeholder="300000"
          />

          {errors.salary_min && (
            <small className="field-error">
              {errors.salary_min}
            </small>
          )}
        </div>

        {/* Maximum salary */}
        <div className="application-field">
          <label htmlFor="salary_max">
            Maximum salary
          </label>

          <input
            id="salary_max"
            name="salary_max"
            type="number"
            min="0"
            step="0.01"
            value={form.salary_max}
            onChange={handleChange}
            placeholder="600000"
          />

          {errors.salary_max && (
            <small className="field-error">
              {errors.salary_max}
            </small>
          )}
        </div>

        {/* Applied date */}
        <div className="application-field">
          <label htmlFor="applied_date">
            Applied date *
          </label>

          <input
            id="applied_date"
            name="applied_date"
            type="date"
            value={form.applied_date}
            onChange={handleChange}
            required
          />

          {errors.applied_date && (
            <small className="field-error">
              {errors.applied_date}
            </small>
          )}
        </div>

        {/* Deadline */}
        <div className="application-field">
          <label htmlFor="deadline">
            Application deadline
          </label>

          <input
            id="deadline"
            name="deadline"
            type="date"
            value={form.deadline}
            onChange={handleChange}
          />

          {errors.deadline && (
            <small className="field-error">
              {errors.deadline}
            </small>
          )}
        </div>

        {/* Job URL */}
        <div className="application-field full-width">
          <label htmlFor="job_url">
            Job posting URL
          </label>

          <input
            id="job_url"
            name="job_url"
            type="url"
            value={form.job_url}
            onChange={handleChange}
            placeholder="https://company.com/jobs/123"
          />
        </div>

        {/* Contact name */}
        <div className="application-field">
          <label htmlFor="contact_name">
            Contact name
          </label>

          <input
            id="contact_name"
            name="contact_name"
            value={form.contact_name}
            onChange={handleChange}
          />
        </div>

        {/* Contact email */}
        <div className="application-field">
          <label htmlFor="contact_email">
            Contact email
          </label>

          <input
            id="contact_email"
            name="contact_email"
            type="email"
            value={form.contact_email}
            onChange={handleChange}
          />
        </div>

        {/* Description */}
        <div className="application-field full-width">
          <label htmlFor="description">
            Job description / notes
          </label>

          <textarea
            id="description"
            name="description"
            rows="4"
            value={form.description}
            onChange={handleChange}
            placeholder="Add job responsibilities, requirements or notes..."
          />
        </div>

      </div>

      {/* Form actions */}
      <div className="application-form-actions">
        <button
          type="button"
          className="secondary-button"
          onClick={onCancel}
          disabled={submitting}
        >
          Cancel
        </button>

        <button
          type="submit"
          className="primary-button"
          disabled={submitting}
        >
          {submitting
            ? "Saving..."
            : initialData
              ? "Save changes"
              : "Create application"}
        </button>
      </div>
    </form>
  );
}
