import { useState, useEffect } from 'react';
import api from '../api/axios';

export default function Learning() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    console.log('Learning component mounted');
    
    const loadData = async () => {
      try {
        console.log('Fetching data...');
        setLoading(true);
        
        // Test API call
        const response = await api.get('/learning/youtube/videos');
        console.log('API Response:', response.data);
        setData(response.data);
        
      } catch (err) {
        console.error('Error:', err);
        setError(err.message || 'Failed to load');
      } finally {
        setLoading(false);
        console.log('Loading complete');
      }
    };
    
    loadData();
  }, []);

  console.log('Rendering Learning component', { loading, error, data });

  if (loading) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Learning & Development</h1>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Learning & Development</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Learning & Development</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📺 YouTube Learning Hub</h2>
        
        {data && data.videos && data.videos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.videos.map((video) => (
              <div key={video.id} className="border rounded-lg p-4 hover:shadow-lg transition-shadow">
                <div className="aspect-video bg-gray-200 rounded mb-3">
                  <img 
                    src={video.thumbnail} 
                    alt={video.title}
                    className="w-full h-full object-cover rounded"
                  />
                </div>
                <h3 className="font-semibold text-lg mb-2">{video.title}</h3>
                <p className="text-sm text-gray-600 mb-2">{video.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{video.duration}</span>
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">{video.difficulty}</span>
                </div>
                <a 
                  href={video.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="mt-3 block w-full bg-blue-600 text-white text-center py-2 rounded hover:bg-blue-700 transition-colors"
                >
                  Watch Now
                </a>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No videos available yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
