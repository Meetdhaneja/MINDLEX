# 🧠 MINDLEX: AI Psychiatry Life Assistant

MINDLEX is a professional, high-aesthetic psychiatry-focused AI assistant built with **FastAPI**, **Next.js**, and **Groq Cloud LLMs**. It features deep emotional intelligence, clinical DSM-5 knowledge retrieval (RAG), and persistent session management.

## ✨ Features
- **Session Management**: Rename and delete conversations persistently.
- **Emotional Intelligence**: Real-time emotion detection and risk assessment.
- **Clinical RAG**: Context-aware psychiatry assistance using DSM-5 data.
- **Premium UI**: Dark-mode primary interface with responsive sidebar and smooth glassmorphism.

## 🚀 Quick Start

### 1. Requirements
- Python 3.9+
- Node.js 18+
- Groq Cloud API Key

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key_here
LM_STUDIO_URL=https://api.groq.com/openai
LM_STUDIO_MODEL=llama-3.1-8b-instant
DATABASE_URL=sqlite:///./psychat.db
DSM_DATA_PATH=./data/dsm.json
```

### 3. Run the Engine (Backend)
```bash
python -m uvicorn backend.main:app --port 8000
```

### 4. Run the Interface (Frontend)
```bash
cd frontend
npm install
npm run dev -- -p 3000
```

Access the application at [http://127.0.0.1:3000](http://127.0.0.1:3000).

## 🛠️ Tech Stack
- **Backend**: FastAPI, SQLAlchemy (SQLite), Pydantic, HTTPI, FAISS.
- **Frontend**: Next.js, React, Vanilla CSS (Aesthetic-focused).
- **AI**: Groq (Llama 3.1), sentence-transformers (MiniLM), DistilRoBERTa.

## ⚖️ License
MIT
