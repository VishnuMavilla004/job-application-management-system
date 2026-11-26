
import api from "./axios";
import { ENDPOINTS } from "./endpoints";

export const resumesAPI = {
  getAll() {
    return api.get(ENDPOINTS.resumes);
  },

  getById(id) {
    return api.get(ENDPOINTS.resumeDetail(id));
  },

  upload(formData) {
    return api.post(ENDPOINTS.resumes, formData);
  },

  update(id, formData) {
    return api.patch(
      ENDPOINTS.resumeDetail(id),
      formData
    );
  },

  setDefault(id) {
    return api.post(ENDPOINTS.resumeDefault(id));
  },

  delete(id) {
    return api.delete(ENDPOINTS.resumeDetail(id));
  },

  download(id) {
    return api.get(ENDPOINTS.resumeDownload(id), {
      responseType: "blob",
    });
  },
};

export default resumesAPI;
