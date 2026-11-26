
export default function StatCard({
  title,
  value,
  description,
  icon: Icon,
  color,
  onClick,
}) {
  return (
    <button
      type="button"
      className="stat-card stat-card-button"
      onClick={onClick}
      aria-label={`View ${title}: ${value}`}
    >
      <div className="stat-card-top">
        <span className="stat-title">{title}</span>

        <div className={`stat-icon ${color}`}>
          <Icon size={21} />
        </div>
      </div>

      <strong className="stat-value">{value}</strong>

      <span className="stat-description">
        {description}
      </span>
    </button>
  );
}
