import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  timeout: 30000, // 30 second timeout
});

// Flag to prevent multiple redirects
let isRedirecting = false;

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle 401 errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // If we get a 401 error, the token is likely expired
    if (error.response?.status === 401 && !isRedirecting) {
      console.log('Received 401 error, clearing auth state');
      
      // Set flag to prevent multiple simultaneous redirects
      isRedirecting = true;
      
      // Clear auth state
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('profile_setup_completed');
      
      // Only redirect to login if we're not already on a public page
      const currentPath = window.location.pathname;
      const publicPaths = ['/', '/welcome', '/careers', '/login', '/signup'];
      const isPublicPath = publicPaths.some(path => currentPath.startsWith(path));
      
      if (!isPublicPath) {
        // Small delay to prevent multiple redirects
        setTimeout(() => {
          window.location.href = '/login';
        }, 100);
      } else {
        // Reset flag if we're on a public page
        setTimeout(() => {
          isRedirecting = false;
        }, 1000);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
