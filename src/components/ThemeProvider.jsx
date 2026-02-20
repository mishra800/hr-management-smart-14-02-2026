import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  // Theme mode: 'light', 'dark', 'auto'
  const [mode, setMode] = useState(() => {
    const saved = localStorage.getItem('theme-mode');
    return saved || 'light';
  });

  // Color theme: 'blue', 'purple', 'green', 'orange', 'pink'
  const [colorTheme, setColorTheme] = useState(() => {
    const saved = localStorage.getItem('color-theme');
    return saved || 'blue';
  });

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    
    // Remove all theme classes
    root.classList.remove('light', 'dark');
    
    // Apply mode
    if (mode === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.add(prefersDark ? 'dark' : 'light');
    } else {
      root.classList.add(mode);
    }
    
    // Apply color theme
    root.setAttribute('data-theme', colorTheme);
    
    // Save to localStorage
    localStorage.setItem('theme-mode', mode);
    localStorage.setItem('color-theme', colorTheme);
  }, [mode, colorTheme]);

  const toggleMode = () => {
    setMode(prev => {
      console.log('Toggling mode from:', prev);
      let newMode;
      if (prev === 'light') newMode = 'dark';
      else if (prev === 'dark') newMode = 'auto';
      else newMode = 'light';
      console.log('New mode:', newMode);
      return newMode;
    });
  };

  const setThemeMode = (newMode) => {
    if (['light', 'dark', 'auto'].includes(newMode)) {
      setMode(newMode);
    }
  };

  const setThemeColor = (newColor) => {
    if (['blue', 'purple', 'green', 'orange', 'pink', 'red', 'indigo', 'teal'].includes(newColor)) {
      setColorTheme(newColor);
    }
  };

  const value = {
    mode,
    colorTheme,
    toggleMode,
    setThemeMode,
    setThemeColor,
    isDark: mode === 'dark' || (mode === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
