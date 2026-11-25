
import api from "./axios";

export const companiesAPI = {
  getAll(params = {}) {
    return api.get("companies/", { params });
  },
};
