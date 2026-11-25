
import {
  formatDate,
  humanize,
} from "../../utils/dashboardFormatters";

export default function ApplicationDetails({ application }) {
  const company =
    application.company_name ||
    application.company?.name ||
    "—";

  const fields = [
    ["Company", company],
    ["Job title", application.job_title],
    ["Location", application.location],
    ["Employment type", humanize(application.employment_type)],
    ["Work mode", humanize(application.work_mode)],
    ["Status", humanize(application.status)],
    ["Minimum salary", application.salary_min ?? "—"],
    ["Maximum salary", application.salary_max ?? "—"],
    ["Applied date", formatDate(application.applied_date)],
    ["Deadline", formatDate(application.deadline)],
    ["Contact name", application.contact_name || "—"],
    ["Contact email", application.contact_email || "—"],
  ];

  return (
    <div className="application-details">
      <div className="details-grid">
        {fields.map(([label, value]) => (
          <div className="details-item" key={label}>
            <span>{label}</span>
            <strong>{value || "—"}</strong>
          </div>
        ))}
      </div>

      {application.job_url && (
        <div className="details-description">
          <span>Job posting</span>
          <a
            href={application.job_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open job posting
          </a>
        </div>
      )}

      <div className="details-description">
        <span>Job description / notes</span>
        <p>{application.description || "No description added."}</p>
      </div>
    </div>
  );
}
