import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:9010',
  timeout: 30000,
});

export const matchingApi = {
  submit(requirement, topN = 5) {
    return api.post('/api/v1/matching/', { requirement, top_n: topN });
  },
  getResult(taskId) {
    return api.get(`/api/v1/matching/${taskId}`);
  },
  getHistory(skip = 0, limit = 20) {
    return api.get('/api/v1/matching/history/list', { params: { skip, limit } });
  },
};

export const knowledgeApi = {
  createCompany(data) {
    return api.post('/api/v1/knowledge/companies', data);
  },
  search(query) {
    return api.post('/api/v1/knowledge/search', { query });
  },
};

export const gatewayApi = {
  getModels() {
    return api.get('/api/v1/gateway/models');
  },
  getStats() {
    return api.get('/api/v1/gateway/stats');
  },
};
