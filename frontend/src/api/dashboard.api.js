
import api from "./axios";

export const dashboardAPI = {
  getSummary: () => api.get("dashboard/summary/"),
  getTrends: () => api.get("dashboard/trends/"),
  getDistribution: () => api.get("dashboard/distribution/"),

  getRecentApplications: () =>
    api.get("applications/", {
      params: { page: 1, page_size: 5, ordering: "-created_at" },
    }),

  getNotifications: () =>
    api.get("notifications/", {
      params: { page: 1, page_size: 5 },
    }),
};
