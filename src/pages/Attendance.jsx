import { useState } from 'react';
import { Clock, BookOpen, BarChart3, Users } from 'lucide-react';
import { useRoleCheck } from '../components/RoleGuard';
import RoleGuard from '../components/RoleGuard';
import SimpleAttendance from '../components/attendance/SimpleAttendance';
import AdminAttendanceDashboard from '../components/attendance/AdminAttendanceDashboard';
import AttendanceProcedures from '../components/attendance/AttendanceProcedures';

function AttendanceContent() {
  const { isAdmin, isHR, isManager } = useRoleCheck();
  const [activeTab, setActiveTab] = useState('attendance');
  
  const tabs = [
    { id: 'attendance', name: 'Attendance', icon: Clock },
    { id: 'procedures', name: 'Procedures & Policy', icon: BookOpen },
    ...(isAdmin() || isHR() || isManager() ? [{ id: 'dashboard', name: 'Dashboard', icon: BarChart3 }] : [])
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'attendance':
        return (isAdmin() || isHR() || isManager()) ? <AdminAttendanceDashboard /> : <SimpleAttendance />;
      case 'procedures':
        return <AttendanceProcedures />;
      case 'dashboard':
        return <AdminAttendanceDashboard />;
      default:
        return (isAdmin() || isHR() || isManager()) ? <AdminAttendanceDashboard /> : <SimpleAttendance />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Attendance Management</h1>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
}

export default function Attendance() {
  return (
    <RoleGuard 
      allowedRoles={['admin', 'hr', 'manager', 'employee']} 
      showError={true}
    >
      <AttendanceContent />
    </RoleGuard>
  );
}
