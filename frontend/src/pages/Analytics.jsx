import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ResponsiveContainer,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import { analyticsAPI } from "../api/analytics.api";
import "../styles/analytics.css";

const today = new Date();

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function getDefaultStartDate() {
  const start = new Date();
  start.setDate(start.getDate() - 29);
  return formatDate(start);
}

const STATUS_COLORS = {
  applied: "#64748b",
  assessment: "#8b5cf6",
  interview: "#0ea5e9",
  offer: "#16a34a",
  rejected: "#ef4444",
  withdrawn: "#f59e0b",
};

function MetricCard({ label, value, suffix = "" }) {
  return (
    <article className="analytics-metric-card">
      <span>{label}</span>
      <strong>
        {value ?? "—"}
        {suffix}
      </strong>
    </article>
  );
}

function ChartCard({ title, children }) {
  return (
    <section className="analytics-chart-card">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function EmptyChart() {
  return (
    <div className="analytics-empty">
      No application data available for this date range.
    </div>
  );
}

export default function Analytics() {
  const [startDate, setStartDate] = useState(getDefaultStartDate);
  const [endDate, setEndDate] = useState(formatDate(today));
  const [granularity, setGranularity] = useState("weekly");

  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState("");

  const loadAnalytics = useCallback(async () => {
    if (startDate > endDate) {
      setError("Start date cannot be after end date.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await analyticsAPI.getAnalytics({
        start_date: startDate,
        end_date: endDate,
        granularity,
      });

      setAnalytics(response.data?.data ?? null);
    } catch (requestError) {
      setError(
        requestError.response?.data?.message ||
          "Unable to load analytics."
      );
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, granularity]);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  const handleExport = async () => {
    setExporting(true);
    setError("");

    try {
      const response = await analyticsAPI.exportCSV({
        start_date: startDate,
        end_date: endDate,
        granularity,
      });

      const blob = new Blob([response.data], {
        type: "text/csv;charset=utf-8;",
      });

      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");

      anchor.href = url;
      anchor.download = "job_application_report.csv";

      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      window.URL.revokeObjectURL(url);
    } catch (requestError) {
      setError(
        requestError.response?.data?.message ||
          "CSV export failed."
      );
    } finally {
      setExporting(false);
    }
  };

  const overview = analytics?.overview;
  const funnel = analytics?.funnel ?? [];
  const trends = analytics?.trends ?? [];
  const companies = analytics?.company_analytics ?? [];
  const statuses = analytics?.status_distribution ?? [];
  const employment = analytics?.employment_type_distribution ?? [];

  return (
    <main className="analytics-page">
      <header className="analytics-header">
        <div>
          <Link to="/dashboard" className="analytics-back-link">
            ← Back to Dashboard
          </Link>
          <h1>Advanced Analytics</h1>
          <p>
            Analyze application progress, conversion rates and
            application trends.
          </p>
        </div>

        <button
          type="button"
          className="analytics-export-button"
          onClick={handleExport}
          disabled={loading || exporting}
        >
          {exporting ? "Exporting..." : "Export CSV"}
        </button>
      </header>

      <section className="analytics-filters">
        <label>
          Start date
          <input
            type="date"
            value={startDate}
            max={endDate}
            onChange={(event) => setStartDate(event.target.value)}
          />
        </label>

        <label>
          End date
          <input
            type="date"
            value={endDate}
            min={startDate}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </label>

        <label>
          Trend interval
          <select
            value={granularity}
            onChange={(event) => setGranularity(event.target.value)}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </label>

        <button
          type="button"
          onClick={loadAnalytics}
          disabled={loading}
        >
          {loading ? "Loading..." : "Apply filters"}
        </button>
      </section>

      {error && (
        <div className="analytics-error" role="alert">
          {error}
        </div>
      )}

      {loading && !analytics ? (
        <div className="analytics-loading">
          Loading analytics...
        </div>
      ) : (
        <>
          <section className="analytics-metrics-grid">
            <MetricCard
              label="Applications"
              value={overview?.total_applications ?? 0}
            />
            <MetricCard
              label="Interview rate"
              value={overview?.interview_rate ?? 0}
              suffix="%"
            />
            <MetricCard
              label="Offer rate"
              value={overview?.offer_rate ?? 0}
              suffix="%"
            />
            <MetricCard
              label="Rejection rate"
              value={overview?.rejection_rate ?? 0}
              suffix="%"
            />
            <MetricCard
              label="Average response time"
              value={overview?.average_response_days}
              suffix={
                overview?.average_response_days === null
                  ? ""
                  : " days"
              }
            />
          </section>

          <section className="analytics-charts-grid">
            <ChartCard title="Application Funnel">
              {funnel.length ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={funnel}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="stage"
                      tickFormatter={(value) =>
                        value.charAt(0).toUpperCase() + value.slice(1)
                      }
                    />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#6366f1" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}

              <div className="analytics-funnel-details">
                {funnel.map((stage) => (
                  <div key={stage.stage}>
                    <span>{stage.stage}</span>
                    <strong>
                      {stage.conversion_from_previous}%
                    </strong>
                    <small>conversion from previous stage</small>
                  </div>
                ))}
              </div>
            </ChartCard>

            <ChartCard title="Application Trends">
              {trends.length ? (
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="count"
                      name="Applications"
                      stroke="#6366f1"
                      strokeWidth={2}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </ChartCard>

            <ChartCard title="Current Status Distribution">
              {statuses.length ? (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={statuses}
                      dataKey="count"
                      nameKey="status"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      label
                    >
                      {statuses.map((item) => (
                        <Cell
                          key={item.status}
                          fill={
                            STATUS_COLORS[item.status] || "#94a3b8"
                          }
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </ChartCard>

            <ChartCard title="Employment Type">
              {employment.length ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={employment}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="employment_type" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar
                      dataKey="count"
                      name="Applications"
                      fill="#0ea5e9"
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </ChartCard>
          </section>

          <section className="analytics-table-card">
            <h2>Top Companies</h2>

            {companies.length ? (
              <div className="analytics-table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Applications</th>
                    </tr>
                  </thead>
                  <tbody>
                    {companies.map((company) => (
                      <tr key={company.company_id}>
                        <td>{company.company__name}</td>
                        <td>{company.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyChart />
            )}
          </section>
        </>
      )}
    </main>
  );
}