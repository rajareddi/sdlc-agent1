# 🔑 OpenAI API Setup Instructions

## Quick Setup

1. **Get your OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (starts with `sk-...`)

2. **Configure the backend:**
   - Open `backend/.env` file
   - Replace `your-openai-api-key-here` with your actual API key:
     ```
     OPENAI_API_KEY=sk-your-actual-key-here
     ```

3. **Restart the backend:**
   ```bash
   cd backend
   D:/agenticworkspace/sdlc-agent/.venv/Scripts/python.exe -m uvicorn app:app --reload --port 8000
   ```

## ⚠️ Important Notes

- Keep your API key secure and never commit it to version control
- The `.env` file is already added to `.gitignore` for security
- You need an OpenAI account with available credits to use the API
- The app uses GPT-3.5-turbo model by default

## 🧪 Testing

Once configured, you can test the API endpoints:

- **Health check:** `GET http://127.0.0.1:8000/`
- **Generate draft:** `POST http://127.0.0.1:8000/generate-draft`
- **Next phase:** `GET http://127.0.0.1:8000/next-phase`

## 🌐 Frontend Integration

The React frontend will automatically connect to the backend API and use the LangGraph orchestrator to generate AI-powered SDLC documentation with human-in-the-loop review.
