import { useState, useEffect } from 'react';
import { useAuth } from '../context/authcontext';
import ProfileImageUpload from '../components/ProfileImageUpload';
import ProfileValidation from '../components/ProfileValidation';
import api from '../api/axios';

export default function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [profileImage, setProfileImage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    department: '',
    position: '',
    address: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    date_of_birth: '',
    wedding_anniversary_date: '',
    gender: ''  // Add gender field
  });
  const [profileCompletion, setProfileCompletion] = useState(0);
  const [missingFields, setMissingFields] = useState([]);
  const [validationErrors, setValidationErrors] = useState({});
  const [isFormValid, setIsFormValid] = useState(false);

  // Use validation hook
  const validation = ProfileValidation({ 
    formData, 
    onValidationChange: (isValid, errors) => {
      setIsFormValid(isValid);
      setValidationErrors(errors);
    }
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      console.log('📋 Loading profile...');
      const response = await api.get('/employees/me/profile');
      console.log('✅ Profile response:', response.data);
      setProfile(response.data);
      
      // Load employee details if available
      if (response.data.employee) {
        console.log('👤 Employee data found:', response.data.employee);
        setFormData({
          first_name: response.data.employee.first_name || '',
          last_name: response.data.employee.last_name || '',
          phone: response.data.employee.phone || '',
          department: response.data.employee.department || '',
          position: response.data.employee.position || '',
          address: response.data.employee.address || '',
          emergency_contact_name: response.data.employee.emergency_contact_name || '',
          emergency_contact_phone: response.data.employee.emergency_contact_phone || '',
          date_of_birth: response.data.employee.date_of_birth ? response.data.employee.date_of_birth.split('T')[0] : '',
          wedding_anniversary_date: response.data.employee.wedding_anniversary_date ? response.data.employee.wedding_anniversary_date.split('T')[0] : '',
          gender: response.data.employee.gender || ''
        });
        
        // Load profile image from employee data
        if (response.data.employee.profile_image_url) {
          console.log('🖼️ Profile image URL found:', response.data.employee.profile_image_url);
          setProfileImage(response.data.employee.profile_image_url);
        }
      } else {
        console.log('⚠️ No employee data found in response');
      }

      // Load profile completion status
      try {
        const statusResponse = await api.get('/employees/me/profile-status');
        console.log('📊 Profile status response:', statusResponse.data);
        if (statusResponse.data.data) {
          setProfileCompletion(statusResponse.data.data.profile_completion || 0);
          setMissingFields(statusResponse.data.data.missing_fields || []);
        } else {
          setProfileCompletion(statusResponse.data.profile_completion || 0);
          setMissingFields(statusResponse.data.missing_fields || []);
        }
      } catch (statusError) {
        console.warn('⚠️ Error loading profile status:', statusError.message);
        // Set default values if status endpoint fails
        setProfileCompletion(0);
        setMissingFields([]);
      }
    } catch (error) {
      console.error('❌ Error loading profile:', error);
      console.error('Error details:', error.response?.data);
      alert('Failed to load profile. Please try again or contact support.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!isFormValid) {
      alert('Please fix the validation errors before saving.');
      return;
    }

    try {
      setLoading(true);
      const response = await api.put('/employees/me/profile', formData);
      alert('Profile updated successfully!');
      setEditing(false);
      
      // Update profile completion from response
      if (response.data.profile_completion) {
        setProfileCompletion(response.data.profile_completion);
      }
      
      loadProfile();
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      alert('Failed to update profile: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpdate = (imageData) => {
    console.log('Profile page: Image updated, dispatching event with:', imageData);
    // Update the profile image immediately
    setProfileImage(imageData);
    // Dispatch custom event to notify layout to refresh profile image
    window.dispatchEvent(new CustomEvent('profileImageUpdated', { detail: imageData }));
    console.log('Profile page: Event dispatched');
    // Also refresh profile to get updated image from server
    loadProfile();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Unable to load profile data</p>
          <button 
            onClick={loadProfile}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
              <p className="text-gray-600">Manage your personal information and profile photo</p>
              
              {/* Profile Completion Status */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Profile Completion</span>
                  <span className="text-sm font-medium text-gray-900">{profileCompletion}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      profileCompletion >= 80 ? 'bg-green-600' : 
                      profileCompletion >= 50 ? 'bg-yellow-600' : 'bg-red-600'
                    }`}
                    style={{ width: `${profileCompletion}%` }}
                  ></div>
                </div>
                {missingFields.length > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    Missing: {missingFields.join(', ').replace(/_/g, ' ')}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={() => setEditing(!editing)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              {editing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Profile Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                  {editing ? (
                    <div>
                      <input
                        type="text"
                        value={formData.first_name}
                        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                        className={validation.getFieldClassName('first_name', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                      />
                      {validation.hasError('first_name') && (
                        <p className="text-red-500 text-xs mt-1">{validation.getFieldError('first_name')}</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-900">{formData.first_name || 'Not set'}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                  {editing ? (
                    <div>
                      <input
                        type="text"
                        value={formData.last_name}
                        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                        className={validation.getFieldClassName('last_name', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                      />
                      {validation.hasError('last_name') && (
                        <p className="text-red-500 text-xs mt-1">{validation.getFieldError('last_name')}</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-900">{formData.last_name || 'Not set'}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <p className="text-gray-900">{profile?.email || user?.email || 'Not set'}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                {editing ? (
                  <div>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      className={validation.getFieldClassName('phone', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                      placeholder="Enter your phone number"
                    />
                    {validation.hasError('phone') && (
                      <p className="text-red-500 text-xs mt-1">{validation.getFieldError('phone')}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-900">{formData.phone || 'Not set'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department *</label>
                {editing ? (
                  <div>
                    <input
                      type="text"
                      value={formData.department}
                      onChange={(e) => setFormData({...formData, department: e.target.value})}
                      className={validation.getFieldClassName('department', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                    />
                    {validation.hasError('department') && (
                      <p className="text-red-500 text-xs mt-1">{validation.getFieldError('department')}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-900">{formData.department || 'Not set'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Position</label>
                {editing ? (
                  <input
                    type="text"
                    value={formData.position}
                    onChange={(e) => setFormData({...formData, position: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                ) : (
                  <p className="text-gray-900">{formData.position || 'Not set'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <p className="text-gray-900 capitalize">{profile?.role || user?.role || 'Employee'}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Gender *</label>
                {editing ? (
                  <div>
                    <select
                      value={formData.gender}
                      onChange={(e) => setFormData({...formData, gender: e.target.value})}
                      className={validation.getFieldClassName('gender', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                    >
                      <option value="">Select Gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                    {validation.hasError('gender') && (
                      <p className="text-red-500 text-xs mt-1">{validation.getFieldError('gender')}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">Required for maternity/paternity leave eligibility</p>
                  </div>
                ) : (
                  <p className="text-gray-900 capitalize">{formData.gender || 'Not set'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                {editing ? (
                  <div>
                    <input
                      type="date"
                      value={formData.date_of_birth}
                      onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                      className={validation.getFieldClassName('date_of_birth', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                    />
                    {validation.hasError('date_of_birth') && (
                      <p className="text-red-500 text-xs mt-1">{validation.getFieldError('date_of_birth')}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-900">{formData.date_of_birth || 'Not set'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Wedding Anniversary Date</label>
                {editing ? (
                  <div>
                    <input
                      type="date"
                      value={formData.wedding_anniversary_date}
                      onChange={(e) => setFormData({...formData, wedding_anniversary_date: e.target.value})}
                      className={validation.getFieldClassName('wedding_anniversary_date', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                    />
                    {validation.hasError('wedding_anniversary_date') && (
                      <p className="text-red-500 text-xs mt-1">{validation.getFieldError('wedding_anniversary_date')}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">Required for anniversary leave eligibility</p>
                  </div>
                ) : (
                  <p className="text-gray-900">{formData.wedding_anniversary_date || 'Not set'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                {editing ? (
                  <textarea
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your full address"
                  />
                ) : (
                  <p className="text-gray-900">{formData.address || 'Not set'}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Emergency Contact Name</label>
                  {editing ? (
                    <input
                      type="text"
                      value={formData.emergency_contact_name}
                      onChange={(e) => setFormData({...formData, emergency_contact_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Emergency contact name"
                    />
                  ) : (
                    <p className="text-gray-900">{formData.emergency_contact_name || 'Not set'}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Emergency Contact Phone</label>
                  {editing ? (
                    <div>
                      <input
                        type="tel"
                        value={formData.emergency_contact_phone}
                        onChange={(e) => setFormData({...formData, emergency_contact_phone: e.target.value})}
                        className={validation.getFieldClassName('emergency_contact_phone', 'w-full px-3 py-2 border rounded-lg focus:ring-2')}
                        placeholder="Emergency contact phone"
                      />
                      {validation.hasError('emergency_contact_phone') && (
                        <p className="text-red-500 text-xs mt-1">{validation.getFieldError('emergency_contact_phone')}</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-900">{formData.emergency_contact_phone || 'Not set'}</p>
                  )}
                </div>
              </div>

              {editing && (
                <div className="space-y-2">
                  <button
                    onClick={handleSave}
                    disabled={loading || !isFormValid}
                    className={`w-full py-2 rounded-lg transition ${
                      loading || !isFormValid 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : 'bg-green-600 hover:bg-green-700'
                    } text-white`}
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </button>
                  
                  {!isFormValid && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-red-800 text-sm font-medium">Please fix the following errors:</p>
                      <ul className="text-red-700 text-xs mt-1 list-disc list-inside">
                        {Object.values(validationErrors).map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Profile Image Upload */}
          <ProfileImageUpload 
            currentImage={profileImage}
            onImageUpdate={handleImageUpdate}
          />
        </div>

        {/* Important Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
          <div className="flex items-center">
            <svg className="h-5 w-5 text-blue-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-blue-800">Profile Photo Required for Attendance</h3>
              <p className="text-sm text-blue-700 mt-1">
                Please upload your profile photo to use the face recognition attendance system.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}