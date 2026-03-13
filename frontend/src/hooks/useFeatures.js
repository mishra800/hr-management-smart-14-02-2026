import { useState, useCallback } from 'react';
import api from '../config/api';

export const useExport = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const exportToCSV = useCallback(async (data, filename = 'export') => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/features/export/csv', data, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const exportToJSON = useCallback(async (data, filename = 'export') => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/features/export/json', data, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return { exportToCSV, exportToJSON, loading, error };
};

export const useAdvancedFilter = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const filterEmployees = useCallback(async (filters) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/filter/employees', { params: filters });
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const filterLeaves = useCallback(async (filters) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/filter/leaves', { params: filters });
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const filterApplications = useCallback(async (filters) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/filter/applications', { params: filters });
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  return { filterEmployees, filterLeaves, filterApplications, loading, error };
};

export const useGlobalSearch = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const search = useCallback(async (query, limit = 50) => {
    if (query.length < 2) return null;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/search/global', {
        params: { q: query, limit }
      });
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { search, loading, error };
};

export const useAuditLogs = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getUserLogs = useCallback(async (limit = 100) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/audit/logs/user', { params: { limit } });
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const getEntityLogs = useCallback(async (entityType, entityId, limit = 50) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/features/audit/logs/entity/${entityType}/${entityId}`, {
        params: { limit }
      });
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const getActionLogs = useCallback(async (action, limit = 100) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/features/audit/logs/action/${action}`, {
        params: { limit }
      });
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  return { getUserLogs, getEntityLogs, getActionLogs, loading, error };
};

export const useNotifications = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getUnread = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/notifications/unread');
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const getCount = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/notifications/count');
      return response.data.unread_count;
    } catch (err) {
      setError(err.message);
      return 0;
    } finally {
      setLoading(false);
    }
  }, []);

  const markAsRead = useCallback(async (notificationId) => {
    try {
      await api.post(`/features/notifications/${notificationId}/read`);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  return { getUnread, getCount, markAsRead, loading, error };
};

export const useDashboardLayout = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getLayout = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/features/dashboard/layout');
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const saveLayout = useCallback(async (layout) => {
    setLoading(true);
    setError(null);
    try {
      await api.post('/features/dashboard/layout', layout);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const addWidget = useCallback(async (widgetName, position) => {
    try {
      await api.post('/features/dashboard/widget/add', null, {
        params: { widget_name: widgetName, position }
      });
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  const removeWidget = useCallback(async (widgetName) => {
    try {
      await api.post('/features/dashboard/widget/remove', null, {
        params: { widget_name: widgetName }
      });
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  const resetLayout = useCallback(async () => {
    try {
      await api.post('/features/dashboard/reset');
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  return { getLayout, saveLayout, addWidget, removeWidget, resetLayout, loading, error };
};
