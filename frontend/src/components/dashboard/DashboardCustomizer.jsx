import { useState, useEffect } from 'react';
import api from '../../config/api';

export default function DashboardCustomizer({ onClose, onSave }) {
  const [layout, setLayout] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchLayout();
  }, []);

  const fetchLayout = async () => {
    try {
      const response = await api.get('/features/dashboard/layout');
      setLayout(response.data);
    } catch (error) {
      console.error('Error fetching layout:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleWidget = (widgetName) => {
    setLayout(prev => ({
      ...prev,
      active_widgets: prev.active_widgets.map(w =>
        w.name === widgetName ? { ...w, enabled: !w.enabled } : w
      )
    }));
  };

  const handleRemoveWidget = (widgetName) => {
    setLayout(prev => ({
      ...prev,
      active_widgets: prev.active_widgets.filter(w => w.name !== widgetName)
    }));
  };

  const handleAddWidget = (widgetName) => {
    if (!layout.active_widgets.find(w => w.name === widgetName)) {
      setLayout(prev => ({
        ...prev,
        active_widgets: [
          ...prev.active_widgets,
          { name: widgetName, position: prev.active_widgets.length, enabled: true, size: 'medium' }
        ]
      }));
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.post('/features/dashboard/layout', layout);
      onSave && onSave();
      onClose();
    } catch (error) {
      console.error('Error saving layout:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (window.confirm('Reset dashboard to default layout?')) {
      try {
        await api.post('/features/dashboard/reset');
        fetchLayout();
      } catch (error) {
        console.error('Error resetting dashboard:', error);
      }
    }
  };

  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  const activeWidgetNames = layout?.active_widgets?.map(w => w.name) || [];
  const availableWidgets = layout?.available_widgets || [];
  const unusedWidgets = availableWidgets.filter(w => !activeWidgetNames.includes(w));

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold">Customize Dashboard</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Active Widgets */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Active Widgets</h3>
            <div className="space-y-2">
              {layout?.active_widgets?.map(widget => (
                <div
                  key={widget.name}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={widget.enabled}
                      onChange={() => handleToggleWidget(widget.name)}
                      className="w-4 h-4"
                    />
                    <span className="font-medium capitalize">{widget.name.replace(/_/g, ' ')}</span>
                  </div>
                  <button
                    onClick={() => handleRemoveWidget(widget.name)}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Available Widgets */}
          {unusedWidgets.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Available Widgets</h3>
              <div className="space-y-2">
                {unusedWidgets.map(widget => (
                  <div
                    key={widget}
                    className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200"
                  >
                    <span className="font-medium capitalize">{widget.replace(/_/g, ' ')}</span>
                    <button
                      onClick={() => handleAddWidget(widget)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      Add
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="sticky bottom-0 bg-gray-50 border-t p-6 flex justify-end gap-3">
          <button
            onClick={handleReset}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
          >
            Reset to Default
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}
