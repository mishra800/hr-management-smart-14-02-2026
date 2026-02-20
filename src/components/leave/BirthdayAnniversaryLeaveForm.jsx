import React, { useState, useEffect } from 'react';
import axios from '../../api/axios';
import { Card } from '../ui/Card';
import Button from '../ui/Button';

const BirthdayAnniversaryLeaveForm = ({ onSubmit, onCancel }) => {
  const [birthdayAnniversaryInfo, setBirthdayAnniversaryInfo] = useState(null);
  const [selectedOccasion, setSelectedOccasion] = useState('');
  const [leaveDate, setLeaveDate] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBirthdayAnniversaryInfo();
  }, []);

  const fetchBirthdayAnniversaryInfo = async () => {
    try {
      const response = await axios.get('/leave/birthday-anniversary-info');
      setBirthdayAnniversaryInfo(response.data.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching birthday/anniversary info:', error);
      setError('Failed to load birthday/anniversary information');
      setLoading(false);
    }
  };

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

    const leaveRequest = {
      leave_type: 'Birthday / Wedding Anniversary Leave',
      start_date: leaveDate,
      end_date: leaveDate,
      reason: reason || `Leave for ${selectedOccasion}`,
      bl_occasion_type: selectedOccasion,
      is_half_day: false
    };

    onSubmit(leaveRequest);
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="text-center">Loading birthday/anniversary information...</div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-red-600 text-center">{error}</div>
      </Card>
    );
  }

  const { birthday, anniversary, bl_taken_this_year, policy } = birthdayAnniversaryInfo;

  // If already taken BL leave this year
  if (bl_taken_this_year) {
    return (
      <Card className="p-6">
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
          <Button onClick={onCancel} variant="secondary">
            Back to Leave Types
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Birthday / Anniversary Leave Request
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
                  : birthday.eligible 
                    ? 'border-gray-300 hover:border-gray-400' 
                    : 'border-gray-200 bg-gray-50 cursor-not-allowed'
              }`}>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="occasion"
                    value="birthday"
                    checked={selectedOccasion === 'birthday'}
                    onChange={(e) => setSelectedOccasion(e.target.value)}
                    disabled={!birthday.eligible}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className={`font-medium ${birthday.eligible ? 'text-gray-900' : 'text-gray-500'}`}>
                        Birthday Leave
                      </span>
                      {!birthday.eligible && (
                        <span className="text-xs text-red-500 bg-red-100 px-2 py-1 rounded">
                          Already Used
                        </span>
                      )}
                    </div>
                    <p className={`text-sm ${birthday.eligible ? 'text-gray-600' : 'text-gray-400'}`}>
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
                  : anniversary.eligible 
                    ? 'border-gray-300 hover:border-gray-400' 
                    : 'border-gray-200 bg-gray-50 cursor-not-allowed'
              }`}>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="occasion"
                    value="anniversary"
                    checked={selectedOccasion === 'anniversary'}
                    onChange={(e) => setSelectedOccasion(e.target.value)}
                    disabled={!anniversary.eligible}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className={`font-medium ${anniversary.eligible ? 'text-gray-900' : 'text-gray-500'}`}>
                        Wedding Anniversary Leave
                      </span>
                      {!anniversary.eligible && (
                        <span className="text-xs text-red-500 bg-red-100 px-2 py-1 rounded">
                          Already Used
                        </span>
                      )}
                    </div>
                    <p className={`text-sm ${anniversary.eligible ? 'text-gray-600' : 'text-gray-400'}`}>
                      Your anniversary: {anniversary.formatted}
                    </p>
                  </div>
                </label>
              </div>
            )}
          </div>

          {!birthday && !anniversary && (
            <div className="text-center py-8 text-gray-500">
              <p>Please update your profile with your date of birth and/or wedding anniversary date to apply for this leave type.</p>
            </div>
          )}
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
            Submit Leave Request
          </Button>
          <Button
            type="button"
            onClick={onCancel}
            variant="secondary"
            className="flex-1"
          >
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default BirthdayAnniversaryLeaveForm;