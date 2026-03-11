import { useState } from 'react';
import { BookOpen, Users, Clock, Heart, Target, ChevronDown, ChevronUp, FileText, AlertTriangle } from 'lucide-react';

export default function PolicyDefinitions() {
  const [expandedSection, setExpandedSection] = useState(null);

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const definitions = [
    {
      id: 'attendance',
      title: 'Attendance',
      icon: Clock,
      color: 'blue',
      definition: 'Attendance is the concept of resources, who are expected to be present at work, on time every day.',
      details: [
        'Expected presence during normal working hours (10:00 AM - 7:00 PM)',
        'Punctuality is essential for team coordination and productivity',
        'Grace period of 15 minutes allowed (maximum 3 times per month)',
        'Regular attendance ensures smooth operations and client satisfaction'
      ],
      implementation: [
        'Real-time attendance tracking system',
        'Biometric/face recognition check-in/out',
        'Grace period monitoring and alerts',
        'Attendance reports and analytics'
      ]
    },
    {
      id: 'absenteeism',
      title: 'Absenteeism',
      icon: Users,
      color: 'red',
      definition: 'Absenteeism generally refers to an employee being absent from work during normal working days/hours.',
      details: [
        'Unplanned absence from scheduled work days',
        'Impacts team productivity and client deliverables',
        'Requires proper communication and documentation',
        'Excessive absenteeism may lead to disciplinary action'
      ],
      implementation: [
        'Absence tracking and pattern analysis',
        'Automated notifications for unauthorized absence',
        'Escalation process for consecutive absences (3+ days)',
        'Integration with leave management system'
      ]
    },
    {
      id: 'leave',
      title: 'Leave',
      icon: BookOpen,
      color: 'green',
      definition: 'Leave is a provision to stay away from work with prior approval from the approving authorities. It may be granted for casual purposes or planned activity, on medical grounds, or in any other emergency conditions.',
      details: [
        'Prior approval required from designated authorities',
        'Available for casual, medical, and emergency purposes',
        'Planned activities and personal commitments',
        'Maintains work-life balance while ensuring business continuity'
      ],
      implementation: [
        'Digital leave request and approval system',
        'Multiple leave types (CL, SL, AL, ML, PL, etc.)',
        'Automated workflow with manager/HR approval',
        'Leave balance tracking and notifications'
      ]
    }
  ];

  const objectives = [
    {
      id: 'attendance_policy',
      title: 'Attendance Policy Objective',
      icon: Target,
      color: 'purple',
      objective: 'Dhanush Group is encouraging all its resources to attend to regular duties within the specified time. The main objective is to promote the efficient operations of the company\'s productivity and client satisfaction.',
      keyPoints: [
        'Encourage regular attendance within specified time',
        'Promote efficient company operations',
        'Enhance overall productivity',
        'Ensure client satisfaction through reliable service delivery'
      ],
      implementation: [
        'Flexible working hours with core time requirements',
        'Performance metrics tied to attendance consistency',
        'Client project scheduling based on team availability',
        'Productivity tracking and improvement initiatives'
      ]
    },
    {
      id: 'leave_policy',
      title: 'Leave Policy Objective',
      icon: Heart,
      color: 'pink',
      objective: 'Dhanush group believes that its resources should have opportunities to enjoy time, which is away from work to balance their family & professional life. The company gives the opportunity to its resource on genuine reasons to spend time with their family during the leave and take care of their personal needs.',
      keyPoints: [
        'Work-life balance is a fundamental right',
        'Family time is essential for employee well-being',
        'Personal needs should be accommodated',
        'Genuine reasons for leave are always considered'
      ],
      implementation: [
        'Generous leave allocation (18 CL + other leaves)',
        'Family-friendly policies (ML, PL, Birthday leaves)',
        'Emergency leave provisions for urgent situations',
        'Flexible leave scheduling to accommodate personal needs'
      ]
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 border-blue-200 text-blue-800',
      red: 'bg-red-50 border-red-200 text-red-800',
      green: 'bg-green-50 border-green-200 text-green-800',
      purple: 'bg-purple-50 border-purple-200 text-purple-800',
      pink: 'bg-pink-50 border-pink-200 text-pink-800',
      orange: 'bg-orange-50 border-orange-200 text-orange-800'
    };
    return colors[color] || colors.blue;
  };

  const getIconColorClasses = (color) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-100',
      red: 'text-red-600 bg-red-100',
      green: 'text-green-600 bg-green-100',
      purple: 'text-purple-600 bg-purple-100',
      pink: 'text-pink-600 bg-pink-100',
      orange: 'text-orange-600 bg-orange-100'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Dhanush Group Attendance & Leave Policy
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Understanding our policy definitions and objectives for effective workforce management
        </p>
      </div>

      {/* Definitions Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <BookOpen className="w-6 h-6 mr-2 text-blue-600" />
          Policy Definitions
        </h2>
        
        <div className="grid gap-6">
          {definitions.map((item) => {
            const Icon = item.icon;
            const isExpanded = expandedSection === item.id;
            
            return (
              <div key={item.id} className={`border rounded-lg ${getColorClasses(item.color)}`}>
                <button
                  onClick={() => toggleSection(item.id)}
                  className="w-full p-6 text-left flex items-center justify-between hover:bg-opacity-80 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getIconColorClasses(item.color)}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold">{item.title}</h3>
                      <p className="text-sm opacity-90 mt-1">{item.definition}</p>
                    </div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
                
                {isExpanded && (
                  <div className="px-6 pb-6 border-t border-opacity-20">
                    <div className="grid md:grid-cols-2 gap-6 mt-4">
                      <div>
                        <h4 className="font-semibold mb-3">Key Details</h4>
                        <ul className="space-y-2">
                          {item.details.map((detail, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="w-1.5 h-1.5 bg-current rounded-full mt-2 flex-shrink-0"></span>
                              <span className="text-sm">{detail}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-3">System Implementation</h4>
                        <ul className="space-y-2">
                          {item.implementation.map((impl, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="w-1.5 h-1.5 bg-current rounded-full mt-2 flex-shrink-0"></span>
                              <span className="text-sm">{impl}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Objectives Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <Target className="w-6 h-6 mr-2 text-purple-600" />
          Policy Objectives
        </h2>
        
        <div className="grid gap-6">
          {objectives.map((item) => {
            const Icon = item.icon;
            const isExpanded = expandedSection === item.id;
            
            return (
              <div key={item.id} className={`border rounded-lg ${getColorClasses(item.color)}`}>
                <button
                  onClick={() => toggleSection(item.id)}
                  className="w-full p-6 text-left flex items-center justify-between hover:bg-opacity-80 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getIconColorClasses(item.color)}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold">{item.title}</h3>
                      <p className="text-sm opacity-90 mt-1 line-clamp-2">{item.objective}</p>
                    </div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
                
                {isExpanded && (
                  <div className="px-6 pb-6 border-t border-opacity-20">
                    <div className="mt-4">
                      <p className="text-sm mb-4 leading-relaxed">{item.objective}</p>
                      
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-semibold mb-3">Key Focus Areas</h4>
                          <ul className="space-y-2">
                            {item.keyPoints.map((point, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <span className="w-1.5 h-1.5 bg-current rounded-full mt-2 flex-shrink-0"></span>
                                <span className="text-sm">{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold mb-3">How We Achieve This</h4>
                          <ul className="space-y-2">
                            {item.implementation.map((impl, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <span className="w-1.5 h-1.5 bg-current rounded-full mt-2 flex-shrink-0"></span>
                                <span className="text-sm">{impl}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Leave Norms Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <FileText className="w-6 h-6 mr-2 text-orange-600" />
          Norms for Availing Leaves
        </h2>
        
        <div className="bg-orange-50 border border-orange-200 rounded-lg">
          <button
            onClick={() => toggleSection('leave_norms')}
            className="w-full p-6 text-left flex items-center justify-between hover:bg-orange-100 transition-colors"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-orange-100 text-orange-600">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-orange-800">Leave Application Guidelines & Rules</h3>
                <p className="text-sm text-orange-700 mt-1">Important norms and procedures for leave management</p>
              </div>
            </div>
            {expandedSection === 'leave_norms' ? <ChevronUp className="w-5 h-5 text-orange-600" /> : <ChevronDown className="w-5 h-5 text-orange-600" />}
          </button>
          
          {expandedSection === 'leave_norms' && (
            <div className="px-6 pb-6 border-t border-orange-200">
              <div className="mt-4 space-y-6">
                
                {/* Leave Limits */}
                <div className="bg-white rounded-lg p-4 border border-orange-100">
                  <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
                    <Clock className="w-4 h-4 mr-2" />
                    Leave Limits & Medical Emergencies
                  </h4>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Maximum <strong>three Casual leaves</strong> can be availed at a stretch</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>In case of <strong>medical emergencies</strong>, leaves can be availed based on eligible leave balance</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span><strong>Medical reports</strong> issued by certified doctor must be submitted to HR team for validation and records</span>
                    </li>
                  </ul>
                </div>

                {/* Leave Clubbing */}
                <div className="bg-white rounded-lg p-4 border border-orange-100">
                  <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Leave Clubbing with Holidays
                  </h4>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Clubbing of leaves with <strong>Weekly offs / Holidays is strongly discouraged</strong> to prevent work delivery lapses</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>If leaves are availed continuously before and after a holiday/weekly off, the <strong>holiday/weekly off will also be considered as leave</strong></span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>In absence of leave balance, it will be considered as <strong>leave without pay</strong></span>
                    </li>
                  </ul>
                </div>

                {/* Application Process */}
                <div className="bg-white rounded-lg p-4 border border-orange-100">
                  <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    Leave Application Process
                  </h4>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Leaves should be applied through <strong>SMHR</strong> and approved by reporting manager <strong>at least 2 days before</strong> availing leave</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>For <strong>emergency leaves</strong>: Written approval (mail/Skype) from manager is mandatory</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Emergency leaves must be applied in SMHR <strong>within 2 days</strong> of returning to office</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Leaves not applied in SMHR will be treated as <strong>unauthorized absence / Leave without Pay</strong></span>
                    </li>
                  </ul>
                </div>

                {/* Special Conditions */}
                <div className="bg-white rounded-lg p-4 border border-orange-100">
                  <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
                    <Users className="w-4 h-4 mr-2" />
                    Special Conditions & Restrictions
                  </h4>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Employees who submit resignation will <strong>not be entitled to avail leaves during notice period</strong></span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Issues with SMHR application should be <strong>immediately reported to HR</strong></span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Alternative: Apply through <strong>email to reporting manager and HR</strong> when SMHR is unavailable</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Leaves not utilized during calendar year will <strong>lapse automatically</strong> after year completion</span>
                    </li>
                  </ul>
                </div>

                {/* Travel & Communication */}
                <div className="bg-white rounded-lg p-4 border border-orange-100">
                  <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
                    <Target className="w-4 h-4 mr-2" />
                    Travel & Communication Requirements
                  </h4>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Employees must inform reporting manager and HR when <strong>traveling out of station during Saturdays & Holidays</strong></span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                      <span>Prior email notification required before <strong>going out of station with team</strong></span>
                    </li>
                  </ul>
                </div>

                {/* Disciplinary Actions */}
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <h4 className="font-semibold text-red-900 mb-3 flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Disciplinary Actions
                  </h4>
                  <div className="bg-red-100 rounded-lg p-3">
                    <p className="text-sm text-red-800 font-medium">
                      ⚠️ <strong>Important:</strong> Violation of any of the above guidelines will lead to initiation of disciplinary actions against the resource.
                    </p>
                  </div>
                </div>

              </div>
            </div>
          )}
        </div>
      </div>

      {/* Implementation Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8 border border-blue-200">
        <h3 className="text-xl font-bold text-gray-900 mb-4">System Implementation Summary</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-blue-900 mb-3">Attendance Management</h4>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>✓ Real-time attendance tracking</li>
              <li>✓ Grace period monitoring</li>
              <li>✓ Absenteeism pattern analysis</li>
              <li>✓ Productivity correlation tracking</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-purple-900 mb-3">Leave Management</h4>
            <ul className="space-y-2 text-sm text-purple-800">
              <li>✓ Work-life balance focused policies</li>
              <li>✓ Family-friendly leave options</li>
              <li>✓ Emergency leave provisions</li>
              <li>✓ Automated approval workflows</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}