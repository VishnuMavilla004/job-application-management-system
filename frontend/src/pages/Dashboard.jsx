import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Activity,
  BriefcaseBusiness,
  CalendarCheck,
  Gift,
  RefreshCw,
  XCircle,
  Ban,
} from "lucide-react";

import { dashboardAPI } from "../api/dashboard.api";

import Sidebar from "../components/dashboard/Sidebar";
import DashboardHeader from "../components/dashboard/DashboardHeader";
import StatCard from "../components/dashboard/StatCard";
import RecentApplications from "../components/dashboard/RecentApplications";

import {
  ApplicationTrendChart,
  EmploymentDistributionChart,
  StatusDistributionChart,
} from "../components/dashboard/DashboardCharts";

import {
  extractList,
  formatNumber,
  formatPercentage,
  unwrapResponse,
} from "../utils/dashboardFormatters";

import "../styles/dashboard.css";

export default function Dashboard() {
  const navigate = useNavigate();

  const [summary, setSummary] = useState({});
  const [trends, setTrends] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);
  const [employmentDistribution, setEmploymentDistribution] = useState([]);
  const [applications, setApplications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const results = await Promise.allSettled([
        dashboardAPI.getSummary(),
        dashboardAPI.getTrends(),
        dashboardAPI.getDistribution(),
        dashboardAPI.getRecentApplications(),
        dashboardAPI.getNotifications(),
      ]);

      const [
        summaryResult,
        trendsResult,
        distributionResult,
        applicationsResult,
        notificationsResult,
      ] = results;

      if (summaryResult.status === "rejected") {
        throw summaryResult.reason;
      }

      const summaryData = unwrapResponse(summaryResult.value);
      setSummary(summaryData || {});

      if (trendsResult.status === "fulfilled") {
        const data = unwrapResponse(trendsResult.value);

        setTrends(
          extractList(data?.trends ?? data?.monthly_trends ?? data)
        );
      }

      if (distributionResult.status === "fulfilled") {
        const data = unwrapResponse(distributionResult.value);

        setStatusDistribution(
          extractList(
            data?.status_distribution ?? data?.statuses ?? data
          )
        );

        setEmploymentDistribution(
          extractList(
            data?.employment_type_distribution ??
            data?.employment_types ??
            []
          )
        );
      }

      if (applicationsResult.status === "fulfilled") {
        const data = unwrapResponse(applicationsResult.value);
        setApplications(extractList(data));
      }

      if (notificationsResult.status === "fulfilled") {
        const responseBody = notificationsResult.value?.data ?? {};
        const notificationData = unwrapResponse(
          notificationsResult.value
        );

        setUnreadCount(
          Number(
            responseBody?.unread_count ??
            notificationData?.unread_count ??
            summaryData?.unread_notification_count ??
            summaryData?.unread_notifications ??
            0
          )
        );
      } else {
        setUnreadCount(
          Number(
            summaryData?.unread_notification_count ??
            summaryData?.unread_notifications ??
            0
          )
        );
      }
    } catch (err) {
      setError(
        err.response?.data?.message ||
        err.response?.data?.detail ||
        "Unable to load dashboard data. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const totalApplications = summary.total_applications ?? 0;
  const activeApplications = summary.active_applications ?? 0;
  const interviews = summary.interviews ?? 0;
  const offers = summary.offers ?? 0;
  const rejections = summary.rejections ?? 0;
  const withdrawals = summary.withdrawals ?? 0;

  const openApplications = (filter = "") => {
  navigate(filter ? `/applications?${filter}` : "/applications");
};

  return (
    <div className="dashboard-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="dashboard-main">
        <DashboardHeader
          onMenuClick={() => setSidebarOpen(true)}
          unreadCount={unreadCount}
          onUnreadCountChange={setUnreadCount}
        />

        <div className="dashboard-content">
          <div className="dashboard-title-row">
            <div>
              <p className="dashboard-eyebrow">OVERVIEW</p>
              <h1>Dashboard</h1>

              <p className="dashboard-subtitle">
                Track your job search progress and opportunities.
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={loadDashboard}
              disabled={loading}
            >
              <RefreshCw
                size={16}
                className={loading ? "refresh-spinning" : ""}
              />
              Refresh
            </button>
          </div>

          {error && (
            <div className="dashboard-error">
              <span>{error}</span>
              <button onClick={loadDashboard}>Retry</button>
            </div>
          )}

          {loading ? (
            <div className="dashboard-loading">
              <div className="spinner" />
              <p>Loading your dashboard...</p>
            </div>
          ) : (
            <>
              <section className="stats-grid">
                <StatCard
                  title="Total Applications"
                  value={formatNumber(totalApplications)}
                  description="All submitted applications"
                  icon={BriefcaseBusiness}
                  color="purple"
                  onClick={() => openApplications()}
                />

                <StatCard
                  title="Active Applications"
                  value={formatNumber(activeApplications)}
                  description="Applied, assessment and interview"
                  icon={Activity}
                  color="blue"
                  onClick={() => openApplications("preset=active")}
                />

                <StatCard
                  title="Interviews"
                  value={formatNumber(interviews)}
                  description="Interview-stage applications"
                  icon={CalendarCheck}
                  color="orange"
                  onClick={() => openApplications("status=interview")}
                />

                <StatCard
                  title="Offers"
                  value={formatNumber(offers)}
                  description="Offers received"
                  icon={Gift}
                  color="green"
                  onClick={() => openApplications("status=offer")}
                />

                <StatCard
                  title="Rejections"
                  value={formatNumber(rejections)}
                  description="Applications rejected"
                  icon={XCircle}
                  color="red"
                  onClick={() => openApplications("status=rejected")}
                />

                <StatCard
                  title="Withdrawals"
                  value={formatNumber(withdrawals)}
                  description="Applications withdrawn"
                  icon={Ban}
                  color="gray"
                  onClick={() => openApplications("status=withdrawn")}
                />
              </section>

              <section className="conversion-grid">
                <div className="conversion-card">
                  <span>Interview conversion rate</span>
                  <strong>
                    {formatPercentage(
                      summary.interview_conversion_rate
                    )}
                  </strong>
                </div>

                <div className="conversion-card">
                  <span>Offer conversion rate</span>
                  <strong>
                    {formatPercentage(summary.offer_conversion_rate)}
                  </strong>
                </div>
              </section>

              <section className="charts-grid">
                <ApplicationTrendChart data={trends} />
                <StatusDistributionChart data={statusDistribution} />
              </section>

              <section className="charts-grid charts-grid-bottom">
                <EmploymentDistributionChart
                  data={employmentDistribution}
                />

                <div className="dashboard-insight-card">
                  <h3>Job search overview</h3>

                  <p>
                    Keep your application statuses updated to maintain
                    accurate analytics.
                  </p>

                  <div className="insight-row">
                    <span>Active applications</span>
                    <strong>{formatNumber(activeApplications)}</strong>
                  </div>

                  <div className="insight-row">
                    <span>Offers received</span>
                    <strong>{formatNumber(offers)}</strong>
                  </div>

                  <div className="insight-row">
                    <span>Withdrawn applications</span>
                    <strong>{formatNumber(withdrawals)}</strong>
                  </div>

                  <div className="insight-row">
                    <span>Unread notifications</span>
                    <strong>{formatNumber(unreadCount)}</strong>
                  </div>
                </div>
              </section>

              <RecentApplications applications={applications} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}