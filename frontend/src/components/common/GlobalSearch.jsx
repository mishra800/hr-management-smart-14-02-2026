import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../config/api';

export default function GlobalSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (searchQuery.length > 2) {
      performSearch();
    } else {
      setResults(null);
    }
  }, [searchQuery]);

  const performSearch = async () => {
    setLoading(true);
    try {
      const response = await api.get('/features/search/global', {
        params: { q: searchQuery, limit: 50 }
      });
      setResults(response.data);
      setShowResults(true);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResultClick = (type, id, path) => {
    navigate(path);
    setSearchQuery('');
    setShowResults(false);
  };

  return (
    <div className="relative w-full max-w-md">
      <div className="relative">
        <input
          type="text"
          placeholder="🔍 Search employees, jobs, leaves..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => searchQuery && setShowResults(true)}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {loading && <span className="absolute right-3 top-2.5">⏳</span>}
      </div>

      {showResults && results && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border z-50 max-h-96 overflow-y-auto">
          {/* Employees */}
          {results.employees?.length > 0 && (
            <div className="border-b">
              <div className="px-4 py-2 bg-gray-50 font-semibold text-sm">Employees</div>
              {results.employees.map(emp => (
                <div
                  key={emp.id}
                  onClick={() => handleResultClick('employee', emp.id, `/employees/${emp.id}`)}
                  className="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b"
                >
                  <div className="font-medium">{emp.name}</div>
                  <div className="text-sm text-gray-600">{emp.position} • {emp.email}</div>
                </div>
              ))}
            </div>
          )}

          {/* Job Applications */}
          {results.job_applications?.length > 0 && (
            <div className="border-b">
              <div className="px-4 py-2 bg-gray-50 font-semibold text-sm">Job Applications</div>
              {results.job_applications.map(app => (
                <div
                  key={app.id}
                  onClick={() => handleResultClick('application', app.id, `/recruitment`)}
                  className="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b"
                >
                  <div className="font-medium">{app.candidate_name}</div>
                  <div className="text-sm text-gray-600">Status: {app.status}</div>
                </div>
              ))}
            </div>
          )}

          {/* Announcements */}
          {results.announcements?.length > 0 && (
            <div>
              <div className="px-4 py-2 bg-gray-50 font-semibold text-sm">Announcements</div>
              {results.announcements.map(ann => (
                <div
                  key={ann.id}
                  onClick={() => handleResultClick('announcement', ann.id, `/announcements`)}
                  className="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b"
                >
                  <div className="font-medium">{ann.title}</div>
                  <div className="text-sm text-gray-600">{ann.content}</div>
                </div>
              ))}
            </div>
          )}

          {!results.employees?.length && !results.job_applications?.length && !results.announcements?.length && (
            <div className="px-4 py-4 text-center text-gray-500">
              No results found
            </div>
          )}
        </div>
      )}
    </div>
  );
}
