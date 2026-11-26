
export default function ApplicationPagination({
  count = 0,
  page = 1,
  pageSize = 10,
  onPageChange,
  onPageSizeChange,
  loading = false,
}) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  const start = count === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, count);

  return (
    <div className="application-pagination">
      <div className="pagination-summary">
        Showing {start}–{end} of {count} applications
      </div>

      <div className="pagination-controls">
        <label>
          Rows per page
          <select
            value={pageSize}
            disabled={loading}
            onChange={(event) => onPageSizeChange(Number(event.target.value))}
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>

        <button
          type="button"
          disabled={loading || page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </button>

        <span className="pagination-page">
          Page {page} of {totalPages}
        </span>

        <button
          type="button"
          disabled={loading || page >= totalPages || count === 0}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
