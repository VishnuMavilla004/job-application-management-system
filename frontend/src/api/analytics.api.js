import api from "./axios";

export const analyticsAPI = {
  getAnalytics: (params) =>
    api.get("dashboard/analytics/", { params }),

  exportCSV: (params) =>
    api.get("dashboard/analytics/export/", {
      params,
      responseType: "blob",
    }),
};