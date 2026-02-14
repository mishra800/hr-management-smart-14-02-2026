# HR System - Theme & Color Guide

## Overview
The HR System now supports multiple color themes and dark mode for better user experience and accessibility.

## Features

### 1. Theme Modes
- **Light Mode** (☀️): Clean white/gray backgrounds, perfect for bright environments
- **Dark Mode** (🌙): Black/dark gray backgrounds, easier on the eyes in low-light
- **Auto Mode** (🌓): Automatically switches based on system preferences

### 2. Color Themes
Choose from 8 beautiful color themes:
- **Blue** (Default): Professional and trustworthy
- **Purple**: Creative and modern
- **Green**: Fresh and growth-oriented
- **Orange**: Energetic and warm
- **Pink**: Friendly and approachable
- **Red**: Bold and attention-grabbing
- **Indigo**: Deep and sophisticated
- **Teal**: Calm and balanced

## How to Use

### Switching Theme Mode
1. Click the sun/moon icon (☀️/🌙) in the top navigation bar
2. Cycles through: Light → Dark → Auto → Light

### Changing Color Theme
1. Click the palette icon (🎨) in the top navigation bar
2. Select your preferred color from the dropdown
3. The theme applies instantly across the entire application

## Technical Implementation

### Theme Provider
The `ThemeProvider` component wraps the entire application and manages:
- Theme mode state (light/dark/auto)
- Color theme selection
- LocalStorage persistence
- System preference detection

### Usage in Components
```jsx
import { useTheme } from './components/ThemeProvider';

function MyComponent() {
  const { mode, colorTheme, isDark, toggleMode, setThemeColor } = useTheme();
  
  return (
    <div className={`bg-white dark:bg-gray-900 text-gray-900 dark:text-white`}>
      Current mode: {mode}
      Current color: {colorTheme}
    </div>
  );
}
```

### Tailwind Dark Mode Classes
Use Tailwind's `dark:` prefix for dark mode styles:
```jsx
<div className="bg-white dark:bg-gray-900">
  <h1 className="text-gray-900 dark:text-white">Title</h1>
  <p className="text-gray-600 dark:text-gray-300">Content</p>
</div>
```

## Color Palette

### Light Mode
- Background: `gray-50` to `gray-100`
- Cards: `white` with `gray-200` borders
- Text: `gray-900` (primary), `gray-600` (secondary)

### Dark Mode
- Background: `gray-900` to `gray-800`
- Cards: `gray-800` with `gray-700` borders
- Text: `white` (primary), `gray-300` (secondary)

## Accessibility

### Contrast Ratios
All color combinations meet WCAG AA standards:
- Light mode: 4.5:1 minimum for normal text
- Dark mode: 4.5:1 minimum for normal text

### Reduced Motion
Respects `prefers-reduced-motion` system setting:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Best Practices

### 1. Always Support Both Modes
When adding new components, always include dark mode styles:
```jsx
// ✅ Good
<button className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600">

// ❌ Bad
<button className="bg-blue-600 hover:bg-blue-700">
```

### 2. Use Semantic Colors
Prefer semantic color names over specific shades:
```jsx
// ✅ Good
<div className="bg-white dark:bg-gray-900">

// ❌ Bad
<div className="bg-gray-50 dark:bg-gray-850">
```

### 3. Test in Both Modes
Always test your UI in both light and dark modes to ensure readability.

### 4. Respect User Preferences
The theme persists in localStorage and respects system preferences in auto mode.

## Customization

### Adding New Color Themes
Edit `frontend/src/components/ThemeToggle.jsx`:
```javascript
const colorThemes = [
  // Add your new theme
  { name: 'cyan', label: 'Cyan', color: 'bg-cyan-600', ring: 'ring-cyan-600' },
];
```

### Modifying Theme Colors
Edit `frontend/src/styles/design-tokens.css` to adjust color values:
```css
:root {
  --brand-primary-600: #2563eb; /* Adjust this */
}
```

## Browser Support
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- IE11: Not supported (uses modern CSS features)

## Performance
- Theme switching is instant (no page reload)
- Preferences saved to localStorage
- Minimal JavaScript overhead
- CSS-based transitions for smooth changes

## Future Enhancements
- [ ] Custom color picker for brand colors
- [ ] High contrast mode for accessibility
- [ ] Theme scheduling (auto-switch at specific times)
- [ ] Per-page theme overrides
- [ ] Export/import theme settings
