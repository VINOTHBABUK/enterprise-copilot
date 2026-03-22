import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically add token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const login = (email, password) =>
  api.post('/auth/login', { email, password });

export const register = (email, name, password, role, departments) =>
  api.post('/auth/register', { email, name, password, role, departments });

export const getMe = () =>
  api.get('/users/me');

// Chat endpoint
export const sendMessage = (message, department = null) =>
  api.post('/chat', { message, department });

// Stats endpoint
export const getStats = () =>
  api.get('/stats');

export default api;