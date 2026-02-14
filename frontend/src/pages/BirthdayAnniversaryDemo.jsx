import React from 'react';
import BirthdayAnniversaryDemo from '../components/leave/BirthdayAnniversaryDemo';

const BirthdayAnniversaryDemoPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Birthday/Anniversary Leave System Demo
          </h1>
          <p className="text-lg text-gray-600 mb-2">
            Interactive demonstration of the new leave restriction feature
          </p>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 text-left max-w-2xl mx-auto">
            <h3 className="font-semibold text-yellow-800 mb-2">🎯 Feature Highlights:</h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• <strong>Mutual Exclusivity:</strong> Choose either birthday OR anniversary per year</li>
              <li>• <strong>Date Validation:</strong> Must be within 7 days of actual date</li>
              <li>• <strong>Clear Policy Display:</strong> Users understand restrictions upfront</li>
              <li>• <strong>Smart Validation:</strong> Prevents policy violations automatically</li>
            </ul>
          </div>
        </div>

        <BirthdayAnniversaryDemo />

        <div className="mt-12 max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              How to Test the Feature
            </h3>
            <div className="space-y-4 text-sm text-gray-600">
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">1</span>
                <p><strong>Select an Occasion:</strong> Choose either "Birthday Leave" or "Wedding Anniversary Leave"</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">2</span>
                <p><strong>Pick a Date:</strong> Select a leave date within 7 days of your birthday (May 15) or anniversary (December 10)</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">3</span>
                <p><strong>Submit Request:</strong> The system will validate your choice and prevent future requests for the other occasion</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">4</span>
                <p><strong>Try Edge Cases:</strong> Test with dates outside the 7-day window to see validation in action</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BirthdayAnniversaryDemoPage;