import { useState, useEffect } from 'react';
import { useTheme } from './ThemeProvider';

export default function ThemeToggle() {
  const { mode, colorTheme, toggleMode, setThemeMode, setThemeColor } = useTheme();
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [previewColor, setPreviewColor] = useState(null);
  const [recentColors, setRecentColors] = useState(() => {
    const saved = localStorage.getItem('recent-colors');
    return saved ? JSON.parse(saved) : [];
  });

  const colorThemes = [
    { name: 'blue', label: 'Blue', color: 'bg-blue-600', ring: 'ring-blue-600' },
    { name: 'purple', label: 'Purple', color: 'bg-purple-600', ring: 'ring-purple-600' },
    { name: 'green', label: 'Green', color: 'bg-green-600', ring: 'ring-green-600' },
    { name: 'orange', label: 'Orange', color: 'bg-orange-600', ring: 'ring-orange-600' },
    { name: 'pink', label: 'Pink', color: 'bg-pink-600', ring: 'ring-pink-600' },
    { name: 'red', label: 'Red', color: 'bg-red-600', ring: 'ring-red-600' },
    { name: 'indigo', label: 'Indigo', color: 'bg-indigo-600', ring: 'ring-indigo-600' },
    { name: 'teal', label: 'Teal', color: 'bg-teal-600', ring: 'ring-teal-600' },
  ];

  const presets = [
    { id: 'professional', name: 'Professional', icon: '💼', mode: 'light', color: 'blue', description: 'Clean and corporate' },
    { id: 'creative', name: 'Creative', icon: '🎨', mode: 'light', color: 'purple', description: 'Vibrant and inspiring' },
    { id: 'nature', name: 'Nature', icon: '🌿', mode: 'light', color: 'green', description: 'Fresh and calming' },
    { id: 'nightOwl', name: 'Night Owl', icon: '🦉', mode: 'dark', color: 'indigo', description: 'Perfect for late nights' },
    { id: 'sunset', name: 'Sunset', icon: '🌅', mode: 'dark', color: 'orange', description: 'Warm and cozy' },
    { id: 'midnight', name: 'Midnight', icon: '🌙', mode: 'dark', color: 'blue', description: 'Deep and focused' },
  ];

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Ctrl/Cmd + Shift + T = Toggle theme mode
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        console.log('Keyboard shortcut: Toggle theme');
        toggleMode();
      }
      // Ctrl/Cmd + Shift + C = Open color picker
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        console.log('Keyboard shortcut: Open color picker');
        setShowColorPicker(true);
      }
      // Escape = Close color picker
      if (e.key === 'Escape' && showColorPicker) {
        setShowColorPicker(false);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [toggleMode, showColorPicker]);

  // Theme preview effect
  useEffect(() => {
    if (previewColor) {
      document.documentElement.setAttribute('data-theme-preview', previewColor);
    } else {
      document.documentElement.removeAttribute('data-theme-preview');
    }
  }, [previewColor]);

  const getModeIcon = () => {
    if (mode === 'light') return '☀️';
    if (mode === 'dark') return '🌙';
    return '🌓';
  };

  const getModeLabel = () => {
    if (mode === 'light') return 'Light';
    if (mode === 'dark') return 'Dark';
    return 'Auto';
  };

  const getDetailedModeLabel = () => {
    if (mode === 'light') return 'Light Mode - Click to switch to Dark';
    if (mode === 'dark') return 'Dark Mode - Click to switch to Auto';
    const systemMode = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'Dark' : 'Light';
    return `Auto Mode (System: ${systemMode}) - Click to switch to Light`;
  };

  const handleModeToggle = (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Theme toggle clicked, current mode:', mode);
    toggleMode();
  };

  const handleColorPickerToggle = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setShowColorPicker(!showColorPicker);
  };

  const handleColorSelect = (themeName) => {
    console.log('Color selected:', themeName);
    setPreviewColor(null); // Clear preview
    setThemeColor(themeName);
    setShowColorPicker(false);
    
    // Add to recent colors (max 3)
    const updated = [themeName, ...recentColors.filter(c => c !== themeName)].slice(0, 3);
    setRecentColors(updated);
    localStorage.setItem('recent-colors', JSON.stringify(updated));
  };

  const applyPreset = (preset) => {
    console.log('Applying preset:', preset.name);
    setThemeMode(preset.mode);
    setThemeColor(preset.color);
    setShowColorPicker(false);
    
    // Add to recent colors
    const updated = [preset.color, ...recentColors.filter(c => c !== preset.color)].slice(0, 3);
    setRecentColors(updated);
    localStorage.setItem('recent-colors', JSON.stringify(updated));
  };

  const handleColorHover = (themeName) => {
    setPreviewColor(themeName);
  };

  const handleColorLeave = () => {
    setPreviewColor(null);
  };

  return (
    <div className="flex items-center space-x-2 relative z-10">
      {/* Mode Toggle */}
      <button
        onClick={handleModeToggle}
        className="p-2.5 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer border border-gray-200 dark:border-gray-700"
        title={getDetailedModeLabel()}
        type="button"
        aria-label={`Switch theme mode (current: ${getModeLabel()})`}
      >
        <span className="text-xl block pointer-events-none select-none">{getModeIcon()}</span>
      </button>

      {/* Mode indicator for Auto mode */}
      {mode === 'auto' && (
        <span className="hidden md:inline-block text-xs text-gray-500 dark:text-gray-400 ml-1">
          (System: {window.matchMedia('(prefers-color-scheme: dark)').matches ? 'Dark' : 'Light'})
        </span>
      )}

      {/* Color Theme Picker */}
      <div className="relative">
        <button
          onClick={handleColorPickerToggle}
          className="p-2.5 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer border border-gray-200 dark:border-gray-700"
          title="Change color theme"
          type="button"
          aria-label="Open color theme picker"
        >
          <span className="text-xl block pointer-events-none select-none">🎨</span>
        </button>

        {showColorPicker && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setShowColorPicker(false)}
            />
            <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-xl shadow-xl ring-1 ring-black ring-opacity-5 z-50 p-4 border border-gray-200 dark:border-gray-700 max-h-[80vh] overflow-y-auto animate-slide-in-down">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                  Choose Color Theme
                </h3>
                <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                  ⌘⇧C
                </span>
              </div>

              {/* Recent Colors */}
              {recentColors.length > 0 && (
                <>
                  <div className="mb-3">
                    <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Recent
                    </h4>
                    <div className="flex gap-2">
                      {recentColors.map((colorName) => {
                        const theme = colorThemes.find(t => t.name === colorName);
                        if (!theme) return null;
                        return (
                          <button
                            key={colorName}
                            onClick={() => handleColorSelect(colorName)}
                            onMouseEnter={() => handleColorHover(colorName)}
                            onMouseLeave={handleColorLeave}
                            className={`relative p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all ${
                              colorTheme === colorName ? 'ring-2 ' + theme.ring : ''
                            }`}
                            title={theme.label}
                            type="button"
                          >
                            <div className={`w-8 h-8 rounded-full ${theme.color} shadow-md hover:scale-110 transition-transform`} />
                            {colorTheme === colorName && (
                              <div className="absolute -top-1 -right-1 text-green-600 dark:text-green-400">
                                <span className="text-xs font-bold">✓</span>
                              </div>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                  <div className="border-t border-gray-200 dark:border-gray-700 my-3" />
                </>
              )}

              {/* Theme Presets */}
              <div className="mb-3">
                <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Quick Presets
                </h4>
                <div className="grid grid-cols-3 gap-2">
                  {presets.map((preset) => (
                    <button
                      key={preset.id}
                      onClick={() => applyPreset(preset)}
                      className="flex flex-col items-center p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all group animate-scale-in"
                      title={preset.description}
                      type="button"
                    >
                      <span className="text-2xl mb-1">{preset.icon}</span>
                      <span className="text-xs font-medium text-gray-900 dark:text-white text-center">
                        {preset.name}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                        {preset.mode}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
              <div className="border-t border-gray-200 dark:border-gray-700 my-3" />

              {/* All Colors */}
              <div>
                <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  All Colors
                </h4>
                <div className="grid grid-cols-4 gap-2">
                  {colorThemes.map((theme) => (
                    <button
                      key={theme.name}
                      onClick={() => handleColorSelect(theme.name)}
                      onMouseEnter={() => handleColorHover(theme.name)}
                      onMouseLeave={handleColorLeave}
                      className={`group relative flex flex-col items-center justify-center p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all cursor-pointer ${
                        colorTheme === theme.name ? 'ring-2 ' + theme.ring : ''
                      } ${previewColor === theme.name ? 'ring-2 ring-gray-400 dark:ring-gray-500' : ''}`}
                      title={`${theme.label}${previewColor === theme.name ? ' (Preview)' : ''}`}
                      type="button"
                    >
                      <div className={`w-8 h-8 rounded-full ${theme.color} shadow-md group-hover:scale-110 transition-transform ${previewColor === theme.name ? 'scale-110' : ''}`} />
                      <span className="text-xs mt-1 text-gray-600 dark:text-gray-300">
                        {theme.label}
                      </span>
                      {colorTheme === theme.name && (
                        <div className="absolute top-1 right-1 text-green-600 dark:text-green-400">
                          <span className="text-xs font-bold">✓</span>
                        </div>
                      )}
                      {previewColor === theme.name && colorTheme !== theme.name && (
                        <div className="absolute top-1 right-1 text-blue-600 dark:text-blue-400">
                          <span className="text-xs font-bold">👁</span>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  {previewColor ? (
                    <p className="text-xs text-blue-600 dark:text-blue-400 text-center font-medium">
                      👁 Previewing: <span className="capitalize">{previewColor}</span>
                    </p>
                  ) : (
                    <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                      Current: <span className="font-semibold capitalize">{colorTheme}</span>
                    </p>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
