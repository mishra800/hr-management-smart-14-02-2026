import { useState } from 'react';
import { Calendar, Clock, AlertTriangle, Send } from 'lucide-react';
import api from '../../api/axios';

export default function MobileLeaveRequest({ onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    leave_type: 'CL',
    start_date: '',
    end_date: '',
    reason: '',
    is_half_day: false,
    half_day_period: 'morning'
  });
  const [loading, setLoading] = useState(false);

  const leaveTypes = [
    { code: 'CL', name: 'Casual Leave', emoji: '🏖️' },
    { code: 'SL', name: 'Sick Leave', emoji: '🤒' },
    { code: 'AL', name: 'Annual Leave', emoji: '✈️' },
    { code: 'PL', name: 'Personal Leave', emoji: '👤' }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        leave_type: formData.leave_type,
        start_date: formData.start_date,
        end_date: formData.is_half_day ? formData.start_date : formData.end_date,
        reason: formData.reason,
        is_half_day: formData.is_half_day,
        half_day_period: formData.is_half_day ? formData.half_day_period : null
      };

      const response = await api.post('/leave/request', payload);
      
      if (onSuccess) {
        onSuccess(response.data);
      }
      
      alert('Leave request submitted successfully!');
    } catch (error) {
      console.error('Error submitting leave request:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to submit leave request';
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getTodayDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  const calculateDuration = () => {
    if (!formData.start_date || !formData.end_date) return 0;
    if (formData.is_half_day) return 0.5;
    
    const start = new Date(formData.start_date);
    const end = new Date(formData.end_date);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
  };

  return (
    <div className="fixed inset-0 bg-white z-50 overflow-y-auto">
      {/* Mobile Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <button
          onClick={onCancel}
          className="text-gray-600 hover:text-gray-800"
        >
          ← Cancel
        </button>
        <h1 className="text-lg font-semibold text-gray-900">Request Leave</h1>
        <div className="w-16"></div> {/* Spacer for centering */}
      </div>

      <form onSubmit={handleSubmit} className="p-4 space-y-6">
        {/* Leave Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Leave Type
          </label>
          <div className="grid grid-cols-2 gap-3">
            {leaveTypes.map((type) => (
              <label
                key={type.code}
                className={`flex items-center space-x-3 p-4 border rounded-lg cursor-pointer transition-colors ${
                  formData.leave_type === type.code
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="leave_type"
                  value={type.code}
                  checked={formData.leave_type === type.code}
                  onChange={handleInputChange}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xl">{type.emoji}</span>
                <div>
                  <div className="text-sm font-medium text-gray-900">{type.name}</div>
                  <div className="text-xs text-gray-500">{type.code}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Half Day Option */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              name="is_half_day"
              checked={formData.is_half_day}
              onChange={handleInputChange}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-gray-500" />
              <span className="text-sm font-medium text-gray-900">Half Day Leave</span>
            </div>
          </label>
          
          {formData.is_half_day && (
            <div className="mt-3 grid grid-cols-2 gap-3">
              <label className={`flex items-center justify-center p-3 border rounded-lg cursor-pointer ${
                formData.half_day_period === 'morning' 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300'
              }`}>
                <input
                  type="radio"
                  name="half_day_period"
                  value="morning"
                  checked={formData.half_day_period === 'morning'}
                  onChange={handleInputChange}
                  className="sr-only"
                />
                <div className="text-center">
                  <div className="text-lg">🌅</div>
                  <div className="text-sm font-medium">Morning</div>
                  <div className="text-xs text-gray-500">10 AM - 2 PM</div>
                </div>
              </label>
              
              <label className={`flex items-center justify-center p-3 border rounded-lg cursor-pointer ${
                formData.half_day_period === 'afternoon' 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300'
              }`}>
                <input
                  type="radio"
                  name="half_day_period"
                  value="afternoon"
                  checked={formData.half_day_period === 'afternoon'}
                  onChange={handleInputChange}
                  className="sr-only"
                />
                <div className="text-center">
                  <div className="text-lg">🌇</div>
                  <div className="text-sm font-medium">Afternoon</div>
                  <div className="text-xs text-gray-500">2 PM - 7 PM</div>
                </div>
              </label>
            </div>
          )}
        </div>

        {/* Date Selection */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                min={getTodayDate()}
                required
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {!formData.is_half_day && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleInputChange}
                  min={formData.start_date || getTodayDate()}
                  required={!formData.is_half_day}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}
        </div>

        {/* Duration Display */}
        {(formData.start_date && (formData.end_date || formData.is_half_day)) && (
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">
                Duration: {calculateDuration()} {calculateDuration() === 1 ? 'day' : 'days'}
              </span>
            </div>
          </div>
        )}

        {/* Reason */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Reason for Leave
          </label>
          <textarea
            name="reason"
            value={formData.reason}
            onChange={handleInputChange}
            required
            rows={4}
            placeholder="Please provide a brief reason for your leave request..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
        </div>

        {/* Policy Reminder */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-amber-800">Policy Reminder</h4>
              <ul className="mt-2 text-sm text-amber-700 space-y-1">
                <li>• Apply for leave at least 1 day in advance</li>
                <li>• Maximum 3 consecutive casual leaves allowed</li>
                <li>• Medical certificate required for sick leave > 2 days</li>
                <li>• Avoid clubbing leaves with weekends/holidays</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="sticky bottom-0 bg-white pt-4 pb-6 border-t border-gray-200 -mx-4 px-4">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Submit Leave Request</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}