
import { AlertTriangle } from "lucide-react";

export default function DeleteConfirmation({
  application,
  onConfirm,
  onCancel,
  deleting,
}) {
  return (
    <div className="delete-confirmation">
      <div className="delete-warning-icon">
        <AlertTriangle size={25} />
      </div>

      <h3>Delete this application?</h3>

      <p>
        Are you sure you want to delete{" "}
        <strong>{application?.job_title}</strong> at{" "}
        <strong>
          {application?.company_name ||
            application?.company?.name ||
            "this company"}
        </strong>
        ? This action cannot be undone.
      </p>

      <div className="application-form-actions">
        <button
          type="button"
          className="secondary-button"
          onClick={onCancel}
          disabled={deleting}
        >
          Cancel
        </button>

        <button
          type="button"
          className="danger-button"
          onClick={onConfirm}
          disabled={deleting}
        >
          {deleting ? "Deleting..." : "Delete application"}
        </button>
      </div>
    </div>
  );
}
