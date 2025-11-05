import axios from 'axios';
import type {
  MemoryAddRequest,
  MemorySearchParams,
  Memory,
  TagSuggestion,
  TagAutocompleteParams,
  PopularTagsParams,
} from '../types/memory';
import type { ChatRequest, ChatResponse } from '../types/chat';
import type { OllamaModel, OllamaStatus } from '../types/ollama';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Memory APIs
export const memoryApi = {
  add: async (data: MemoryAddRequest) => {
    const response = await api.post('/api/memory/add', data);
    return response.data;
  },

  search: async (params: MemorySearchParams) => {
    const response = await api.get('/api/memory/search', { params });
    return response.data;
  },

  list: async (userId: string, limit = 50) => {
    const response = await api.get('/api/memory/list', {
      params: { user_id: userId, limit },
    });
    return response.data;
  },

  delete: async (memoryId: string) => {
    const response = await api.delete(`/api/memory/${memoryId}`);
    return response.data;
  },

  // Tag-related APIs
  suggestTags: async (content: string, maxTags = 5, language = 'auto'): Promise<TagSuggestion> => {
    const response = await api.post('/api/memory/suggest-tags', {
      content,
      max_tags: maxTags,
      language,
    });
    return response.data;
  },

  autocompleteTags: async (params: TagAutocompleteParams): Promise<{ tags: string[] }> => {
    const response = await api.get('/api/memory/tags/autocomplete', { params });
    return response.data;
  },

  getPopularTags: async (params?: PopularTagsParams): Promise<{ tags: Array<{ tag: string; count: number }> }> => {
    const response = await api.get('/api/memory/tags/popular', { params });
    return response.data;
  },
};

// Chat APIs
export const chatApi = {
  send: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/api/chat', data);
    return response.data;
  },
};

// Ollama APIs
export const ollamaApi = {
  listModels: async (): Promise<{ models: OllamaModel[] }> => {
    const response = await api.get('/api/ollama/models');
    return response.data;
  },

  checkStatus: async (): Promise<OllamaStatus> => {
    const response = await api.get('/api/ollama/status');
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;
