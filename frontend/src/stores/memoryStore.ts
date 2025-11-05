import { create } from 'zustand';
import type { Memory } from '../types/memory';

interface MemoryStore {
  memories: Memory[];
  isLoading: boolean;
  setMemories: (memories: Memory[]) => void;
  addMemory: (memory: Memory) => void;
  removeMemory: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useMemoryStore = create<MemoryStore>((set) => ({
  memories: [],
  isLoading: false,

  setMemories: (memories) => set({ memories }),

  addMemory: (memory) =>
    set((state) => ({ memories: [memory, ...state.memories] })),

  removeMemory: (id) =>
    set((state) => ({
      memories: state.memories.filter((m) => m.id !== id),
    })),

  setLoading: (loading) => set({ isLoading: loading }),
}));
