import { useState, useEffect } from 'react';
import api from '../../api/axios';

export default function AIInterviewResults({ applicationId, onScheduleInterview }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchResults();
  }, [applicationId]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/ai-interview/results/${applicationId}`);
      setResults(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching results:', err);
      setError('Failed to load interview results');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading results...</div>;
  }

  if (error) {
    return <div className="text-center py-4 text-red-600">{error}</div>;
  }

  if (!results) {
    return <div className="text-center py-4">No results available</div>;
  }

  const scoreColor = results.overall_score >= 70 ? 'text-green-600' : 
                     results.overall_score >= 50 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Overall Score */}
      <div className="mb-6 text-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">AI Interview Results</h3>
        <div className={`text-4xl font-bold ${scoreColor}`}>
          {results.overall_score.toFixed(1)}/100
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Recommendation: <span className="font-semibold">{results.recommendation.toUpperCase()}</span>
        </p>
      </div>

      {/* Question Breakdown */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 mb-3">Question-wise Breakdown</h4>
        <div className="space-y-3">
          {results.responses.map((response, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-3">
              <div className="flex justify-between items-start mb-2">
                <p className="font-medium text-gray-700">Q{idx + 1}: {response.question}</p>
                <span className={`text-sm font-semibold ${
                  response.score >= 70 ? 'text-green-600' : 
                  response.score >= 50 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {response.score.toFixed(1)}/100
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">
                <strong>Sentiment:</strong> {response.sentiment}
              </p>
              <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                {response.feedback}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button
          onClick={() => fetchResults()}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          🔄 Refresh
        </button>
        {results.recommendation === 'proceed' && (
          <button
            onClick={() => onScheduleInterview && onScheduleInterview()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            📅 Schedule Interview
          </button>
        )}
      </div>
    </div>
  );
}
