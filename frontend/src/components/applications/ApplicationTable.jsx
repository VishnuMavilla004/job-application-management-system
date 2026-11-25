
import { Eye, Pencil, Trash2 } from "lucide-react";
import {
  formatDate,
  humanize,
} from "../../utils/dashboardFormatters";

export default function ApplicationTable({
  applications,
  onView,
  onEdit,
  onDelete,
}) {
  if (!applications.length) {
    return (
      <div className="applications-empty">
        <div className="applications-empty-icon">
          <Eye size={26} />
        </div>
        <h3>No applications found</h3>
        <p>Create your first application to start tracking your job search.</p>
      </div>
    );
  }

  return (
    <div className="applications-table-wrapper">
      <table className="applications-table">
        <thead>
          <tr>
            <th>Job title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Applied date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {applications.map((application) => (
            <tr key={application.id}>
              <td className="application-job-title">
                {application.job_title}
              </td>

              <td>
                {application.company_name ||
                  application.company?.name ||
                  "—"}
              </td>

              <td>{application.location || "—"}</td>

              <td>{formatDate(application.applied_date)}</td>

              <td>
                <span
                  className={`status-pill status-${application.status}`}
                >
                  {humanize(application.status)}
                </span>
              </td>

              <td>
                <div className="application-actions">
                  <button
                    type="button"
                    title="View"
                    aria-label="View application"
                    onClick={() => onView(application)}
                  >
                    <Eye size={17} />
                  </button>

                  <button
                    type="button"
                    title="Edit"
                    aria-label="Edit application"
                    onClick={() => onEdit(application)}
                  >
                    <Pencil size={17} />
                  </button>

                  <button
                    type="button"
                    title="Delete"
                    aria-label="Delete application"
                    className="delete-action"
                    onClick={() => onDelete(application)}
                  >
                    <Trash2 size={17} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
