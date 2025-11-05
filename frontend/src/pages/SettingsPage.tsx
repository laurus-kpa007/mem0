import React from 'react';
import ModelSelector from '../components/ModelSelector';
import { useSettingsStore } from '../stores/settingsStore';
import { Save } from 'lucide-react';

const SettingsPage: React.FC = () => {
  const { userId, setUserId, useMemory, setUseMemory, memoryLimit, setMemoryLimit } =
    useSettingsStore();

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">Configure your Mem0 test program</p>
      </div>

      {/* Model Selection */}
      <ModelSelector />

      {/* User Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">User Settings</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              User ID
            </label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Enter your user ID"
            />
            <p className="text-xs text-gray-500 mt-1">
              Memories are stored per user ID. Change this to switch between different user contexts.
            </p>
          </div>
        </div>
      </div>

      {/* Memory Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Memory Settings</h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Use Memory in Chat</label>
              <p className="text-xs text-gray-500 mt-1">
                When enabled, the AI will use stored memories to answer your questions
              </p>
            </div>
            <button
              onClick={() => setUseMemory(!useMemory)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                useMemory ? 'bg-primary-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  useMemory ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Memory Search Limit: {memoryLimit}
            </label>
            <input
              type="range"
              min="1"
              max="20"
              value={memoryLimit}
              onChange={(e) => setMemoryLimit(parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Maximum number of related memories to retrieve for each chat message
            </p>
          </div>
        </div>
      </div>

      {/* Save Info */}
      <div className="bg-blue-50 rounded-lg p-4 flex items-start gap-3">
        <Save size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-900">
          <p className="font-medium">Auto-save enabled</p>
          <p className="text-blue-700 mt-1">
            All settings are automatically saved to your browser's local storage.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
