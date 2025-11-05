import React, { useEffect, useState } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { useMemoryStore } from '../stores/memoryStore';
import { memoryApi } from '../services/api';
import { Trash2, Tag, RefreshCw } from 'lucide-react';
import type { Memory } from '../types/memory';

const MemoryList: React.FC = () => {
  const { userId } = useSettingsStore();
  const { memories, setMemories, removeMemory, setLoading, isLoading } = useMemoryStore();
  const [error, setError] = useState<string | null>(null);

  const loadMemories = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await memoryApi.list(userId, 100);
      setMemories(data.memories || []);
    } catch (err) {
      console.error('Error loading memories:', err);
      setError('Failed to load memories');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, [userId]);

  const handleDelete = async (memoryId: string) => {
    if (!confirm('Are you sure you want to delete this memory?')) {
      return;
    }

    try {
      await memoryApi.delete(memoryId);
      removeMemory(memoryId);
    } catch (err) {
      console.error('Error deleting memory:', err);
      alert('Failed to delete memory');
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Stored Memories</h2>
            <p className="text-sm text-gray-500 mt-1">
              {memories.length} {memories.length === 1 ? 'memory' : 'memories'}
            </p>
          </div>
          <button
            onClick={loadMemories}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading memories...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">{error}</div>
        ) : memories.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No memories stored yet. Add some content to get started!
          </div>
        ) : (
          memories.map((memory) => (
            <div key={memory.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="text-gray-900 mb-2">
                    {memory.memory || memory.content}
                  </p>

                  {memory.metadata?.tags && memory.metadata.tags.length > 0 && (
                    <div className="flex items-center gap-2 mb-2">
                      <Tag size={14} className="text-gray-400" />
                      <div className="flex flex-wrap gap-1">
                        {memory.metadata.tags.map((tag: string) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>ID: {memory.id.substring(0, 8)}...</span>
                    {memory.created_at && (
                      <span>{formatDate(memory.created_at)}</span>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(memory.id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete memory"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MemoryList;
