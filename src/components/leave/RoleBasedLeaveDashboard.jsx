import { useState, useEffect } from 'react';
import { 
  Calendar, Clock, TrendingUp, AlertTriangle, CheckCircle, XCircle, 
  Users, BarChart3, FileText, Settings, DollarSign, Shield,
  Home, Bell, Download, Upload, Eye, Edit, Trash2, Plus
} from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/authcontext';

export default function RoleBasedLeaveDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchRoleBasedData();
  }, [user?.role]);

  const fetchRoleBasedData = async () => {
    try {
      setLoading(true);
      // Mock data for now since the endpoint might not be available
      const mockData = {
        my_leave_balance: 12,
        pending_requests: 2,
        team_pending_approvals: 5,
        team_on_leave_today: 2,
        team_wfh_today: 3,
        total_pending_approvals: 12,
        employees_on_leave_today: 8,
        policy_violations: 3
      };
      setDashboardData(mockData);
    } catch (error) {
      console.error('Error fetching role-based data:', error);
      // Set mock data on error as well
      setDashboardData({
        my_leave_balance: 12,
        pending_requests: 2,
        team_pending_approvals: 5,
        team_on_leave_today: 2,
        team_wfh_today: 3,
        total_pending_approvals: 12,
        employees_on_leave_today: 8,
        policy_violations: 3
      });
    } finally {
      setLoading(false);
    }
  };

  // Employee Dashboard
  const EmployeeDashboard = () => (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Casual Leave</p>
              <p className="text-2xl font-bold text-blue-600">{dashboardData.my_leave_balance || 12}</p>
              <p className="text-xs text-gray-500">days remaining</p>
            </div>
            <Calendar className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sick Leave</p>
              <p className="text-2xl font-bold text-green-600">8</p>
              <p className="text-xs text-gray-500">days remaining</p>
            </div>
            <Shield className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Requests</p>
              <p className="text-2xl font-bold text-yellow-600">{dashboardData.pending_requests || 2}</p>
              <p className="text-xs text-gray-500">awaiting approval</p>
            </div>
            <Clock className="h-8 w-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Next Holiday</p>
              <p className="text-2xl font-bold text-purple-600">15</p>
              <p className="text-xs text-gray-500">days away</p>
            </div>
            <Calendar className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Plus className="h-6 w-6 text-blue-600 mb-2" />
            <span className="text-sm font-medium">Apply Leave</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Home className="h-6 w-6 text-green-600 mb-2" />
            <span className="text-sm font-medium">WFH Request</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Eye className="h-6 w-6 text-purple-600 mb-2" />
            <span className="text-sm font-medium">View Balance</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Calendar className="h-6 w-6 text-orange-600 mb-2" />
            <span className="text-sm font-medium">Calendar</span>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium">Casual Leave Approved</p>
                <p className="text-xs text-gray-500">Feb 15-16, 2024</p>
              </div>
            </div>
            <span className="text-xs text-green-600 font-medium">Approved</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Clock className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm font-medium">WFH Request Pending</p>
                <p className="text-xs text-gray-500">Feb 20, 2024</p>
              </div>
            </div>
            <span className="text-xs text-yellow-600 font-medium">Pending</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Manager Dashboard
  const ManagerDashboard = () => (
    <div className="space-y-6">
      {/* Manager Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Approvals</p>
              <p className="text-2xl font-bold text-red-600">{dashboardData.team_pending_approvals || 5}</p>
              <p className="text-xs text-gray-500">require action</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Team on Leave</p>
              <p className="text-2xl font-bold text-blue-600">{dashboardData.team_on_leave_today || 2}</p>
              <p className="text-xs text-gray-500">today</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Team WFH</p>
              <p className="text-2xl font-bold text-green-600">{dashboardData.team_wfh_today || 3}</p>
              <p className="text-xs text-gray-500">today</p>
            </div>
            <Home className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Approval Rate</p>
              <p className="text-2xl font-bold text-purple-600">92%</p>
              <p className="text-xs text-gray-500">this month</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Manager Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Manager Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <CheckCircle className="h-6 w-6 text-green-600 mb-2" />
            <span className="text-sm font-medium">Approve Leaves</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Calendar className="h-6 w-6 text-blue-600 mb-2" />
            <span className="text-sm font-medium">Team Calendar</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <BarChart3 className="h-6 w-6 text-purple-600 mb-2" />
            <span className="text-sm font-medium">Analytics</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="h-6 w-6 text-orange-600 mb-2" />
            <span className="text-sm font-medium">Export Reports</span>
          </button>
        </div>
      </div>

      {/* Pending Approvals */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Pending Approvals</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-blue-600">JD</span>
              </div>
              <div>
                <p className="text-sm font-medium">John Doe - Casual Leave</p>
                <p className="text-xs text-gray-500">Feb 25-26, 2024 • Personal work</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-green-100 text-green-700 rounded text-xs font-medium hover:bg-green-200">
                Approve
              </button>
              <button className="px-3 py-1 bg-red-100 text-red-700 rounded text-xs font-medium hover:bg-red-200">
                Reject
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-purple-600">JS</span>
              </div>
              <div>
                <p className="text-sm font-medium">Jane Smith - WFH Request</p>
                <p className="text-xs text-gray-500">Feb 22, 2024 • Medical appointment</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-green-100 text-green-700 rounded text-xs font-medium hover:bg-green-200">
                Approve
              </button>
              <button className="px-3 py-1 bg-red-100 text-red-700 rounded text-xs font-medium hover:bg-red-200">
                Reject
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // HR/Admin Dashboard
  const HRAdminDashboard = () => (
    <div className="space-y-6">
      {/* HR Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Pending</p>
              <p className="text-2xl font-bold text-red-600">{dashboardData.total_pending_approvals || 12}</p>
              <p className="text-xs text-gray-500">across all teams</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">On Leave Today</p>
              <p className="text-2xl font-bold text-blue-600">{dashboardData.employees_on_leave_today || 8}</p>
              <p className="text-xs text-gray-500">employees</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Policy Violations</p>
              <p className="text-2xl font-bold text-yellow-600">{dashboardData.policy_violations || 3}</p>
              <p className="text-xs text-gray-500">need review</p>
            </div>
            <Shield className="h-8 w-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Encashments</p>
              <p className="text-2xl font-bold text-green-600">₹45K</p>
              <p className="text-xs text-gray-500">pending</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Compliance</p>
              <p className="text-2xl font-bold text-purple-600">94%</p>
              <p className="text-xs text-gray-500">score</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* HR Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">HR Administration</h3>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <CheckCircle className="h-6 w-6 text-green-600 mb-2" />
            <span className="text-sm font-medium">Bulk Approve</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <BarChart3 className="h-6 w-6 text-blue-600 mb-2" />
            <span className="text-sm font-medium">Analytics</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Settings className="h-6 w-6 text-purple-600 mb-2" />
            <span className="text-sm font-medium">Policy Mgmt</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="h-6 w-6 text-orange-600 mb-2" />
            <span className="text-sm font-medium">Reports</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Calendar className="h-6 w-6 text-red-600 mb-2" />
            <span className="text-sm font-medium">Holidays</span>
          </button>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <Bell className="h-6 w-6 text-yellow-600 mb-2" />
            <span className="text-sm font-medium">Notifications</span>
          </button>
        </div>
      </div>

      {/* Advanced Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Department Utilization</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Engineering</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{width: '78%'}}></div>
                </div>
                <span className="text-sm font-medium">78%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Sales</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{width: '65%'}}></div>
                </div>
                <span className="text-sm font-medium">65%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Marketing</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{width: '82%'}}></div>
                </div>
                <span className="text-sm font-medium">82%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Policy Compliance</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm">Advance Notice</span>
              </div>
              <span className="text-sm font-medium text-green-600">96%</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
                <span className="text-sm">Weekend Clustering</span>
              </div>
              <span className="text-sm font-medium text-yellow-600">12%</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <XCircle className="h-4 w-4 text-red-600" />
                <span className="text-sm">Unauthorized Absence</span>
              </div>
              <span className="text-sm font-medium text-red-600">3%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

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
      {/* Role-based Header */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {user?.role === 'employee' && 'My Leave Dashboard'}
              {user?.role === 'manager' && 'Team Management Dashboard'}
              {(user?.role === 'hr' || user?.role === 'admin') && 'HR Administration Dashboard'}
            </h1>
            <p className="text-gray-600">
              {user?.role === 'employee' && 'Manage your leave requests and view balances'}
              {user?.role === 'manager' && 'Approve team requests and monitor leave patterns'}
              {(user?.role === 'hr' || user?.role === 'admin') && 'Comprehensive leave management and policy administration'}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium capitalize">
              {user?.role}
            </span>
          </div>
        </div>
      </div>

      {/* Role-specific Dashboard Content */}
      {user?.role === 'employee' && <EmployeeDashboard />}
      {user?.role === 'manager' && <ManagerDashboard />}
      {(user?.role === 'hr' || user?.role === 'admin') && <HRAdminDashboard />}
    </div>
  );
}