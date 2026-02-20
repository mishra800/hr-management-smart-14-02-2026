import { useState } from 'react';
import { AlertTriangle, Clock, Mail, FileText, Phone } from 'lucide-react';
import api from '../../api/axios';

export default function EmergencyLeave({ onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    leave_type: 'CL',
    start_date: '',
    end_date: '',
    reason: '',
    emergency_type: '',
    manager_email_approval: false,
    medical_certificate: false,
    contact_number: '',
    emergency_contact: ''
  });
  const [loading, setLoading] = useState(false);

  const emergencyTypes = [
    { value: 'medical', label: 'Medical Emergency', icon: '🏥' },
    { value: 'family', label: 'Family Emergency', icon: '👨‍👩‍👧‍👦' },
    { value: 'personal', label: 'Personal Emergency', icon: '⚠️' },
    { value: 'bereavement', label: 'Bereavement', icon: '🕊️' },
    { value: 'natural_disaster', label: 'Natural Disaster', icon: '🌪️' },
    { value: 'other', label: 'Other Emergency', icon: '🚨' }
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
        end_date: formData.end_date,
        reason: `${formData.emergency_type.toUpperCase()}: ${formData.reason}`,
        emergency: true,
        manager_email_approval: formData.manager_email_approval,
        medical_certificate: formData.medical_certificate,
        emergency_contact: formData.emergency_contact,
        contact_number: formData.contact_number
      };

      const response = await api.post('/leave/emergency', payload);
      
      if (onSuccess) {
        onSuccess(response.data);
      }
      
      alert('Emergency leave request submitted successfully. Please complete SMHR application within 2 days of return.');
    } catch (error) {
      console.error('Error submitting emergency leave:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to submit emergency leave request';
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getTodayDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  const getYesterdayDate = () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return yesterday.toISOString().split('T')[0];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-red-50 border-b border-red-200 p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-red-900">Emergency Leave Request</h2>
              <p className="text-sm text-red-700">For urgent situations requiring immediate leave</p>
            </div>
          </div>
        </div>

        {/* Emergency Notice */}
        <div className="p-6 bg-amber-50 border-b border-amber-200">
          <div className="flex items-start space-x-3">
            <Clock className="w-5 h-5 text-amber-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-amber-800">Important Notice</h3>
              <ul className="mt-2 text-sm text-amber-700 space-y-1">
                <li>• Emergency leaves can be applied for past dates with manager approval</li>
                <li>• SMHR application must be completed within 2 days of return to office</li>
                <li>• Medical certificate required for medical emergencies</li>
                <li>• HR will be notified immediately of this emergency request</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Emergency Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Emergency Type *
            </label>
            <div className="grid grid-cols-2 gap-3">
              {emergencyTypes.map((type) => (
                <label
                  key={type.value}
                  className={`flex items-center space-x-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                    formData.emergency_type === type.value
                      ? 'border-red-500 bg-red-50'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="emergency_type"
                    value={type.value}
                    checked={formData.emergency_type === type.value}
                    onChange={handleInputChange}
                    className="text-red-600 focus:ring-red-500"
                    required
                  />
                  <span className="text-lg">{type.icon}</span>
                  <span className="text-sm font-medium text-gray-900">{type.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Leave Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date *
              </label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                max={getTodayDate()}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              />
              <p className="mt-1 text-xs text-gray-500">Can be a past date for emergencies</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date *
              </label>
              <input
                type="date"
                name="end_date"
                value={formData.end_date}
                onChange={handleInputChange}
                min={formData.start_date || getYesterdayDate()}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>

          {/* Leave Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Leave Type *
            </label>
            <select
              name="leave_type"
              value={formData.leave_type}
              onChange={handleInputChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="CL">Casual Leave</option>
              <option value="BRL">Bereavement Leave</option>
              <option value="ML">Medical Leave</option>
            </select>
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Detailed Reason *
            </label>
            <textarea
              name="reason"
              value={formData.reason}
              onChange={handleInputChange}
              required
              rows={4}
              placeholder="Please provide detailed information about the emergency situation..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>

          {/* Contact Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Contact Number *
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="tel"
                  name="contact_number"
                  value={formData.contact_number}
                  onChange={handleInputChange}
                  required
                  placeholder="+91 9876543210"
                  className="w-full pl-10 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Emergency Contact
              </label>
              <input
                type="text"
                name="emergency_contact"
                value={formData.emergency_contact}
                onChange={handleInputChange}
                placeholder="Name and phone of emergency contact"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div className="space-y-3">
            {formData.start_date && new Date(formData.start_date) < new Date() && (
              <label className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  name="manager_email_approval"
                  checked={formData.manager_email_approval}
                  onChange={handleInputChange}
                  required
                  className="mt-1 w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                />
                <div className="flex items-center space-x-2">
                  <Mail className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-700">
                    I have obtained manager approval via email for this past-date emergency leave *
                  </span>
                </div>
              </label>
            )}

            {(formData.emergency_type === 'medical' || formData.leave_type === 'ML') && (
              <label className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  name="medical_certificate"
                  checked={formData.medical_certificate}
                  onChange={handleInputChange}
                  className="mt-1 w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                />
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-700">
                    I will provide medical certificate upon return to office
                  </span>
                </div>
              </label>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="px-6 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>}
              <span>{loading ? 'Submitting...' : 'Submit Emergency Leave'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}