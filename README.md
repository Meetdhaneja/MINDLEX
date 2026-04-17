# AI Psychiatry Chatbot

Full-stack local psychiatry support chatbot built with FastAPI, Next.js, SQLite, LM Studio, Hugging Face emotion detection, and DSM-5 RAG over FAISS.

## Structure

```text
backend/
  main.py
  rag.py
  emotion.py
  risk.py
  db.py
frontend/
  pages/index.js
  components/Chat.js
data/
  dsm.json
```

## Environment

Create a root `.env` from `.env.example`:

```env
HF_TOKEN=your_token_here
LM_STUDIO_URL=http://127.0.0.1:1234
LM_STUDIO_MODEL=nvidia/nemotron-3-nano-4b
DATABASE_URL=sqlite:///./psychat.db
DSM_DATA_PATH=./data/dsm.json
```

Create `frontend/.env.local` from `frontend/.env.local.example`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Run Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

## LM Studio

1. Start LM Studio local server.
2. Load `nvidia/nemotron-3-nano-4b`.
3. Ensure the OpenAI-compatible API is available at `http://127.0.0.1:1234`.

## Docker

After creating `.env`, you can run the full stack with Docker:

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Backend container reaches LM Studio on the host via `host.docker.internal:1234`
- If LM Studio is not reachable there, set `DOCKER_LM_STUDIO_URL=http://host.docker.internal:1234` before `docker compose up`

## Available Endpoints

- `POST /chat`
- `GET /history`
- `GET /health`
