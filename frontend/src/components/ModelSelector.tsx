import React, { useEffect, useState } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { ollamaApi } from '../services/api';
import type { OllamaModel } from '../types/ollama';
import { RefreshCw, CheckCircle2 } from 'lucide-react';

const ModelSelector: React.FC = () => {
  const { selectedModel, setSelectedModel } = useSettingsStore();
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ollamaApi.listModels();
      setModels(data.models || []);
    } catch (err) {
      setError('Failed to load models. Is Ollama running?');
      console.error('Error loading models:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">LLM Model</h2>
        <button
          onClick={loadModels}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="space-y-2">
        {loading ? (
          <div className="text-center py-8 text-gray-500">
            Loading models...
          </div>
        ) : models.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No models available. Please pull models using Ollama CLI.
          </div>
        ) : (
          models.map((model) => (
            <button
              key={model.name}
              onClick={() => setSelectedModel(model.name)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                selectedModel === model.name
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">
                      {model.name}
                    </span>
                    {selectedModel === model.name && (
                      <CheckCircle2 size={18} className="text-primary-600" />
                    )}
                  </div>
                  {model.size && (
                    <span className="text-sm text-gray-500">{model.size}</span>
                  )}
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default ModelSelector;
