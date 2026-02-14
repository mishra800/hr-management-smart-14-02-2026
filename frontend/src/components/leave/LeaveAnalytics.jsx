import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Calendar, Download, Filter } from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/authcontext';

export default function LeaveAnalytics() {
  const { user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    if (user?.role && ['admin', 'hr', 'manager'].includes(user.role)) {
      fetchAnalytics();
    }
  }, [selectedYear, selectedDepartment, user]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.append('year', selectedYear);
      if (selectedDepartment !== 'all') {
        params.append('department', selectedDepartment);
      }

      const response = await api.get(`/leave/analytics?${params}`);
      setAnalyticsData(response.data?.data || {});
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async (format) => {
    try {
      const params = new URLSearchParams();
      params.append('format', format);
      if (selectedDepartment !== 'all') {
        params.append('department', selectedDepartment);
      }

      const response = await api.get(`/leave/reports/export?${params}`);
      const exportData = response.data?.data;
      
      if (exportData?.download_url) {
        // In a real implementation, this would trigger a file download
        alert(`Report generated! Download URL: ${exportData.download_url}`);
      }
    } catch (error) {
      console.error('Error exporting report:', error);
      alert('Failed to export report');
    }
  };

  if (!user?.role || !['admin', 'hr', 'manager'].includes(user.role)) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Access denied. Manager/HR role required.</p>
      </div>
    );
  }

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
      {/* Header with Filters */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Leave Analytics</h2>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
          <div className="relative">
            <button
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              onClick={() => {
                const dropdown = document.getElementById('export-dropdown');
                dropdown.classList.toggle('hidden');
              }}
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
            <div id="export-dropdown" className="hidden absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
              <div className="py-1">
                <button
                  onClick={() => handleExportReport('csv')}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  Export as CSV
                </button>
                <button
                  onClick={() => handleExportReport('excel')}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  Export as Excel
                </button>
                <button
                  onClick={() => handleExportReport('pdf')}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  Export as PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[2024, 2023, 2022, 2021].map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Departments</option>
                <option value="Engineering">Engineering</option>
                <option value="Marketing">Marketing</option>
                <option value="Sales">Sales</option>
                <option value="HR">HR</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={fetchAnalytics}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {analyticsData && (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Requests</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.total_leave_requests}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Approval Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.approval_rate}%</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Avg Duration</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.average_leave_duration} days</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Pending</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.pending_requests}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Charts and Detailed Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Leave Type Distribution */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Leave Type Distribution</h3>
              <div className="space-y-4">
                {analyticsData.leave_type_distribution?.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-4 h-4 bg-blue-500 rounded" style={{
                        backgroundColor: `hsl(${index * 60}, 70%, 50%)`
                      }}></div>
                      <span className="text-sm font-medium text-gray-900">{item.leave_type}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-bold text-gray-900">{item.count}</span>
                      <span className="text-xs text-gray-500 ml-1">({item.percentage}%)</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Department Statistics */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Statistics</h3>
              <div className="space-y-4">
                {analyticsData.department_wise_stats?.map((dept, index) => (
                  <div key={index} className="border-b border-gray-100 pb-3 last:border-b-0">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">{dept.department}</span>
                      <span className="text-sm text-gray-600">{dept.total_leaves} leaves</span>
                    </div>
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>Avg Duration: {dept.avg_duration} days</span>
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${(dept.total_leaves / 50) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Monthly Trends */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Trends</h3>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              {analyticsData.monthly_trends?.map((month, index) => (
                <div key={index} className="text-center">
                  <div className="mb-2">
                    <div className="w-full bg-gray-200 rounded-full h-20 flex items-end justify-center">
                      <div
                        className="bg-blue-600 rounded-full w-8"
                        style={{ height: `${(month.requests / 25) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <p className="text-xs font-medium text-gray-900">{month.month.slice(0, 3)}</p>
                  <p className="text-xs text-gray-600">{month.requests} requests</p>
                  <p className="text-xs text-green-600">{month.approved} approved</p>
                </div>
              ))}
            </div>
          </div>

          {/* Insights */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Most Popular Leave Type</h4>
                <p className="text-sm text-blue-700">{analyticsData.most_common_leave_type}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">Peak Leave Months</h4>
                <p className="text-sm text-green-700">{analyticsData.peak_leave_months?.join(', ')}</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 mb-2">Approval Rate</h4>
                <p className="text-sm text-purple-700">
                  {analyticsData.approval_rate}% of requests approved
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}