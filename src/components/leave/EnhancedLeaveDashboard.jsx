import { useState, useEffect } from 'react';
import { Calendar, Clock, TrendingUp, AlertTriangle, CheckCircle, XCircle, Users } from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/authcontext';

export default function EnhancedLeaveDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    balances: [],
    statistics: {},
    pendingRequests: [],
    recentActivity: [],
    upcomingLeaves: [],
    teamLeaves: []
  });
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('current_year');

  useEffect(() => {
    fetchDashboardData();
  }, [selectedPeriod]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const requests = [
        api.get('/leave/balance'),
        api.get('/leave/statistics'),
        api.get('/leave/requests?status=pending'),
        api.get('/leave/requests?limit=5'),
      ];

      if (user?.role && ['admin', 'hr', 'manager'].includes(user.role)) {
        requests.push(api.get('/leave/pending'));
      }

      const responses = await Promise.all(requests);
      
      setDashboardData({
        balances: responses[0].data?.data || [],
        statistics: responses[1].data?.data || {},
        pendingRequests: responses[2].data?.data || [],
        recentActivity: responses[3].data?.data || [],
        teamLeaves: responses[4]?.data?.data || []
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
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
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-200 h-32 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Period Selection */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Leave Dashboard</h2>
        <select
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="current_year">Current Year</option>
          <option value="last_6_months">Last 6 Months</option>
          <option value="last_3_months">Last 3 Months</option>
        </select>
      </div>

      {/* Leave Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {dashboardData.balances.map((balance, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{balance.leave_type}</p>
                <p className="text-2xl font-bold text-gray-900">{balance.balance}</p>
                <p className="text-xs text-gray-500">of {balance.total_allocated} days</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Used: {balance.used}</span>
                <span>{Math.round((balance.used / balance.total_allocated) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${(balance.used / balance.total_allocated) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Leaves Taken</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.statistics.total_leaves_taken || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Requests</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.pendingRequests.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg. Leave Duration</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.statistics.average_leave_duration || 0} days</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity and Team Leaves */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {dashboardData.recentActivity.slice(0, 5).map((activity, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className={`p-2 rounded-full ${getStatusColor(activity.status)}`}>
                    {getStatusIcon(activity.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {activity.leave_type} - {activity.duration_days} day(s)
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(activity.start_date).toLocaleDateString()} - {new Date(activity.end_date).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                    {activity.status}
                  </span>
                </div>
              ))}
              {dashboardData.recentActivity.length === 0 && (
                <p className="text-gray-500 text-center py-4">No recent activity</p>
              )}
            </div>
          </div>
        </div>

        {/* Team Leaves (for managers) */}
        {user?.role && ['admin', 'hr', 'manager'].includes(user.role) && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Team Leaves</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {dashboardData.teamLeaves.slice(0, 5).map((leave, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-gray-600">
                          {leave.employee?.first_name?.[0]}{leave.employee?.last_name?.[0]}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {leave.employee?.first_name} {leave.employee?.last_name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(leave.start_date).toLocaleDateString()} - {leave.duration_days} day(s)
                        </p>
                      </div>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(leave.status)}`}>
                      {leave.status}
                    </span>
                  </div>
                ))}
                {dashboardData.teamLeaves.length === 0 && (
                  <p className="text-gray-500 text-center py-4">No team leaves</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Leave Pattern Analysis */}
      {dashboardData.statistics.leave_pattern_analysis && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Leave Pattern Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center ${
                dashboardData.statistics.leave_pattern_analysis.frequent_monday_friday 
                  ? 'bg-red-100 text-red-600' 
                  : 'bg-green-100 text-green-600'
              }`}>
                <Calendar className="w-8 h-8" />
              </div>
              <p className="mt-2 text-sm font-medium text-gray-900">Monday/Friday Pattern</p>
              <p className="text-xs text-gray-500">
                {dashboardData.statistics.leave_pattern_analysis.frequent_monday_friday ? 'Frequent' : 'Normal'}
              </p>
            </div>
            <div className="text-center">
              <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center ${
                dashboardData.statistics.leave_pattern_analysis.frequent_before_holidays 
                  ? 'bg-red-100 text-red-600' 
                  : 'bg-green-100 text-green-600'
              }`}>
                <AlertTriangle className="w-8 h-8" />
              </div>
              <p className="mt-2 text-sm font-medium text-gray-900">Holiday Pattern</p>
              <p className="text-xs text-gray-500">
                {dashboardData.statistics.leave_pattern_analysis.frequent_before_holidays ? 'Frequent' : 'Normal'}
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
                <TrendingUp className="w-8 h-8" />
              </div>
              <p className="mt-2 text-sm font-medium text-gray-900">Long Leave Frequency</p>
              <p className="text-xs text-gray-500">
                {dashboardData.statistics.leave_pattern_analysis.long_leave_frequency}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Policy Compliance Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Policy Compliance Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold text-green-900">Work-Life Balance</h4>
                <p className="text-sm text-green-700">
                  Your leave requests support our policy of balancing family & professional life
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-blue-900">Team Productivity</h4>
                <p className="text-sm text-blue-700">
                  Your attendance contributes to efficient operations and client satisfaction
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h5 className="font-medium text-gray-900 mb-2">Policy Objectives Alignment</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Attendance Policy:</span>
              <p className="text-gray-600">Promoting efficient operations and productivity</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Leave Policy:</span>
              <p className="text-gray-600">Supporting work-life balance and family time</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}