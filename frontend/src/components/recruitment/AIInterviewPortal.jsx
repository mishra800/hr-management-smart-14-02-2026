import { useState, useEffect, useRef } from 'react';
import api from '../../api/axios';

export default function AIInterviewPortal({ sessionToken }) {
  const [session, setSession] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    fetchInterviewSession();
  }, [sessionToken]);

  const fetchInterviewSession = async () => {
    try {
      const response = await api.get(`/ai-interview/session/${sessionToken}`);
      setSession(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching session:', error);
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setRecordedAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleSubmitResponse = async () => {
    if (!session || !session.questions[currentQuestionIndex]) return;

    setSubmitting(true);
    try {
      const questionId = session.questions[currentQuestionIndex].id;
      const responseText = responses[questionId] || '';

      await api.post(`/ai-interview/response/submit/${questionId}`, {
        response_text: responseText,
        audio_url: recordedAudio ? URL.createObjectURL(recordedAudio) : null
      });

      // Move to next question
      if (currentQuestionIndex < session.questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setRecordedAudio(null);
      } else {
        // Complete interview
        await completeInterview();
      }
    } catch (error) {
      console.error('Error submitting response:', error);
      alert('Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  const completeInterview = async () => {
    try {
      await api.post(`/ai-interview/complete/${session.id}`);
      alert('Interview completed! Results will be sent to your email.');
      // Redirect to results page or close modal
    } catch (error) {
      console.error('Error completing interview:', error);
      alert('Failed to complete interview');
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading interview...</div>;
  }

  if (!session || !session.questions || session.questions.length === 0) {
    return <div className="text-center py-8">No interview questions available</div>;
  }

  const currentQuestion = session.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / session.questions.length) * 100;

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium">Question {currentQuestionIndex + 1} of {session.questions.length}</span>
          <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">{currentQuestion.question}</h2>
      </div>

      {/* Response Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Your Answer</label>
        <textarea
          value={responses[currentQuestion.id] || ''}
          onChange={(e) => setResponses({
            ...responses,
            [currentQuestion.id]: e.target.value
          })}
          placeholder="Type your answer here..."
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows="4"
        />
      </div>

      {/* Recording Controls */}
      <div className="mb-6 flex gap-3">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            🎤 Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex items-center gap-2 px-4 py-2 bg-red-700 text-white rounded-lg hover:bg-red-800"
          >
            ⏹️ Stop Recording
          </button>
        )}
        {recordedAudio && (
          <span className="text-sm text-green-600 flex items-center gap-1">
            ✓ Audio recorded
          </span>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between gap-3">
        <button
          onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
          disabled={currentQuestionIndex === 0}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          ← Previous
        </button>

        <button
          onClick={handleSubmitResponse}
          disabled={submitting || !responses[currentQuestion.id]}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Submitting...' : currentQuestionIndex === session.questions.length - 1 ? 'Complete Interview' : 'Next →'}
        </button>
      </div>
    </div>
  );
}
