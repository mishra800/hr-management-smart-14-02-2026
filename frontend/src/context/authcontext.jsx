import { createContext, useState, useContext, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false); // Changed to false - don't load on mount

  // Simple function to check if user appears to be logged in
  const isLoggedIn = () => {
    const token = localStorage.getItem('token');
    return !!token && token.split('.').length === 3; // Basic JWT format check
  };

  const fetchUser = async () => {
    // Don't make API call if no token
    if (!isLoggedIn()) {
      setUser(null);
      return null;
    }

    try {
      const response = await api.get('/users/me');
      console.log('Fetched User:', response.data);
      
      // Handle both direct data and APIResponse format
      const userData = response.data.data || response.data;
      setUser(userData);
      return userData;
    } catch (error) {
      console.error('Error fetching user:', error);
      
      // If it's a 401 error, the token is likely expired
      if (error.response?.status === 401) {
        console.log('Token expired or invalid, clearing auth state');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('profile_setup_completed');
        setUser(null);
      }
      
      setUser(null);
      return null;
    }
  };

  useEffect(() => {
    // Validate token on mount
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const tokenParts = token.split('.');
        if (tokenParts.length === 3) {
          // Token has correct JWT format, validate it
          console.log('✅ Token found and validated');
          // Optionally fetch user data to verify token is still valid
          fetchUser().catch(err => {
            console.warn('⚠️ Token validation failed:', err.message);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            localStorage.removeItem('profile_setup_completed');
            setUser(null);
          });
        } else {
          console.warn('⚠️ Invalid token format');
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          localStorage.removeItem('profile_setup_completed');
          setUser(null);
        }
      } catch (error) {
        console.error('❌ Error validating token:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('profile_setup_completed');
        setUser(null);
      }
    }
  }, []);

  const checkFirstTimeLogin = async (userData) => {
    try {
      // Only check for employees - simplified version
      if (userData.role === 'employee') {
        // For now, just check if it's first time login
        const isFirstLogin = !localStorage.getItem('profile_setup_completed');
        if (isFirstLogin) {
          // Mark as completed to avoid repeated redirects
          localStorage.setItem('profile_setup_completed', 'true');
        }
      }
    } catch (error) {
      console.error('Error checking first time login:', error);
      // Don't let this prevent login
    }
  };

  const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await api.post('/auth/login', formData);
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      
      // Fetch full user data immediately before returning
      const userData = await fetchUser();
      
      if (userData) {
        return true;
      } else {
        // If fetch failed, set temporary user and try again in background
        setUser({ email, token: access_token });
        setTimeout(() => {
          fetchUser().catch(err => console.error('Failed to fetch user:', err));
        }, 100);
        return true;
      }
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('profile_setup_completed');
    setUser(null);
  };

  // Method to validate user when needed (e.g., on protected route access)
  const validateUser = async () => {
    if (!isLoggedIn()) {
      setUser(null);
      return false;
    }

    // If we already have user data, don't fetch again
    if (user && user.email && user.role) {
      return true;
    }

    // Fetch user data if we don't have it
    const userData = await fetchUser();
    return !!userData;
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, fetchUser, isLoggedIn, validateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
