import React, { useState } from 'react';
import { Card } from '../ui/Card';
import Button from '../ui/Button';

const BirthdayAnniversaryDemo = () => {
  const [selectedOccasion, setSelectedOccasion] = useState('');
  const [leaveDate, setLeaveDate] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  // Mock data for demo
  const mockEmployeeData = {
    birthday: {
      date: "2024-05-15",
      formatted: "May 15",
      eligible: true
    },
    anniversary: {
      date: "2024-12-10", 
      formatted: "December 10",
      eligible: true
    },
    bl_taken_this_year: null, // null means no BL leave taken yet
    policy: {
      rule: "You can take leave for either your birthday OR wedding anniversary per year, not both",
      max_days: 1,
      date_flexibility: "Leave can be taken within 7 days of the actual date"
    }
  };

  const { birthday, anniversary, bl_taken_this_year, policy } = mockEmployeeData;

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!selectedOccasion) {
      setError('Please select whether this leave is for your birthday or anniversary');
      return;
    }
    
    if (!leaveDate) {
      setError('Please select a leave date');
      return;
    }

    // Validate date proximity (within 7 days)
    const selectedDate = new Date(leaveDate);
    const occasionDate = new Date(selectedOccasion === 'birthday' ? birthday.date : anniversary.date);
    const daysDiff = Math.abs((selectedDate - occasionDate) / (1000 * 60 * 60 * 24));
    
    if (daysDiff > 7) {
      setError(`Leave date should be within 7 days of your ${selectedOccasion} (${selectedOccasion === 'birthday' ? birthday.formatted : anniversary.formatted})`);
      return;
    }

    setError('');
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <Card className="p-6 max-w-2xl mx-auto mt-8">
        <div className="text-center">
          <div className="text-green-600 mb-4">
            <svg className="w-16 h-16 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Leave Request Submitted Successfully!
          </h3>
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <p><strong>Leave Type:</strong> Birthday/Anniversary Leave</p>
            <p><strong>Occasion:</strong> {selectedOccasion.charAt(0).toUpperCase() + selectedOccasion.slice(1)}</p>
            <p><strong>Date:</strong> {new Date(leaveDate).toLocaleDateString()}</p>
            <p><strong>Reason:</strong> {reason || `Leave for ${selectedOccasion}`}</p>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Your leave request has been submitted for approval. You will not be able to apply for {selectedOccasion === 'birthday' ? 'anniversary' : 'birthday'} leave this year.
          </p>
          <Button onClick={() => { setSubmitted(false); setSelectedOccasion(''); setLeaveDate(''); setReason(''); }}>
            Submit Another Request
          </Button>
        </div>
      </Card>
    );
  }

  // If already taken BL leave this year (demo scenario)
  if (bl_taken_this_year) {
    return (
      <Card className="p-6 max-w-2xl mx-auto mt-8">
        <div className="text-center">
          <div className="text-yellow-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Birthday/Anniversary Leave Already Taken
          </h3>
          <p className="text-gray-600 mb-4">
            You have already taken Birthday/Anniversary leave for your <strong>{bl_taken_this_year}</strong> this year.
          </p>
          <p className="text-sm text-gray-500 mb-4">
            {policy.rule}
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <Card className="p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Birthday / Anniversary Leave Request (Demo)
          </h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-blue-800">
              <strong>Policy:</strong> {policy.rule}
            </p>
            <p className="text-sm text-blue-600 mt-1">
              {policy.date_flexibility}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Occasion Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Occasion <span className="text-red-500">*</span>
            </label>
            <div className="space-y-3">
              {birthday && (
                <div className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedOccasion === 'birthday' 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="occasion"
                      value="birthday"
                      checked={selectedOccasion === 'birthday'}
                      onChange={(e) => setSelectedOccasion(e.target.value)}
                      className="mr-3"
                    />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">
                          Birthday Leave
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        Your birthday: {birthday.formatted}
                      </p>
                    </div>
                  </label>
                </div>
              )}

              {anniversary && (
                <div className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedOccasion === 'anniversary' 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="occasion"
                      value="anniversary"
                      checked={selectedOccasion === 'anniversary'}
                      onChange={(e) => setSelectedOccasion(e.target.value)}
                      className="mr-3"
                    />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">
                          Wedding Anniversary Leave
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        Your anniversary: {anniversary.formatted}
                      </p>
                    </div>
                  </label>
                </div>
              )}
            </div>
          </div>

          {/* Leave Date Selection */}
          {selectedOccasion && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Leave Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={leaveDate}
                onChange={(e) => setLeaveDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Select a date within 7 days of your {selectedOccasion === 'birthday' ? 'birthday' : 'anniversary'}
              </p>
            </div>
          )}

          {/* Reason */}
          {selectedOccasion && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reason (Optional)
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder={`Leave for ${selectedOccasion}`}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows="3"
              />
            </div>
          )}

          {error && (
            <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <Button
              type="submit"
              disabled={!selectedOccasion || !leaveDate}
              className="flex-1"
            >
              Submit Leave Request (Demo)
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default BirthdayAnniversaryDemo;