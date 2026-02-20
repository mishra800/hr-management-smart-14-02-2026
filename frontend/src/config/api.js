// Centralized API configuration
// Automatically detects environment and uses appropriate API URL

// Function to detect the best API URL
function getApiBaseUrl() {
  // 1. Use environment variable if set (highest priority)
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // 2. Auto-detect based on current hostname
  const hostname = window.location.hostname;
  
  // If accessing via IP address, use that IP for API
  if (hostname.match(/^\d+\.\d+\.\d+\.\d+$/)) {
    return `http://${hostname}:8000`;
  }
  
  // If on localhost, use localhost
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // For any other hostname (production domain, etc.), use same host with port 8000
  return `http://${hostname}:8000`;
}

export const API_BASE_URL = getApiBaseUrl();

console.log('🌐 API Configuration:', {
  hostname: window.location.hostname,
  apiBaseUrl: API_BASE_URL,
  environment: import.meta.env.MODE
});

export default API_BASE_URL;
