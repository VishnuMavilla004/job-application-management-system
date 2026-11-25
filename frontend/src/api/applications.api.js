
import api from "./axios";

const BASE_URL = "applications/";

export const applicationsAPI = {
  getAll(params = {}) {
    return api.get(BASE_URL, { params });
  },

  getById(id) {
    return api.get(`${BASE_URL}${id}/`);
  },

  create(data) {
    return api.post(BASE_URL, data);
  },

  update(id, data) {
    return api.patch(`${BASE_URL}${id}/`, data);
  },

  delete(id) {
    return api.delete(`${BASE_URL}${id}/`);
  },
};
