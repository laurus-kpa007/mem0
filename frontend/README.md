# Mem0 Test Program - Frontend

React + TypeScript + Vite frontend for the Mem0 test program.

## Features

- 💬 **Chat Interface**: Chat with AI using stored memories
- 📝 **Memory Management**: Add, view, and delete memories
- 🏷️ **AI Tag Suggestions**: Automatic tag generation for memories
- ⚙️ **Settings**: Configure LLM model, user ID, and memory settings
- 🎨 **Modern UI**: Built with Tailwind CSS and Lucide React icons

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **Zustand** - State management
- **React Router** - Routing
- **Axios** - API communication
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/       # Reusable components
│   ├── Layout.tsx
│   ├── ChatInterface.tsx
│   ├── MemoryInput.tsx
│   ├── MemoryList.tsx
│   └── ModelSelector.tsx
├── pages/           # Page components
│   ├── ChatPage.tsx
│   ├── MemoryPage.tsx
│   └── SettingsPage.tsx
├── stores/          # Zustand stores
│   ├── chatStore.ts
│   ├── memoryStore.ts
│   └── settingsStore.ts
├── services/        # API services
│   └── api.ts
├── types/           # TypeScript types
│   ├── memory.ts
│   ├── chat.ts
│   └── ollama.ts
├── App.tsx          # Main app component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Environment Variables

- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)

## Usage

### 1. Configure Settings

Go to Settings page to:
- Select your LLM model (e.g., llama3.2:latest)
- Set your user ID
- Enable/disable memory usage in chat
- Configure memory search limit

### 2. Add Memories

Go to Memory page to:
- Enter text content
- Click "Suggest Tags" for AI-powered tag suggestions
- Add tags manually if needed
- Save the memory

### 3. Chat with AI

Go to Chat page to:
- Ask questions
- Get answers based on your stored memories
- View related memories used in each response

## Development

```bash
# Start dev server
npm run dev

# Type checking
npm run build

# Lint
npm run lint
```

## API Integration

The frontend connects to the FastAPI backend at `VITE_API_BASE_URL`. Make sure the backend is running before starting the frontend.

Available endpoints:
- `POST /api/memory/add` - Add memory
- `GET /api/memory/list` - List memories
- `DELETE /api/memory/{id}` - Delete memory
- `POST /api/memory/suggest-tags` - Suggest tags
- `POST /api/chat` - Send chat message
- `GET /api/ollama/models` - List models

See [TAG_FEATURE.md](../TAG_FEATURE.md) for detailed tag feature documentation.
