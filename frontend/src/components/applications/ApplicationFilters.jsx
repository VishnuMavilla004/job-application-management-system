
import { useEffect, useState } from "react";

const STATUS_OPTIONS = [
  ["applied", "Applied"],
  ["assessment", "Assessment"],
  ["interview", "Interview"],
  ["offer", "Offer"],
  ["rejected", "Rejected"],
  ["withdrawn", "Withdrawn"],
];

const EMPLOYMENT_OPTIONS = [
  ["full_time", "Full-time"],
  ["part_time", "Part-time"],
  ["contract", "Contract"],
  ["internship", "Internship"],
  ["freelance", "Freelance"],
];

const WORK_MODE_OPTIONS = [
  ["onsite", "On-site"],
  ["remote", "Remote"],
  ["hybrid", "Hybrid"],
];

const EMPTY_FILTERS = {
  search: "",
  status: "",
  company: "",
  employment_type: "",
  work_mode: "",
  location: "",
  applied_after: "",
  applied_before: "",
  deadline_after: "",
  deadline_before: "",
  minimum_salary: "",
  maximum_salary: "",
};

export default function ApplicationFilters({
  companies = [],
  initialFilters = EMPTY_FILTERS,
  onApply,
  onReset,
  loading = false,
}) {
  const [filters, setFilters] = useState({
    ...EMPTY_FILTERS,
    ...initialFilters,
  });

  function updateFilter(event) {
    const { name, value } = event.target;
    setFilters((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    onApply(filters);
  }

  function handleReset() {
    setFilters(EMPTY_FILTERS);
    onReset();
  }

  return (
    <form className="application-filters" onSubmit={handleSubmit}>
      <div className="filter-search-row">
        <input
          type="search"
          name="search"
          value={filters.search}
          onChange={updateFilter}
          placeholder="Search job title, company, description, location..."
          aria-label="Search applications"
        />

        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Apply Filters"}
        </button>

        <button
          type="button"
          className="filter-reset-button"
          onClick={handleReset}
          disabled={loading}
        >
          Reset
        </button>
      </div>

      <div className="filter-grid">
        <label>
          Status
          <select name="status" value={filters.status} onChange={updateFilter}>
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>

        <label>
          Company
          <select name="company" value={filters.company} onChange={updateFilter}>
            <option value="">All companies</option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Employment type
          <select
            name="employment_type"
            value={filters.employment_type}
            onChange={updateFilter}
          >
            <option value="">All types</option>
            {EMPLOYMENT_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>

        <label>
          Work mode
          <select name="work_mode" value={filters.work_mode} onChange={updateFilter}>
            <option value="">All work modes</option>
            {WORK_MODE_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>

        <label>
          Location
          <input
            name="location"
            value={filters.location}
            onChange={updateFilter}
            placeholder="e.g. Bengaluru"
          />
        </label>

        <label>
          Applied after
          <input
            type="date"
            name="applied_after"
            value={filters.applied_after}
            onChange={updateFilter}
          />
        </label>

        <label>
          Applied before
          <input
            type="date"
            name="applied_before"
            value={filters.applied_before}
            onChange={updateFilter}
          />
        </label>

        <label>
          Deadline after
          <input
            type="date"
            name="deadline_after"
            value={filters.deadline_after}
            onChange={updateFilter}
          />
        </label>

        <label>
          Deadline before
          <input
            type="date"
            name="deadline_before"
            value={filters.deadline_before}
            onChange={updateFilter}
          />
        </label>

        <label>
          Minimum salary
          <input
            type="number"
            min="0"
            name="minimum_salary"
            value={filters.minimum_salary}
            onChange={updateFilter}
            placeholder="Minimum"
          />
        </label>

        <label>
          Maximum salary
          <input
            type="number"
            min="0"
            name="maximum_salary"
            value={filters.maximum_salary}
            onChange={updateFilter}
            placeholder="Maximum"
          />
        </label>
      </div>
    </form>
  );
}
