import { useTheme } from './ThemeProvider';

export default function ThemeDemo() {
  const { mode, colorTheme, isDark } = useTheme();

  const colorExamples = [
    { name: 'Primary', light: 'bg-blue-600', dark: 'dark:bg-blue-500' },
    { name: 'Success', light: 'bg-green-600', dark: 'dark:bg-green-500' },
    { name: 'Warning', light: 'bg-yellow-600', dark: 'dark:bg-yellow-500' },
    { name: 'Error', light: 'bg-red-600', dark: 'dark:bg-red-500' },
    { name: 'Info', light: 'bg-cyan-600', dark: 'dark:bg-cyan-500' },
  ];

  return (
    <div className="space-y-6 p-6 bg-white dark:bg-gray-900 rounded-xl shadow-lg">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Theme Demo
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Current Mode: <span className="font-semibold">{mode}</span> | 
          Color Theme: <span className="font-semibold">{colorTheme}</span> | 
          Dark: <span className="font-semibold">{isDark ? 'Yes' : 'No'}</span>
        </p>
      </div>

      {/* Color Swatches */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Color Palette
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {colorExamples.map((color) => (
            <div key={color.name} className="text-center">
              <div className={`w-full h-20 rounded-lg ${color.light} ${color.dark} shadow-md`} />
              <p className="mt-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                {color.name}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Text Examples */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Typography
        </h3>
        <div className="space-y-2">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            Heading Text
          </p>
          <p className="text-lg text-gray-800 dark:text-gray-200">
            Primary Text
          </p>
          <p className="text-base text-gray-600 dark:text-gray-400">
            Secondary Text
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            Muted Text
          </p>
        </div>
      </div>

      {/* Button Examples */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Buttons
        </h3>
        <div className="flex flex-wrap gap-3">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-lg transition-colors">
            Primary
          </button>
          <button className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg transition-colors">
            Secondary
          </button>
          <button className="px-4 py-2 bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 text-white rounded-lg transition-colors">
            Success
          </button>
          <button className="px-4 py-2 bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 text-white rounded-lg transition-colors">
            Danger
          </button>
        </div>
      </div>

      {/* Card Example */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Cards
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
              Card Title
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              This is a card with adaptive colors for light and dark modes.
            </p>
          </div>
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
              Info Card
            </h4>
            <p className="text-sm text-blue-700 dark:text-blue-400">
              Colored card with semantic meaning.
            </p>
          </div>
          <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <h4 className="font-semibold text-green-900 dark:text-green-300 mb-2">
              Success Card
            </h4>
            <p className="text-sm text-green-700 dark:text-green-400">
              Success state with proper contrast.
            </p>
          </div>
        </div>
      </div>

      {/* Form Elements */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Form Elements
        </h3>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Text input"
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            <option>Select option</option>
            <option>Option 1</option>
            <option>Option 2</option>
          </select>
          <textarea
            placeholder="Textarea"
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Badges */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Badges
        </h3>
        <div className="flex flex-wrap gap-2">
          <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm font-medium rounded-full">
            Primary
          </span>
          <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-sm font-medium rounded-full">
            Success
          </span>
          <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-sm font-medium rounded-full">
            Warning
          </span>
          <span className="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-sm font-medium rounded-full">
            Error
          </span>
          <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm font-medium rounded-full">
            Neutral
          </span>
        </div>
      </div>
    </div>
  );
}
