import { useState } from 'react';
import api from '../../config/api';

export default function AdvancedFilter({ entityType = 'employees', onFilter }) {
  const [showFilter, setShowFilter] = useState(false);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(false);

  const filterConfigs = {
    employees: [
      { key: 'department', label: 'Department', type: 'text' },
      { key: 'position', label: 'Position', type: 'text' },
      { key: 'status', label: 'Status', type: 'select', options: ['Active', 'Inactive', 'On Leave'] },
      { key: 'search', label: 'Search', type: 'text', placeholder: 'Name, Email, ID' }
    ],
    leaves: [
      { key: 'status', label: 'Status', type: 'select', options: ['Pending', 'Approved', 'Rejected'] },
      { key: 'leave_type', label: 'Leave Type', type: 'select', options: ['Sick', 'Casual', 'Earned', 'Unpaid'] },
      { key: 'employee_id', label: 'Employee ID', type: 'number' }
    ],
    applications: [
      { key: 'status', label: 'Status', type: 'select', options: ['Applied', 'Screening', 'Interview', 'Offered', 'Rejected'] },
      { key: 'job_id', label: 'Job ID', type: 'number' },
      { key: 'search', label: 'Candidate Name/Email', type: 'text' }
    ]
  };

  const config = filterConfigs[entityType] || [];

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleApplyFilter = async () => {
    setLoading(true);
    try {
      const endpoint = `/features/filter/${entityType}`;
      const response = await api.get(endpoint, { params: filters });
      onFilter && onFilter(response.data);
      setShowFilter(false);
    } catch (error) {
      console.error('Error applying filter:', error);
      alert('Failed to apply filter');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFilters({});
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowFilter(!showFilter)}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2"
      >
        <span>🔍</span> Advanced Filter
      </button>

      {showFilter && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-10 p-4">
          <h3 className="font-semibold mb-4">Filter Options</h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {config.map(field => (
              <div key={field.key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {field.label}
                </label>
                {field.type === 'select' ? (
                  <select
                    value={filters[field.key] || ''}
                    onChange={(e) => handleFilterChange(field.key, e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All</option>
                    {field.options?.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={field.type}
                    placeholder={field.placeholder || field.label}
                    value={filters[field.key] || ''}
                    onChange={(e) => handleFilterChange(field.key, e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={handleReset}
              className="flex-1 px-3 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
            >
              Reset
            </button>
            <button
              onClick={handleApplyFilter}
              disabled={loading}
              className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Filtering...' : 'Apply'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
