import { useState, useEffect } from 'react';
import { Calendar, Clock, AlertTriangle, Upload, X, CheckCircle, Info } from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/authcontext';
import BirthdayAnniversaryLeaveForm from './BirthdayAnniversaryLeaveForm';

export default function EnhancedLeaveRequestForm({ onClose, onSubmit }) {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    leave_type: '',
    start_date: '',
    end_date: '',
    reason: '',
    is_half_day: false,
    half_day_period: 'morning',
    emergency: false,
    medical_certificate: null,
    manager_email_approval: '',
    contact_number: '',
    alternate_contact: '',
    medical_reason_details: '',
    family_member_relation: '',
    expected_delivery_date: '',
    child_number: 1,
    adoption_date: '',
    // New fields for enhanced maternity/paternity leave
    pregnancy_stage: '',
    child_birth_date: '',
    spouse_name: '',
    hospital_name: '',
    doctor_certificate: null,
    advance_notice_days: 0
  });

  const [leaveTypes, setLeaveTypes] = useState([]);
  const [leaveBalance, setLeaveBalance] = useState([]);
  const [validation, setValidation] = useState({});
  const [policyCompliance, setPolicyCompliance] = useState({});
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showBirthdayAnniversaryForm, setShowBirthdayAnniversaryForm] = useState(false);

  useEffect(() => {
    fetchLeaveTypes();
    fetchLeaveBalance();
  }, []);

  useEffect(() => {
    if (formData.leave_type && formData.start_date && formData.end_date) {
      validateLeaveRequest();
    }
  }, [formData.leave_type, formData.start_date, formData.end_date]);

  const fetchLeaveTypes = async () => {
    try {
      const response = await api.get('/leave/types');
      setLeaveTypes(response.data?.data || []);
    } catch (error) {
      console.error('Error fetching leave types:', error);
    }
  };

  const fetchLeaveBalance = async () => {
    try {
      const response = await api.get('/leave/balance');
      setLeaveBalance(response.data?.data || []);
    } catch (error) {
      console.error('Error fetching leave balance:', error);
    }
  };

  const validateLeaveRequest = async () => {
    try {
      // Mock validation for now
      const mockCompliance = {
        compliant: true,
        compliance_score: 85,
        checks: {
          leave_type_valid: true,
          advance_notice_given: true,
          not_adjacent_to_weekend: true,
          not_adjacent_to_holiday: true,
          within_balance_limits: true,
          manager_approval_required: true,
          hr_approval_required: false,
          medical_certificate_required: false
        },
        violations: [],
        recommendations: []
      };
      setPolicyCompliance(mockCompliance);
    } catch (error) {
      console.error('Error validating leave request:', error);
      // Set default compliance data
      setPolicyCompliance({
        compliant: true,
        compliance_score: 100,
        checks: {},
        violations: [],
        recommendations: []
      });
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Check if Birthday/Anniversary Leave is selected
    if (name === 'leave_type') {
      const isBirthdayAnniversaryLeave = value === 'Birthday / Wedding Anniversary Leave' || 
                                        leaveTypes.find(lt => lt.code === value)?.name === 'Birthday / Wedding Anniversary Leave';
      setShowBirthdayAnniversaryForm(isBirthdayAnniversaryLeave);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setFormData(prev => ({
          ...prev,
          medical_certificate: e.target.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFileChange = (e) => {
    const { name } = e.target;
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFormData(prev => ({
          ...prev,
          [name]: event.target.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleBirthdayAnniversarySubmit = (leaveRequest) => {
    // Submit the birthday/anniversary leave request
    handleSubmitLeaveRequest(leaveRequest);
  };

  const handleBirthdayAnniversaryCancel = () => {
    setShowBirthdayAnniversaryForm(false);
    setFormData(prev => ({ ...prev, leave_type: '' }));
  };

  const handleSubmitLeaveRequest = async (leaveRequestData) => {
    setLoading(true);
    try {
      const response = await api.post('/leave/request', leaveRequestData);
      if (response.data.success) {
        alert('Leave request submitted successfully!');
        if (onSubmit) onSubmit(response.data.data);
        onClose();
      }
    } catch (error) {
      console.error('Error submitting leave request:', error);
      alert(error.response?.data?.detail || 'Failed to submit leave request');
    } finally {
      setLoading(false);
    }
  };

  const calculateLeaveDays = () => {
    if (!formData.start_date || !formData.end_date) return 0;
    
    const start = new Date(formData.start_date);
    const end = new Date(formData.end_date);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    
    return formData.is_half_day ? 0.5 : diffDays;
  };

  const getLeaveBalance = (leaveType) => {
    const balance = leaveBalance.find(b => b.leave_type === leaveType);
    return balance ? balance.balance : 0;
  };

  const getLeaveTypeDetails = (leaveType) => {
    return leaveTypes.find(type => type.code === leaveType);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = formData.emergency ? '/leave/emergency' : '/leave/request';
      const response = await api.post(endpoint, formData);
      
      if (response.data?.success) {
        onSubmit?.(response.data.data);
        onClose?.();
      }
    } catch (error) {
      console.error('Error submitting leave request:', error);
      alert(error.response?.data?.detail || 'Failed to submit leave request');
    } finally {
      setLoading(false);
    }
  };

  const selectedLeaveType = getLeaveTypeDetails(formData.leave_type);
  const currentBalance = getLeaveBalance(formData.leave_type);
  const requestedDays = calculateLeaveDays();

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {showBirthdayAnniversaryForm ? (
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Birthday / Anniversary Leave Request
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <BirthdayAnniversaryLeaveForm
              onSubmit={handleBirthdayAnniversarySubmit}
              onCancel={handleBirthdayAnniversaryCancel}
            />
          </div>
        ) : (
          <div>
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">
                  {formData.emergency ? 'Emergency Leave Request' : 'Leave Request'}
                </h2>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Leave Type Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Leave Type *
              </label>
              <select
                name="leave_type"
                value={formData.leave_type}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Leave Type</option>
                {leaveTypes.map(type => (
                  <option key={type.code} value={type.code}>
                    {type.name} ({type.code})
                  </option>
                ))}
              </select>
              
              {selectedLeaveType && (
                <div className="mt-2 p-3 bg-blue-50 rounded-md">
                  <p className="text-sm text-blue-800">
                    <strong>Balance:</strong> {currentBalance} days
                  </p>
                  <p className="text-sm text-blue-600 mt-1">
                    {selectedLeaveType.rules}
                  </p>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Emergency Request
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  name="emergency"
                  checked={formData.emergency}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-600">
                  This is an emergency leave request
                </span>
              </div>
              {formData.emergency && (
                <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5" />
                    <p className="text-sm text-yellow-800">
                      Emergency requests must be applied in SMHR within 2 days of return to office.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Date Selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date *
              </label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date *
              </label>
              <input
                type="date"
                name="end_date"
                value={formData.end_date}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration
              </label>
              <div className="space-y-2">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    name="is_half_day"
                    checked={formData.is_half_day}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="text-sm text-gray-600">Half Day</span>
                </div>
                
                {formData.is_half_day && (
                  <select
                    name="half_day_period"
                    value={formData.half_day_period}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  >
                    <option value="morning">Morning (10:00 AM - 2:00 PM)</option>
                    <option value="afternoon">Afternoon (2:00 PM - 7:00 PM)</option>
                  </select>
                )}
                
                <div className="text-sm text-gray-600">
                  <strong>Total Days:</strong> {requestedDays}
                </div>
              </div>
            </div>
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason *
            </label>
            <textarea
              name="reason"
              value={formData.reason}
              onChange={handleInputChange}
              required
              rows={3}
              placeholder="Please provide a detailed reason for your leave request..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Contact Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contact Number *
              </label>
              <input
                type="tel"
                name="contact_number"
                value={formData.contact_number}
                onChange={handleInputChange}
                required
                placeholder="+91 9876543210"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Alternate Contact
              </label>
              <input
                type="tel"
                name="alternate_contact"
                value={formData.alternate_contact}
                onChange={handleInputChange}
                placeholder="+91 9876543210"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Leave Type Specific Fields */}
          {formData.leave_type === 'SL' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Medical Reason Details
              </label>
              <textarea
                name="medical_reason_details"
                value={formData.medical_reason_details}
                onChange={handleInputChange}
                rows={2}
                placeholder="Please describe your medical condition..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {formData.leave_type === 'BRL' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Family Member Relation
              </label>
              <select
                name="family_member_relation"
                value={formData.family_member_relation}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Relation</option>
                <option value="father">Father</option>
                <option value="mother">Mother</option>
                <option value="spouse">Spouse</option>
                <option value="child">Child</option>
                <option value="sibling">Sibling</option>
                <option value="grandparent">Grandparent</option>
              </select>
            </div>
          )}

          {formData.leave_type === 'ML' && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <h4 className="font-medium text-blue-900 mb-2">Maternity Leave Policy</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Eligible for 108 days of maternity leave</li>
                  <li>• Must apply at least 2 months (60 days) in advance</li>
                  <li>• Medical documents are mandatory</li>
                  <li>• Can be taken after 7 months of pregnancy or after childbirth</li>
                  <li>• Approval flow: Employee → HR → Manager</li>
                </ul>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pregnancy Stage *
                  </label>
                  <select
                    name="pregnancy_stage"
                    value={formData.pregnancy_stage}
                    onChange={handleInputChange}
                    required
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select Stage</option>
                    <option value="after_7_months">After 7 months of pregnancy</option>
                    <option value="after_childbirth">After childbirth</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Expected/Actual Delivery Date *
                  </label>
                  <input
                    type="date"
                    name="expected_delivery_date"
                    value={formData.expected_delivery_date}
                    onChange={handleInputChange}
                    required
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hospital Name
                  </label>
                  <input
                    type="text"
                    name="hospital_name"
                    value={formData.hospital_name}
                    onChange={handleInputChange}
                    placeholder="Hospital/Clinic name"
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Doctor Certificate *
                  </label>
                  <input
                    type="file"
                    name="doctor_certificate"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png"
                    required
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          )}

          {formData.leave_type === 'PL' && (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <h4 className="font-medium text-green-900 mb-2">Paternity Leave Policy</h4>
                <ul className="text-sm text-green-800 space-y-1">
                  <li>• Eligible for 3 days of paternity leave</li>
                  <li>• Must be taken around the time of childbirth</li>
                  <li>• Approval flow: Employee → HR → Manager</li>
                </ul>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Child Birth Date *
                  </label>
                  <input
                    type="date"
                    name="child_birth_date"
                    value={formData.child_birth_date}
                    onChange={handleInputChange}
                    required
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Spouse Name
                  </label>
                  <input
                    type="text"
                    name="spouse_name"
                    value={formData.spouse_name}
                    onChange={handleInputChange}
                    placeholder="Spouse's full name"
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hospital Name
                </label>
                <input
                  type="text"
                  name="hospital_name"
                  value={formData.hospital_name}
                  onChange={handleInputChange}
                  placeholder="Hospital/Clinic where child was born"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          {/* Medical Certificate Upload */}
          {(formData.leave_type === 'SL' || formData.leave_type === 'ML') && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Medical Certificate
                {formData.leave_type === 'ML' && <span className="text-red-500"> *</span>}
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4">
                    <label className="cursor-pointer">
                      <span className="mt-2 block text-sm font-medium text-gray-900">
                        Upload medical certificate
                      </span>
                      <input
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={handleFileUpload}
                        className="hidden"
                        required={formData.leave_type === 'ML'}
                      />
                    </label>
                    <p className="mt-1 text-xs text-gray-500">
                      PDF, PNG, JPG up to 10MB
                    </p>
                  </div>
                </div>
              </div>
              {formData.medical_certificate && (
                <div className="mt-2 flex items-center space-x-2 text-sm text-green-600">
                  <CheckCircle className="w-4 h-4" />
                  <span>Medical certificate uploaded</span>
                </div>
              )}
            </div>
          )}

          {/* Emergency Manager Approval */}
          {formData.emergency && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Manager Email Approval
              </label>
              <input
                type="email"
                name="manager_email_approval"
                value={formData.manager_email_approval}
                onChange={handleInputChange}
                placeholder="manager@company.com"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Required for emergency leave requests for past dates
              </p>
            </div>
          )}

          {/* Policy Compliance Check */}
          {policyCompliance.compliance_score !== undefined && (
            <div className="border rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Info className="w-5 h-5 text-blue-600" />
                <h3 className="text-sm font-medium text-gray-900">Policy Compliance Check</h3>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Compliance Score</span>
                  <span className={`text-sm font-medium ${
                    policyCompliance.compliance_score >= 80 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {policyCompliance.compliance_score}%
                  </span>
                </div>
                
                {policyCompliance.violations?.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-red-600 mb-2">Policy Violations:</p>
                    <ul className="text-sm text-red-600 space-y-1">
                      {policyCompliance.violations.map((violation, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <span>•</span>
                          <span>{violation.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {policyCompliance.recommendations?.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-blue-600 mb-2">Recommendations:</p>
                    <ul className="text-sm text-blue-600 space-y-1">
                      {policyCompliance.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <span>•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || (policyCompliance.compliance_score !== undefined && policyCompliance.compliance_score < 50)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Submitting...' : 'Submit Request'}
            </button>
          </div>
        </form>
          </div>
        )}
      </div>
    </div>
  );
}