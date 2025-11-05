import React, { useState } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { memoryApi } from '../services/api';
import { Plus, X, Sparkles, Loader2 } from 'lucide-react';

interface MemoryInputProps {
  onMemoryAdded?: () => void;
}

const MemoryInput: React.FC<MemoryInputProps> = ({ onMemoryAdded }) => {
  const { userId } = useSettingsStore();
  const [content, setContent] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [suggestedTags, setSuggestedTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestingTags, setSuggestingTags] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSuggestTags = async () => {
    if (!content.trim()) {
      setMessage({ type: 'error', text: 'Please enter content first' });
      return;
    }

    setSuggestingTags(true);
    try {
      const result = await memoryApi.suggestTags(content, 5, 'auto');
      setSuggestedTags(result.tags);
      setMessage(null);
    } catch (error) {
      console.error('Error suggesting tags:', error);
      setMessage({ type: 'error', text: 'Failed to suggest tags' });
    } finally {
      setSuggestingTags(false);
    }
  };

  const handleAddTag = (tag: string) => {
    const normalizedTag = tag.trim().toLowerCase();
    if (normalizedTag && !tags.includes(normalizedTag)) {
      setTags([...tags, normalizedTag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleAddSuggestedTag = (tag: string) => {
    if (!tags.includes(tag)) {
      setTags([...tags, tag]);
      setSuggestedTags(suggestedTags.filter((t) => t !== tag));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      setMessage({ type: 'error', text: 'Please enter content' });
      return;
    }

    setLoading(true);
    setMessage(null);
    try {
      await memoryApi.add({
        content: content.trim(),
        user_id: userId,
        metadata: {
          tags: tags.length > 0 ? tags : undefined,
        },
      });
      setMessage({ type: 'success', text: 'Memory added successfully!' });
      setContent('');
      setTags([]);
      setSuggestedTags([]);
      if (onMemoryAdded) {
        onMemoryAdded();
      }
    } catch (error) {
      console.error('Error adding memory:', error);
      setMessage({ type: 'error', text: 'Failed to add memory' });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      handleAddTag(tagInput);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Add Memory</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Content Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter text to store in memory..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            rows={4}
            disabled={loading}
          />
        </div>

        {/* AI Tag Suggestion Button */}
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleSuggestTags}
            disabled={!content.trim() || suggestingTags || loading}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {suggestingTags ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Suggesting...
              </>
            ) : (
              <>
                <Sparkles size={16} />
                Suggest Tags
              </>
            )}
          </button>
        </div>

        {/* Suggested Tags */}
        {suggestedTags.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Suggested Tags (click to add)
            </label>
            <div className="flex flex-wrap gap-2">
              {suggestedTags.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => handleAddSuggestedTag(tag)}
                  className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200 transition-colors"
                >
                  + {tag}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Selected Tags */}
        {tags.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Selected Tags
            </label>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-primary-900"
                  >
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Manual Tag Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Add Tags Manually (press Enter)
          </label>
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a tag and press Enter..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={loading}
          />
        </div>

        {/* Message */}
        {message && (
          <div
            className={`p-3 rounded-lg text-sm ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !content.trim()}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {loading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Adding...
            </>
          ) : (
            <>
              <Plus size={18} />
              Add Memory
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default MemoryInput;
