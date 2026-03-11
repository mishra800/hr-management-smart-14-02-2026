import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Calendar, Users, Home, Star } from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/authcontext';

export default function LeaveCalendar() {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarData, setCalendarData] = useState({
    leaves: [],
    holidays: [],
    wfhRequests: [],
    working_days: 0
  });
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('month'); // month, team

  useEffect(() => {
    fetchCalendarData();
  }, [currentDate]);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();

      const requests = [
        api.get(`/leave/calendar?month=${month}&year=${year}`),
        api.get(`/leave/holidays?year=${year}`),
        api.get('/leave/requests'),
        api.get('/leave/wfh/requests')
      ];

      const responses = await Promise.all(requests);
      
      setCalendarData({
        ...responses[0].data?.data,
        holidays: responses[1].data?.data || [],
        leaves: responses[2].data?.data || [],
        wfhRequests: responses[3].data?.data || []
      });
    } catch (error) {
      console.error('Error fetching calendar data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getEventsForDate = (date) => {
    if (!date) return { leaves: [], holidays: [], wfh: [] };

    const dateStr = date.toISOString().split('T')[0];
    
    const leaves = calendarData.leaves.filter(leave => {
      const startDate = new Date(leave.start_date).toISOString().split('T')[0];
      const endDate = new Date(leave.end_date).toISOString().split('T')[0];
      return dateStr >= startDate && dateStr <= endDate;
    });

    const holidays = calendarData.holidays.filter(holiday => 
      holiday.date === dateStr
    );

    const wfh = calendarData.wfhRequests.filter(request => 
      request.date === dateStr && request.status === 'approved'
    );

    return { leaves, holidays, wfh };
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const isToday = (date) => {
    if (!date) return false;
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isWeekend = (date) => {
    if (!date) return false;
    const day = date.getDay();
    return day === 0 || day === 6; // Sunday or Saturday
  };

  const getDateClasses = (date, events) => {
    if (!date) return '';
    
    let classes = 'relative p-2 text-sm cursor-pointer hover:bg-gray-100 transition-colors ';
    
    if (isToday(date)) {
      classes += 'bg-blue-100 text-blue-900 font-semibold ';
    } else if (isWeekend(date)) {
      classes += 'text-gray-400 ';
    } else {
      classes += 'text-gray-900 ';
    }

    if (events.holidays.length > 0) {
      classes += 'bg-red-50 ';
    }

    return classes;
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="bg-gray-200 h-8 rounded w-1/3"></div>
        <div className="bg-gray-200 h-96 rounded"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-gray-900">Leave Calendar</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('month')}
              className={`px-3 py-1 text-sm rounded-md ${
                viewMode === 'month' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              My Calendar
            </button>
            {user?.role && ['admin', 'hr', 'manager'].includes(user.role) && (
              <button
                onClick={() => setViewMode('team')}
                className={`px-3 py-1 text-sm rounded-md ${
                  viewMode === 'team' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Team Calendar
              </button>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigateMonth(-1)}
              className="p-2 hover:bg-gray-100 rounded-md"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h3 className="text-lg font-semibold text-gray-900 min-w-[200px] text-center">
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </h3>
            <button
              onClick={() => navigateMonth(1)}
              className="p-2 hover:bg-gray-100 rounded-md"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <Calendar className="w-8 h-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Working Days</p>
              <p className="text-xl font-bold text-gray-900">{calendarData.working_days}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <Star className="w-8 h-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Holidays</p>
              <p className="text-xl font-bold text-gray-900">
                {calendarData.holidays.filter(h => 
                  new Date(h.date).getMonth() === currentDate.getMonth()
                ).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <Users className="w-8 h-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">My Leaves</p>
              <p className="text-xl font-bold text-gray-900">
                {calendarData.leaves.filter(l => 
                  new Date(l.start_date).getMonth() === currentDate.getMonth() ||
                  new Date(l.end_date).getMonth() === currentDate.getMonth()
                ).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <Home className="w-8 h-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">WFH Days</p>
              <p className="text-xl font-bold text-gray-900">
                {calendarData.wfhRequests.filter(w => 
                  new Date(w.date).getMonth() === currentDate.getMonth() &&
                  w.status === 'approved'
                ).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* Calendar Header */}
        <div className="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="p-3 text-center text-sm font-medium text-gray-700">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Body */}
        <div className="grid grid-cols-7">
          {days.map((date, index) => {
            const events = getEventsForDate(date);
            return (
              <div
                key={index}
                className={`min-h-[120px] border-r border-b border-gray-200 ${getDateClasses(date, events)}`}
              >
                {date && (
                  <>
                    <div className="font-medium mb-1">{date.getDate()}</div>
                    
                    {/* Events */}
                    <div className="space-y-1">
                      {events.holidays.map((holiday, idx) => (
                        <div
                          key={idx}
                          className="text-xs bg-red-100 text-red-700 px-1 py-0.5 rounded truncate"
                          title={holiday.name}
                        >
                          🎉 {holiday.name}
                        </div>
                      ))}
                      
                      {events.leaves.map((leave, idx) => (
                        <div
                          key={idx}
                          className={`text-xs px-1 py-0.5 rounded truncate ${
                            leave.status === 'approved' 
                              ? 'bg-green-100 text-green-700' 
                              : leave.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                          title={`${leave.leave_type} - ${leave.reason}`}
                        >
                          🏖️ {leave.leave_type}
                        </div>
                      ))}
                      
                      {events.wfh.map((wfh, idx) => (
                        <div
                          key={idx}
                          className="text-xs bg-purple-100 text-purple-700 px-1 py-0.5 rounded truncate"
                          title={`WFH - ${wfh.reason}`}
                        >
                          🏠 WFH
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-100 rounded"></div>
            <span>🎉 Holidays</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-100 rounded"></div>
            <span>🏖️ Approved Leave</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-100 rounded"></div>
            <span>⏳ Pending Leave</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-purple-100 rounded"></div>
            <span>🏠 Work From Home</span>
          </div>
        </div>
      </div>
    </div>
  );
}