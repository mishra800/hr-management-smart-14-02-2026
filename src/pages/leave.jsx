import { useState, useEffect } from 'react';
import { Calendar, Home, AlertTriangle, BarChart3, Clock, TrendingUp, BookOpen, Plus } from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/authcontext';
import RoleBasedLeaveDashboard from '../components/leave/RoleBasedLeaveDashboard';
import EnhancedLeaveRequestForm from '../components/leave/EnhancedLeaveRequestForm';
import WFHManager from '../components/leave/WFHManager';
import LeaveCalendar from '../components/leave/LeaveCalendar';
import EmergencyLeave from '../components/leave/EmergencyLeave';
import LeaveAnalytics from '../components/leave/LeaveAnalytics';
import PolicyDefinitions from '../components/leave/PolicyDefinitions';

export default function Leave() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showLeaveForm, setShowLeaveForm] = useState(false);
  const [showEmergencyForm, setShowEmergencyForm] = useState(false);
  const [refreshData, setRefreshData] = useState(0);
  
  const isManager = user && ['admin', 'hr', 'manager'].includes(user.role);
  const isHRAdmin = user && ['admin', 'hr'].includes(user.role);

  // Role-based tabs
  const getTabsForRole = () => {
    const baseTabs = [
      { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
      { id: 'calendar', name: 'Calendar', icon: Calendar },
      { id: 'requests', name: 'My Requests', icon: Clock },
      { id: 'policy', name: 'Policy & Guidelines', icon: BookOpen }
    ];

    if (user?.role === 'employee') {
      return [
        ...baseTabs,
        { id: 'wfh', name: 'Work From Home', icon: Home }
      ];
    }

    if (user?.role === 'manager') {
      return [
        ...baseTabs,
        { id: 'wfh', name: 'Work From Home', icon: Home },
        { id: 'analytics', name: 'Team Analytics', icon: TrendingUp },
        { id: 'approvals', name: 'Pending Approvals', icon: AlertTriangle }
      ];
    }

    if (isHRAdmin) {
      return [
        ...baseTabs,
        { id: 'wfh', name: 'Work From Home', icon: Home },
        { id: 'analytics', name: 'Advanced Analytics', icon: TrendingUp },
        { id: 'approvals', name: 'All Approvals', icon: AlertTriangle },
        { id: 'management', name: 'Leave Management', icon: BarChart3 }
      ];
    }

    return baseTabs;
  };

  const tabs = getTabsForRole();

  const handleLeaveSubmit = (leaveData) => {
    setRefreshData(prev => prev + 1);
    // Show success message or handle response
  };

  const renderRequestsTab = () => (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-lg font-semibold mb-4">My Leave Requests</h2>
      {/* Leave requests list component would go here */}
      <p className="text-gray-500">Leave requests component to be implemented</p>
    </div>
  );

  const renderApprovalsTab = () => (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-lg font-semibold mb-4">
        {isHRAdmin ? 'All Pending Approvals' : 'Team Approvals'}
      </h2>
      {/* Approvals component would go here */}
      <p className="text-gray-500">Approvals component to be implemented</p>
    </div>
  );

  const renderManagementTab = () => (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-lg font-semibold mb-4">Leave Management</h2>
      {/* Advanced management features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-2">Policy Configuration</h3>
          <p className="text-sm text-gray-600 mb-3">Manage leave policies and rules</p>
          <button className="text-blue-600 text-sm hover:underline">Configure</button>
        </div>
        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-2">Holiday Management</h3>
          <p className="text-sm text-gray-600 mb-3">Publish and manage holidays</p>
          <button className="text-blue-600 text-sm hover:underline">Manage</button>
        </div>
        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-2">Reports & Analytics</h3>
          <p className="text-sm text-gray-600 mb-3">Generate comprehensive reports</p>
          <button className="text-blue-600 text-sm hover:underline">Generate</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header with Role-based Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Leave Management</h1>
            <p className="text-gray-600">
              {user?.role === 'employee' && 'Manage your leave requests and work-life balance'}
              {user?.role === 'manager' && 'Approve team requests and monitor leave patterns'}
              {isHRAdmin && 'Comprehensive leave administration and policy management'}
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Role-based Quick Actions */}
            <button
              onClick={() => setShowLeaveForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Apply Leave
            </button>
            
            {user?.role === 'employee' && (
              <button
                onClick={() => setShowEmergencyForm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <AlertTriangle className="w-4 h-4" />
                Emergency Leave
              </button>
            )}
            
            {isHRAdmin && (
              <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <BarChart3 className="w-4 h-4" />
                Bulk Actions
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <nav className="flex space-x-8 px-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'dashboard' && <RoleBasedLeaveDashboard key={refreshData} />}
        {activeTab === 'calendar' && <LeaveCalendar />}
        {activeTab === 'wfh' && <WFHManager />}
        {activeTab === 'requests' && renderRequestsTab()}
        {activeTab === 'policy' && <PolicyDefinitions />}
        {activeTab === 'analytics' && <LeaveAnalytics />}
        {activeTab === 'approvals' && renderApprovalsTab()}
        {activeTab === 'management' && isHRAdmin && renderManagementTab()}
      </div>

      {/* Enhanced Leave Request Form */}
      {showLeaveForm && (
        <EnhancedLeaveRequestForm
          onClose={() => setShowLeaveForm(false)}
          onSubmit={handleLeaveSubmit}
        />
      )}

      {/* Emergency Leave Form */}
      {showEmergencyForm && (
        <EmergencyLeave
          onClose={() => setShowEmergencyForm(false)}
          onSubmit={handleLeaveSubmit}
        />
      )}
    </div>
  );
}