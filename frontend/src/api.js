import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// API functions
export const getHealth = () => api.get("/healthz");
export const getMetrics = () => api.get("/metrics");
export const getRuns = (limit = 50) => api.get(`/agent/runs?limit=${limit}`);
export const getRunTrace = (runId) => api.get(`/agent/runs/${runId}/trace`);
export const getContext = (sha) => api.get(`/context?commit_sha=${sha}`);

// Additional API functions for context management
export const addContext = (texts, commitSha = null) => {
  const data = { texts };
  if (commitSha) data.commit_sha = commitSha;
  return api.post("/context/add", data);
};

export const getContextStats = () => api.get("/context/stats");

export const queryContext = (queryText, topK = 5) => 
  api.get(`/context/query?query_text=${encodeURIComponent(queryText)}&top_k=${topK}`);

export default api;
