import { create } from 'zustand';
import type { ChatMessage } from '../types/chat';

interface ChatStore {
  messages: ChatMessage[];
  sessionId: string;
  isLoading: boolean;
  addMessage: (message: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
  setSessionId: (id: string) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  sessionId: `session_${Date.now()}`,
  isLoading: false,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  setLoading: (loading) => set({ isLoading: loading }),

  clearMessages: () => set({ messages: [] }),

  setSessionId: (id) => set({ sessionId: id }),
}));
