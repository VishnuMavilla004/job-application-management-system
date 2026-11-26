
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
} from "recharts";

import { humanize } from "../../utils/dashboardFormatters";

// Permanent status-to-colour mapping.
// Colours never change based on application counts or array positions.
const STATUS_CONFIG = {
  applied: {
    label: "Applied",
    color: "#4f46e5",
    order: 1,
  },
  assessment: {
    label: "Assessment",
    color: "#0d9488",
    order: 2,
  },
  interview: {
    label: "Interview",
    color: "#f59e0b",
    order: 3,
  },
  offer: {
  label: "Offer",
  color: "#F9A8D4",
  order: 4,
},
  rejected: {
  label: "Rejected",
  color: "#dc2626",
  order: 5,
},
  withdrawn: {
    label: "Withdrawn",
    color: "#8b5cf6",
    order: 6,
  },
};

const STATUS_KEYS = Object.keys(STATUS_CONFIG);

export function ApplicationTrendChart({ data = [] }) {
  const chartData = data.map((item) => ({
    month: item.month_label || item.month,
    applications: Number(
      item.count ?? item.application_count ?? 0
    ),
  }));

  return (
    <section className="chart-card">
      <div className="chart-heading">
        <div>
          <h3>Application activity</h3>
          <p>Applications submitted over the last six months</p>
        </div>
      </div>

      {chartData.length === 0 ? (
        <div className="chart-empty">
          No trend data available.
        </div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient
                  id="applicationGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#4f46e5"
                    stopOpacity={0.28}
                  />
                  <stop
                    offset="95%"
                    stopColor="#4f46e5"
                    stopOpacity={0.01}
                  />
                </linearGradient>
              </defs>

              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
              />

              <XAxis
                dataKey="month"
                tick={{ fontSize: 12 }}
              />

              <YAxis
                allowDecimals={false}
                tick={{ fontSize: 12 }}
              />

              <Tooltip />

              <Area
                type="monotone"
                dataKey="applications"
                stroke="#4f46e5"
                strokeWidth={3}
                fill="url(#applicationGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}

export function StatusDistributionChart({ data = [] }) {
  // Convert API results into a status-count lookup.
  const statusCounts = data.reduce((counts, item) => {
    const status = String(item.status ?? "")
      .trim()
      .toLowerCase();

    if (!STATUS_CONFIG[status]) {
      return counts;
    }

    counts[status] =
      (counts[status] || 0) +
      Number(item.count ?? item.application_count ?? 0);

    return counts;
  }, {});

  // Always retain all six statuses and their fixed colours.
  const chartData = STATUS_KEYS.map((status) => ({
    status,
    name: STATUS_CONFIG[status].label,
    value: statusCounts[status] ?? 0,
    color: STATUS_CONFIG[status].color,
  }));

  const pieData = chartData.filter(
    (item) => item.value > 0
  );

  const hasData = pieData.length > 0;

  return (
    <section className="chart-card">
      <div className="chart-heading">
        <div>
          <h3>Application status</h3>
          <p>Distribution across application stages</p>
        </div>
      </div>

      {!hasData ? (
        <div className="chart-empty">
          No application data available.
        </div>
      ) : (
        <>
          <div className="pie-chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={58}
                  outerRadius={90}
                  paddingAngle={3}
                >
                  {pieData.map((item) => (
                    <Cell
                      key={item.status}
                      fill={item.color}
                    />
                  ))}
                </Pie>

                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-legend">
            {chartData.map((item) => (
              <div
                className="legend-item"
                key={item.status}
              >
                <span
                  className="legend-dot"
                  style={{
                    backgroundColor: item.color,
                  }}
                />

                <span>{item.name}</span>

                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}

export function EmploymentDistributionChart({ data = [] }) {
  const chartData = data.map((item) => ({
    type: humanize(item.employment_type ?? item.type),
    count: Number(
      item.count ?? item.application_count ?? 0
    ),
  }));

  return (
    <section className="chart-card">
      <div className="chart-heading">
        <div>
          <h3>Employment types</h3>
          <p>Applications by employment category</p>
        </div>
      </div>

      {chartData.length === 0 ? (
        <div className="chart-empty">
          No employment data available.
        </div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
              />

              <XAxis
                dataKey="type"
                tick={{ fontSize: 11 }}
                interval={0}
              />

              <YAxis
                allowDecimals={false}
                tick={{ fontSize: 12 }}
              />

              <Tooltip />

              <Bar
                dataKey="count"
                fill="#0d9488"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
