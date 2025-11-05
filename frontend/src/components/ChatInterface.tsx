import React, { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';
import { useSettingsStore } from '../stores/settingsStore';
import { chatApi } from '../services/api';
import { Send, Bot, User, Database, Loader2, Trash2 } from 'lucide-react';
import type { ChatMessage } from '../types/chat';

const ChatInterface: React.FC = () => {
  const { messages, addMessage, isLoading, setLoading, clearMessages, sessionId } = useChatStore();
  const { userId, selectedModel, useMemory, memoryLimit } = useSettingsStore();
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await chatApi.send({
        message: inputMessage,
        user_id: userId,
        session_id: sessionId,
        model: selectedModel,
        use_memory: useMemory,
        memory_limit: memoryLimit,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        related_memories: response.related_memories,
      };

      addMessage(assistantMessage);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend and Ollama are running.',
        timestamp: new Date().toISOString(),
      };
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      clearMessages();
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return '';
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Chat</h2>
            <p className="text-sm text-gray-500">
              Model: <span className="font-medium">{selectedModel}</span>
              {useMemory && (
                <span className="ml-2">
                  | Memory: <span className="font-medium">Enabled ({memoryLimit} results)</span>
                </span>
              )}
            </p>
          </div>
          <button
            onClick={handleClearChat}
            className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <Trash2 size={16} />
            Clear Chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-12">
            <Bot size={48} className="mx-auto mb-4 text-gray-400" />
            <p className="text-lg">Start a conversation!</p>
            <p className="text-sm mt-2">
              Your messages will be answered using stored memories and the selected LLM model.
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-4 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <Bot size={18} className="text-primary-600" />
                </div>
              )}

              <div
                className={`flex flex-col max-w-2xl ${
                  message.role === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                <div
                  className={`px-4 py-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>

                {/* Related Memories */}
                {message.related_memories && message.related_memories.length > 0 && (
                  <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200 max-w-full">
                    <div className="flex items-center gap-2 text-sm font-medium text-blue-900 mb-2">
                      <Database size={14} />
                      Related Memories
                    </div>
                    <div className="space-y-1">
                      {message.related_memories.map((mem, idx) => (
                        <div key={idx} className="text-xs text-blue-800">
                          • {mem.memory || mem.content}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <span className="text-xs text-gray-500 mt-1">
                  {formatTime(message.timestamp)}
                </span>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                  <User size={18} className="text-gray-600" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot size={18} className="text-primary-600" />
            </div>
            <div className="flex items-center gap-2 px-4 py-3 bg-gray-100 rounded-lg">
              <Loader2 size={16} className="animate-spin text-gray-600" />
              <span className="text-gray-600">Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <Send size={18} />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
