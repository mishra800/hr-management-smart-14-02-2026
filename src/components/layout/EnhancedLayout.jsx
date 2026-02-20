import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/authcontext';
import { 
  Menu, X, Search, User, ChevronDown, LogOut, Settings,
  Maximize2, Minimize2
} from 'lucide-react';
import Button from '../ui/Button.jsx';
import Badge from '../ui/Badge.jsx';
import NotificationCenter from '../NotificationCenter.jsx';
import EnhancedAIAssistant from './EnhancedAIAssistant.jsx';
import ThemeToggle from '../ThemeToggle.jsx';

const EnhancedLayout = () => {
  const { logout, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Layout state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchOpen, setSearchOpen] = useState(false);

  const role = user?.role || 'employee';

  // Enhanced navigation with better organization
  const navigationSections = [
    {
      title: 'Overview',
      items: [
        { 
          name: 'Dashboard', 
          href: '/dashboard', 
          icon: '📊', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Main dashboard overview'
        }
      ]
    },
    {
      title: 'Administration',
      items: [
        { 
          name: 'Super Admin', 
          href: '/dashboard/superadmin', 
          icon: '🔐', 
          roles: ['admin'],
          description: 'System administration and role management'
        }
      ]
    },
    {
      title: 'People Management',
      items: [
        { 
          name: 'Employees', 
          href: '/dashboard/employees', 
          icon: '👥', 
          roles: ['admin', 'hr', 'manager'],
          description: 'Employee directory and management'
        },
        { 
          name: 'Recruitment', 
          href: '/dashboard/recruitment', 
          icon: '🎯', 
          roles: ['admin', 'hr'],
          description: 'Hiring and recruitment pipeline'
        },
        { 
          name: 'Onboarding', 
          href: '/dashboard/onboarding', 
          icon: '🚀', 
          roles: ['admin', 'hr'],
          description: 'New employee onboarding'
        }
      ]
    },
    {
      title: 'Workforce',
      items: [
        { 
          name: 'Attendance', 
          href: '/dashboard/attendance', 
          icon: '⏰', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Time tracking and attendance'
        },
        { 
          name: 'Leave Management', 
          href: '/dashboard/leave', 
          icon: '🏖️', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Leave requests and approvals'
        },
        { 
          name: 'WFH Requests', 
          href: '/dashboard/wfh-request', 
          icon: '🏠', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Work from home requests'
        },
        { 
          name: 'Performance', 
          href: '/dashboard/performance', 
          icon: '⭐', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Performance reviews and goals'
        }
      ]
    },
    {
      title: 'Development',
      items: [
        { 
          name: 'Learning', 
          href: '/dashboard/learning', 
          icon: '📚', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Training and development programs'
        },
        { 
          name: 'Career', 
          href: '/dashboard/career', 
          icon: '🎯', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Career development and planning'
        },
        { 
          name: 'Engagement', 
          href: '/dashboard/engagement', 
          icon: '❤️', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Employee engagement activities'
        }
      ]
    },
    {
      title: 'Operations',
      items: [
        { 
          name: 'Payroll', 
          href: '/dashboard/payroll', 
          icon: '💰', 
          roles: ['admin', 'hr'],
          description: 'Payroll management and processing'
        },
        { 
          name: 'Assets', 
          href: '/dashboard/assets', 
          icon: '💻', 
          roles: ['admin', 'hr', 'assets_team', 'employee'],
          description: 'IT assets and equipment'
        },
        { 
          name: 'Documents', 
          href: '/dashboard/documents', 
          icon: '📄', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Document management system'
        },
        { 
          name: 'Analytics', 
          href: '/dashboard/analysis', 
          icon: '📈', 
          roles: ['admin', 'hr', 'manager'],
          description: 'Reports and business analytics'
        }
      ]
    },
    {
      title: 'Communication',
      items: [
        { 
          name: 'Announcements', 
          href: '/dashboard/announcements', 
          icon: '📢', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Company announcements'
        },
        { 
          name: 'Meetings', 
          href: '/dashboard/meetings', 
          icon: '🤝', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Meeting rooms and scheduling'
        },
        { 
          name: 'Notifications', 
          href: '/dashboard/notifications', 
          icon: '🔔', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Notification center'
        }
      ]
    },
    {
      title: 'Support',
      items: [
        { 
          name: 'Help Center', 
          href: '/dashboard/help', 
          icon: '❓', 
          roles: ['admin', 'hr', 'manager', 'employee'],
          description: 'Help and support resources'
        }
      ]
    }
  ];

  // Filter navigation based on user role
  const getFilteredNavigation = () => {
    return navigationSections.map(section => ({
      ...section,
      items: section.items.filter(item => item.roles.includes(role))
    })).filter(section => section.items.length > 0);
  };

  // Global search functionality
  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    // Mock search results - replace with actual API call
    const mockResults = [
      { type: 'employee', title: 'John Doe', subtitle: 'Software Engineer', href: '/dashboard/employees/1' },
      { type: 'page', title: 'Attendance Dashboard', subtitle: 'View attendance records', href: '/dashboard/attendance' },
      { type: 'document', title: 'Employee Handbook', subtitle: 'HR Policy Document', href: '/dashboard/documents/handbook' }
    ];

    setSearchResults(mockResults.filter(item => 
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.subtitle.toLowerCase().includes(query.toLowerCase())
    ));
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Cmd/Ctrl + K for search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
      // Escape to close search
      if (e.key === 'Escape') {
        setSearchOpen(false);
        setSearchQuery('');
        setSearchResults([]);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = () => {
      setUserMenuOpen(false);
      setSearchOpen(false);
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setFullscreen(true);
    } else {
      document.exitFullscreen();
      setFullscreen(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700
        transition-all duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        ${sidebarCollapsed ? 'w-16' : 'w-64'}
        lg:translate-x-0
      `}>
        {/* Sidebar header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          {!sidebarCollapsed && (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">HR</span>
              </div>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">HRSystem</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="hidden lg:flex"
          >
            <Menu className="w-4 h-4" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-6 overflow-y-auto">
          {getFilteredNavigation().map((section) => (
            <div key={section.title}>
              {!sidebarCollapsed && (
                <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {section.title}
                </h3>
              )}
              <div className="mt-2 space-y-1">
                {section.items.map((item) => {
                  const isActive = location.pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`
                        group flex items-center px-3 py-2 text-sm font-medium rounded-lg
                        transition-colors duration-200
                        ${isActive 
                          ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border-r-2 border-blue-700 dark:border-blue-500' 
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
                        }
                      `}
                      title={sidebarCollapsed ? item.name : ''}
                    >
                      <span className="text-lg mr-3">{item.icon}</span>
                      {!sidebarCollapsed && (
                        <>
                          <span className="flex-1">{item.name}</span>
                          {item.badge && (
                            <Badge variant="primary" size="sm">
                              {item.badge}
                            </Badge>
                          )}
                        </>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Sidebar footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          {!sidebarCollapsed && (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-300 dark:bg-gray-700 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-gray-600 dark:text-gray-300" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user?.name || user?.email}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{role}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main content */}
      <div className={`
        flex flex-col min-h-screen transition-all duration-300
        ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64'}
      `}>
        {/* Top navigation */}
        <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 h-16 flex items-center justify-between px-4 lg:px-6 transition-colors duration-200">
          {/* Left side */}
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </Button>

            {/* Search */}
            <div className="relative">
              <div className="flex items-center">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 z-10" />
                <input
                  type="text"
                  placeholder="Search... (⌘K)"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    handleSearch(e.target.value);
                  }}
                  onFocus={() => setSearchOpen(true)}
                  className="w-64 pl-10 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
              </div>

              {/* Search results */}
              {searchOpen && searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                  {searchResults.map((result, index) => (
                    <Link
                      key={index}
                      to={result.href}
                      className="block px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition-colors"
                      onClick={() => {
                        setSearchOpen(false);
                        setSearchQuery('');
                        setSearchResults([]);
                      }}
                    >
                      <div className="font-medium text-gray-900 dark:text-white">{result.title}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{result.subtitle}</div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-3">
            {/* Fullscreen toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleFullscreen}
              className="hidden md:flex"
            >
              {fullscreen ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </Button>

            {/* Theme Toggle - Using our new ThemeToggle component */}
            <ThemeToggle />

            {/* Notifications */}
            <NotificationCenter />

            {/* User menu */}
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  setUserMenuOpen(!userMenuOpen);
                }}
                className="flex items-center space-x-2"
              >
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-gray-600" />
                </div>
                <ChevronDown className="w-4 h-4" />
              </Button>

              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                  <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {user?.name || user?.email}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{role}</p>
                  </div>
                  <div className="py-1">
                    <Link
                      to="/dashboard/profile"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <User className="w-4 h-4 mr-3" />
                      Profile
                    </Link>
                    <Link
                      to="/dashboard/settings"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <Settings className="w-4 h-4 mr-3" />
                      Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <LogOut className="w-4 h-4 mr-3" />
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>

      {/* Enhanced AI Assistant */}
      <EnhancedAIAssistant />
    </div>
  );
};

export default EnhancedLayout;