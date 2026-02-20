import { useState, useEffect } from 'react';
import { Home, Calendar, Clock, AlertCircle, CheckCircle, XCircle, Mail } from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/authcontext';

export default function WFHManager() {
  const { user } = useAuth();
  const [wfhRequests, setWfhRequests] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newWfhRequest, setNewWfhRequest] = useState({
    date: '',
    reason: '',
    manager_approval_email: false
  });

  useEffect(() => {
    fetchWfhRequests();
  }, []);

  const fetchWfhRequests = async () => {
    try {
      setLoading(true);
      const response = await api.get('/leave/wfh/requests');
      setWfhRequests(response.data?.data || []);
    } catch (error) {
      console.error('Error fetching WFH requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        date: newWfhRequest.date,
        reason: newWfhRequest.reason,
        manager_approval_email: newWfhRequest.manager_approval_email
      };

      await api.post('/leave/wfh/request', payload);
      
      setShowForm(false);
      setNewWfhRequest({
        date: '',
        reason: '',
        manager_approval_email: false
      });
      fetchWfhRequests();
      alert('WFH request submitted successfully!');
    } catch (error) {
      console.error('Error submitting WFH request:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to submit WFH request';
      alert(errorMessage);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewWfhRequest(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const isRestrictedDay = (date) => {
    const dayOfWeek = new Date(date).getDay();
    return dayOfWeek === 1 || dayOfWeek === 5; // Monday or Friday
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="bg-gray-200 h-8 rounded w-1/3"></div>
        <div className="bg-gray-200 h-32 rounded"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Home className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Work From Home</h2>
            <p className="text-sm text-gray-600">Manage your remote work requests</p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center space-x-2"
        >
          <Home className="w-4 h-4" />
          <span>{showForm ? 'Cancel Request' : 'Request WFH'}</span>
        </button>
      </div>

      {/* WFH Policy Notice */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-amber-800">WFH Policy Guidelines</h3>
            <ul className="mt-2 text-sm text-amber-700 space-y-1">
              <li>• WFH on Mondays and Fridays requires manager approval</li>
              <li>• Minimum 1 day advance notice required</li>
              <li>• Avoid WFH immediately before/after holidays</li>
              <li>• Ensure HR is informed of approved WFH requests</li>
            </ul>
          </div>
        </div>
      </div>

      {/* WFH Request Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">New WFH Request</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                WFH Date
              </label>
              <input
                type="date"
                name="date"
                value={newWfhRequest.date}
                onChange={handleInputChange}
                min={getMinDate()}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {newWfhRequest.date && isRestrictedDay(newWfhRequest.date) && (
                <p className="mt-1 text-sm text-amber-600 flex items-center space-x-1">
                  <AlertCircle className="w-4 h-4" />
                  <span>This is a restricted day (Monday/Friday) - Manager approval required</span>
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reason for WFH
              </label>
              <textarea
                name="reason"
                value={newWfhRequest.reason}
                onChange={handleInputChange}
                required
                rows={3}
                placeholder="e.g., Personal appointment, Home maintenance, Better focus environment..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {newWfhRequest.date && isRestrictedDay(newWfhRequest.date) && (
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  name="manager_approval_email"
                  checked={newWfhRequest.manager_approval_email}
                  onChange={handleInputChange}
                  required
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label className="text-sm text-gray-700 flex items-center space-x-1">
                  <Mail className="w-4 h-4" />
                  <span>I have obtained manager approval via email</span>
                </label>
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Submit Request
              </button>
            </div>
          </form>
        </div>
      )}

      {/* WFH Requests List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">My WFH Requests</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {wfhRequests.map((request) => (
            <div key={request.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Calendar className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(request.date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">{request.reason}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>Requested: {new Date(request.created_at).toLocaleDateString()}</span>
                      {request.manager_approval_email && (
                        <span className="flex items-center space-x-1 text-blue-600">
                          <Mail className="w-3 h-3" />
                          <span>Manager Approved</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                    {getStatusIcon(request.status)}
                    <span className="ml-1">{request.status.charAt(0).toUpperCase() + request.status.slice(1)}</span>
                  </span>
                </div>
              </div>
            </div>
          ))}
          {wfhRequests.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              <Home className="w-12 h-12 mx-auto text-gray-300 mb-4" />
              <p>No WFH requests found</p>
              <p className="text-sm mt-1">Click "Request WFH" to create your first request</p>
            </div>
          )}
        </div>
      </div>

      {/* WFH Statistics */}
      {wfhRequests.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Approved WFH</p>
                <p className="text-2xl font-bold text-gray-900">
                  {wfhRequests.filter(r => r.status === 'approved').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending WFH</p>
                <p className="text-2xl font-bold text-gray-900">
                  {wfhRequests.filter(r => r.status === 'pending').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Home className="w-5 h-5 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Requests</p>
                <p className="text-2xl font-bold text-gray-900">{wfhRequests.length}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}