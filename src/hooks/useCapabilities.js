import { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/authcontext';

/**
 * Hook to fetch and check user capabilities based on SuperAdmin settings
 */
export function useCapabilities() {
  const { user } = useAuth();
  const [capabilities, setCapabilities] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCapabilities();
  }, [user?.role]);

  const fetchCapabilities = async () => {
    if (!user?.role) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await api.get(`/admin/capabilities/${user.role}`);
      setCapabilities(response.data.capabilities || {});
      setError(null);
    } catch (err) {
      console.error('Error fetching capabilities:', err);
      // If error, use default capabilities based on role
      setCapabilities(getDefaultCapabilities(user.role));
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Check if user has access to a specific module
   * @param {string} moduleId - Module identifier (e.g., 'dashboard', 'recruitment')
   * @returns {boolean} - True if user has access
   */
  const hasModuleAccess = (moduleId) => {
    if (!capabilities || !moduleId) return false;
    
    const moduleCapability = capabilities[moduleId];
    return moduleCapability?.enabled === true;
  };

  /**
   * Check if user has specific permission for a module
   * @param {string} moduleId - Module identifier
   * @param {string} permission - Permission type ('read', 'write', 'delete')
   * @returns {boolean} - True if user has the permission
   */
  const hasPermission = (moduleId, permission) => {
    if (!capabilities || !moduleId || !permission) return false;
    
    const moduleCapability = capabilities[moduleId];
    if (!moduleCapability?.enabled) return false;
    
    return moduleCapability.permissions?.includes(permission) === true;
  };

  /**
   * Get all enabled modules for the user
   * @returns {string[]} - Array of enabled module IDs
   */
  const getEnabledModules = () => {
    if (!capabilities) return [];
    
    return Object.keys(capabilities).filter(moduleId => 
      capabilities[moduleId]?.enabled === true
    );
  };

  return {
    capabilities,
    loading,
    error,
    hasModuleAccess,
    hasPermission,
    getEnabledModules,
    refresh: fetchCapabilities
  };
}

/**
 * Get default capabilities if API fails
 * This ensures the app doesn't break if capabilities can't be fetched
 */
function getDefaultCapabilities(role) {
  const modules = [
    'dashboard', 'recruitment', 'onboarding', 'employees', 'attendance',
    'leave', 'performance', 'engagement', 'learning', 'payroll',
    'analysis', 'career', 'assets', 'announcements'
  ];

  const defaults = {
    admin: modules.reduce((acc, mod) => ({ ...acc, [mod]: { enabled: true, permissions: ['read', 'write', 'delete'] } }), {}),
    super_admin: modules.reduce((acc, mod) => ({ ...acc, [mod]: { enabled: true, permissions: ['read', 'write', 'delete'] } }), {}),
    hr: modules.reduce((acc, mod) => ({ ...acc, [mod]: { enabled: true, permissions: ['read', 'write'] } }), {}),
    manager: {
      dashboard: { enabled: true, permissions: ['read'] },
      recruitment: { enabled: true, permissions: ['read', 'write'] },
      employees: { enabled: true, permissions: ['read', 'write'] },
      attendance: { enabled: true, permissions: ['read', 'write'] },
      leave: { enabled: true, permissions: ['read', 'write'] },
      performance: { enabled: true, permissions: ['read', 'write'] },
      engagement: { enabled: true, permissions: ['read', 'write'] },
      analysis: { enabled: true, permissions: ['read'] },
      assets: { enabled: true, permissions: ['read'] },
      announcements: { enabled: true, permissions: ['read'] },
    },
    employee: {
      dashboard: { enabled: true, permissions: ['read'] },
      attendance: { enabled: true, permissions: ['read'] },
      leave: { enabled: true, permissions: ['read'] },
      performance: { enabled: true, permissions: ['read'] },
      engagement: { enabled: true, permissions: ['read'] },
      learning: { enabled: true, permissions: ['read'] },
      career: { enabled: true, permissions: ['read'] },
      assets: { enabled: true, permissions: ['read'] },
      announcements: { enabled: true, permissions: ['read'] },
    },
    assets_team: {
      dashboard: { enabled: true, permissions: ['read'] },
      assets: { enabled: true, permissions: ['read', 'write'] },
      announcements: { enabled: true, permissions: ['read'] },
    },
    candidate: {
      dashboard: { enabled: true, permissions: ['read'] },
    }
  };

  return defaults[role] || defaults.employee;
}
