
import { Link } from "react-router-dom";
import {
  formatDate,
  humanize,
} from "../../utils/dashboardFormatters";

export default function RecentApplications({ applications = [] }) {
  return (
    <section className="recent-card">
      <div className="recent-heading">
        <div>
          <h3>Recent applications</h3>
          <p>Your latest job application activity</p>
        </div>

        <Link to="/applications">View all</Link>
      </div>

      {applications.length === 0 ? (
        <div className="recent-empty">
          <h4>No applications yet</h4>
          <p>Your job applications will appear here.</p>
        </div>
      ) : (
        <div className="table-scroll">
          <table className="recent-table">
            <thead>
              <tr>
                <th>Job title</th>
                <th>Company</th>
                <th>Applied date</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {applications.map((application) => (
                <tr key={application.id}>
                  <td className="job-title-cell">
                    {application.job_title}
                  </td>
                  <td>
                    {application.company_name ||
                      application.company?.name ||
                      "—"}
                  </td>
                  <td>{formatDate(application.applied_date)}</td>
                  <td>
                    <span
                      className={`status-pill status-${application.status}`}
                    >
                      {humanize(application.status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
