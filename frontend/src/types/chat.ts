import { Memory } from './memory';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  related_memories?: Memory[];
}

export interface ChatRequest {
  message: string;
  user_id: string;
  session_id: string;
  model: string;
  use_memory: boolean;
  memory_limit: number;
}

export interface ChatResponse {
  response: string;
  related_memories: Memory[];
  model_used: string;
  timestamp: string;
}
