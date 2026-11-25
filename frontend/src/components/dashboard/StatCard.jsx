
export default function StatCard({
  title,
  value,
  description,
  icon: Icon,
  color,
}) {
  return (
    <article className="stat-card">
      <div className="stat-card-top">
        <span className="stat-title">{title}</span>
        <div className={`stat-icon ${color}`}>
          <Icon size={21} />
        </div>
      </div>

      <strong className="stat-value">{value}</strong>
      <span className="stat-description">{description}</span>
    </article>
  );
}
