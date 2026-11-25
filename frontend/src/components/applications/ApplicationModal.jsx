
import { X } from "lucide-react";

export default function ApplicationModal({
  title,
  children,
  onClose,
  size = "medium",
}) {
  return (
    <div
      className="application-modal-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        className={`application-modal modal-${size}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <header className="application-modal-header">
          <h2>{title}</h2>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </header>

        <div className="application-modal-body">
          {children}
        </div>
      </section>
    </div>
  );
}
