import { useState } from 'react';
import { Fingerprint, Clock, MapPin, AlertTriangle, CheckCircle, XCircle, Settings, Users } from 'lucide-react';

export default function AttendanceProcedures() {
  const [expandedSection, setExpandedSection] = useState(null);

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const procedures = [
    {
      id: 'biometric_system',
      title: 'Biometric System Usage',
      icon: Fingerprint,
      color: 'blue',
      description: 'Attendance capturing via authorized biometric system with Login and Logout recording',
      requirements: [
        'Use biometric system authorized by Dhanush management',
        'Ensure proper Login and Logout through biometric system',
        'Report biometric issues to HR team immediately',
        'Maintain proper record keeping without fail'
      ],
      implementation: [
        '✅ Face recognition system integrated',
        '✅ Photo capture for verification',
        '✅ Automatic login/logout recording',
        '✅ HR notification system for issues'
      ],
      troubleshooting: [
        'Cannot access biometric → Report to HR immediately',
        'Login/Logout issues → Contact HR for resolution',
        'System maintenance → HR will provide alternative method',
        'Face recognition failure → Use manual HR approval process'
      ]
    },
    {
      id: 'remote_locations',
      title: 'Remote Location Procedures',
      icon: MapPin,
      color: 'green',
      description: 'Attendance procedures for resources working from other locations',
      requirements: [
        'Shift timing changes require HR intimation with manager approval',
        'Official travel notification at least 1 day before with manager email approval',
        'HR database recording for all location changes',
        'Proper documentation and approval workflow'
      ],
      implementation: [
        '✅ Shift change request system',
        '✅ Travel notification workflow',
        '✅ Manager approval integration',
        '✅ HR database synchronization'
      ],
      procedures: [
        'Submit shift change request → Manager approval → HR confirmation',
        'Travel notification → Manager email approval → HR recording',
        'Location verification through GPS tracking',
        'Automatic attendance adjustment for approved changes'
      ]
    },
    {
      id: 'working_hours',
      title: 'Working Hours Requirements',
      icon: Clock,
      color: 'purple',
      description: 'Minimum working hours for Half Day and Full Day attendance',
      requirements: [
        'Half Day: Minimum 5 hours from login to logout',
        'Full Day: Minimum 9 hours from login to logout',
        'Same day login and logout required',
        'Proper time tracking and validation'
      ],
      implementation: [
        '✅ Automatic hour calculation',
        '✅ Half day (5 hours) validation',
        '✅ Full day (9 hours) validation',
        '✅ Real-time hour tracking'
      ],
      validation: [
        'System automatically calculates working hours',
        'Alerts for insufficient hours before logout',
        'Half day status assigned for 5+ hours',
        'Full day status assigned for 9+ hours'
      ]
    },
    {
      id: 'office_timings',
      title: 'Office Operating Particulars',
      icon: Settings,
      color: 'orange',
      description: 'Office timings, grace periods, and disciplinary actions',
      details: {
        office_hours: '10:00 AM – 7:00 PM (9 hours)',
        grace_period: '15 minutes up to 3 times per month',
        work_days: 'Monday – Friday (Saturday WFH/Office on need basis)',
        disciplinary_action: '4th late login onwards = Half day leave deduction'
      },
      implementation: [
        '✅ Office timing enforcement (10 AM - 7 PM)',
        '✅ Grace period tracking (15 min, 3 times/month)',
        '✅ Late login penalty system',
        '✅ Saturday flexible work arrangement'
      ],
      penalties: [
        'Late beyond grace period → Written manager permission required',
        '4th late login onwards → Half day leave deduction',
        'No leave balance → Leave without pay (LOP)',
        'Consecutive violations → Disciplinary action'
      ]
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 border-blue-200 text-blue-800',
      green: 'bg-green-50 border-green-200 text-green-800',
      purple: 'bg-purple-50 border-purple-200 text-purple-800',
      orange: 'bg-orange-50 border-orange-200 text-orange-800'
    };
    return colors[color] || colors.blue;
  };

  const getIconColorClasses = (color) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-100',
      green: 'text-green-600 bg-green-100',
      purple: 'text-purple-600 bg-purple-100',
      orange: 'text-orange-600 bg-orange-100'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Attendance Capturing Procedures
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Comprehensive procedures for attendance system usage and office operating particulars
        </p>
      </div>

      {/* Implementation Status Overview */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
        <div className="flex items-center space-x-3 mb-4">
          <CheckCircle className="w-6 h-6 text-green-600" />
          <h2 className="text-xl font-bold text-gray-900">Implementation Status</h2>
        </div>
        <div className="grid md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">✅</div>
            <p className="text-sm font-medium text-gray-900">Biometric System</p>
            <p className="text-xs text-gray-600">Face Recognition</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">✅</div>
            <p className="text-sm font-medium text-gray-900">Remote Procedures</p>
            <p className="text-xs text-gray-600">Travel & Shift Changes</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">✅</div>
            <p className="text-sm font-medium text-gray-900">Working Hours</p>
            <p className="text-xs text-gray-600">5h/9h Validation</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">✅</div>
            <p className="text-sm font-medium text-gray-900">Office Timings</p>
            <p className="text-xs text-gray-600">Grace & Penalties</p>
          </div>
        </div>
      </div>

      {/* Detailed Procedures */}
      <div className="space-y-6">
        {procedures.map((procedure) => {
          const Icon = procedure.icon;
          const isExpanded = expandedSection === procedure.id;
          
          return (
            <div key={procedure.id} className={`border rounded-lg ${getColorClasses(procedure.color)}`}>
              <button
                onClick={() => toggleSection(procedure.id)}
                className="w-full p-6 text-left flex items-center justify-between hover:bg-opacity-80 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getIconColorClasses(procedure.color)}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold">{procedure.title}</h3>
                    <p className="text-sm opacity-90 mt-1">{procedure.description}</p>
                  </div>
                </div>
                {isExpanded ? <XCircle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
              </button>
              
              {isExpanded && (
                <div className="px-6 pb-6 border-t border-opacity-20">
                  <div className="mt-4 space-y-6">
                    
                    {/* Requirements */}
                    {procedure.requirements && (
                      <div>
                        <h4 className="font-semibold mb-3 flex items-center">
                          <AlertTriangle className="w-4 h-4 mr-2" />
                          Policy Requirements
                        </h4>
                        <ul className="space-y-2">
                          {procedure.requirements.map((req, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="w-1.5 h-1.5 bg-current rounded-full mt-2 flex-shrink-0"></span>
                              <span className="text-sm">{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Office Details */}
                    {procedure.details && (
                      <div>
                        <h4 className="font-semibold mb-3 flex items-center">
                          <Clock className="w-4 h-4 mr-2" />
                          Office Configuration
                        </h4>
                        <div className="grid md:grid-cols-2 gap-4">
                          {Object.entries(procedure.details).map(([key, value]) => (
                            <div key={key} className="bg-white bg-opacity-50 rounded-lg p-3">
                              <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                                {key.replace('_', ' ')}
                              </span>
                              <p className="text-sm font-medium text-gray-900 mt-1">{value}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Implementation Status */}
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center">
                        <CheckCircle className="w-4 h-4 mr-2" />
                        System Implementation
                      </h4>
                      <ul className="space-y-2">
                        {procedure.implementation.map((impl, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <span className="text-green-600 mt-0.5">✓</span>
                            <span className="text-sm">{impl}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Procedures/Validation */}
                    {(procedure.procedures || procedure.validation || procedure.troubleshooting || procedure.penalties) && (
                      <div className="grid md:grid-cols-2 gap-6">
                        {procedure.procedures && (
                          <div>
                            <h4 className="font-semibold mb-3">Process Flow</h4>
                            <ul className="space-y-2">
                              {procedure.procedures.map((proc, index) => (
                                <li key={index} className="flex items-start space-x-2">
                                  <span className="w-1.5 h-1.5 bg-current rounded-full mt-2 flex-shrink-0"></span>
                                  <span className="text-sm">{proc}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {procedure.validation && (
                          <div>
                            <h4 className="font-semibold mb-3">Validation Rules</h4>
                            <ul className="space-y-2">
                              {procedure.validation.map((val, index) => (
                                <li key={index} className="flex items-start space-x-2">
                                  <span className="w-1.5 h-1.5 bg-current rounded-full mt-2 flex-shrink-0"></span>
                                  <span className="text-sm">{val}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {procedure.troubleshooting && (
                          <div>
                            <h4 className="font-semibold mb-3">Troubleshooting</h4>
                            <ul className="space-y-2">
                              {procedure.troubleshooting.map((trouble, index) => (
                                <li key={index} className="flex items-start space-x-2">
                                  <span className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
                                  <span className="text-sm">{trouble}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {procedure.penalties && (
                          <div>
                            <h4 className="font-semibold mb-3">Disciplinary Actions</h4>
                            <ul className="space-y-2">
                              {procedure.penalties.map((penalty, index) => (
                                <li key={index} className="flex items-start space-x-2">
                                  <span className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
                                  <span className="text-sm">{penalty}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Quick Reference Card */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Users className="w-5 h-5 mr-2 text-blue-600" />
          Quick Reference Guide
        </h3>
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Daily Attendance</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Use biometric system for login/logout</li>
              <li>• Office hours: 10 AM - 7 PM</li>
              <li>• Grace period: 15 min (3x/month)</li>
              <li>• Report issues to HR immediately</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Working Hours</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Half Day: Minimum 5 hours</li>
              <li>• Full Day: Minimum 9 hours</li>
              <li>• Same day login/logout required</li>
              <li>• Automatic hour calculation</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Special Cases</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Shift changes: Manager + HR approval</li>
              <li>• Travel: 1 day advance notice</li>
              <li>• Late login penalty: 4th onwards</li>
              <li>• Saturday: WFH/Office as needed</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}