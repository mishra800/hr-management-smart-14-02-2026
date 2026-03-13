import { useParams } from 'react-router-dom';
import AIInterviewPortal from '../components/recruitment/AIInterviewPortal';

export default function InterviewPage() {
  const { sessionToken } = useParams();

  if (!sessionToken) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Invalid Interview Link</h1>
          <p className="text-gray-600">The interview link is invalid or has expired.</p>
          <p className="text-gray-600 mt-2">Please contact the recruiter for a new link.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto">
        <AIInterviewPortal sessionToken={sessionToken} />
      </div>
    </div>
  );
}
