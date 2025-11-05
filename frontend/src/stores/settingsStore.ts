import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsStore {
  userId: string;
  selectedModel: string;
  useMemory: boolean;
  memoryLimit: number;
  setUserId: (id: string) => void;
  setSelectedModel: (model: string) => void;
  setUseMemory: (use: boolean) => void;
  setMemoryLimit: (limit: number) => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      userId: 'user123',
      selectedModel: 'llama3.2:latest',
      useMemory: true,
      memoryLimit: 5,

      setUserId: (id) => set({ userId: id }),
      setSelectedModel: (model) => set({ selectedModel: model }),
      setUseMemory: (use) => set({ useMemory: use }),
      setMemoryLimit: (limit) => set({ memoryLimit: limit }),
    }),
    {
      name: 'mem0-settings',
    }
  )
);
