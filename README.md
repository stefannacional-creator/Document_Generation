# Document Generation Agent

A simple agentic document generator that takes a title, type, topic, and optional reference file, then uses an AI agent to plan, write, and compile a fully-formatted document — downloadable as a PDF.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, `react-markdown` |
| Backend | FastAPI, Python 3.11+, uv |
| AI / LLM | LangChain + Groq (LLaMA 3.3) or xAI (Grok) — both free tier |
| PDF | xhtml2pdf (pure Python, no system libs needed) |
| File parsing | pypdf (PDF), python-docx (DOCX), plain text / Markdown |

## Project Structure

```
Document_Generation/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── pyproject.toml           # Python deps (managed by uv)
│   ├── .env.example             # Copy to .env and fill in keys
│   ├── routes/
│   │   ├── generate.py          # POST /api/generate/stream  +  /api/generate/pdf
│   │   └── upload.py            # POST /api/upload-reference
│   ├── services/
│   │   ├── agent_service.py     # LangChain agentic loop
│   │   ├── llm_service.py       # LLM provider switcher (Groq / xAI)
│   │   └── pdf_service.py       # Markdown → PDF
│   └── tools/
│       └── document_tools.py    # plan_outline / write_section / finalize tools
└── frontend/
    ├── src/
    │   ├── app/page.tsx          # Main page
    │   ├── components/           # DocumentForm, DocumentPreview, AgentLog
    │   └── utils/api.ts          # All fetch calls to the backend
    └── next.config.mjs           # Proxies /api/* to the backend
```

## Setup

### 1. Backend

**Requirements:** Python 3.11+ and [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
cd backend

# Create the virtual environment
uv venv

# Copy and fill in environment variables
cp .env.example .env
# Edit .env — set LLM_PROVIDER and the matching API key (see below)

# Install dependencies
uv sync

# Run the backend
uv run uvicorn main:app --reload
# Runs on http://localhost:8000
```

**`.env` keys:**

| Key | Required | Description |
|-----|----------|-------------|
| `LLM_PROVIDER` | Yes | `groq` or `xai` |
| `GROQ_API_KEY` | If using Groq | Free at [console.groq.com](https://console.groq.com) |
| `XAI_API_KEY` | If using xAI | Free tier at [x.ai](https://x.ai) |
| `LLM_MODEL` | No | Override the default model |

---

### 2. Frontend

**Requirements:** Node.js 18+

```bash
cd frontend

npm install

npm run dev
# Runs on http://localhost:3000
```

The Next.js dev server proxies all `/api/*` requests to `http://localhost:8000` automatically — no CORS config needed locally.

---

## How it works

1. Fill in the form (title, document type, topic, writing style)
2. Optionally attach a reference file (PDF, DOCX, TXT, or Markdown) — its text is extracted and passed to the agent as context
3. Click **Generate Document** — the agent streams its progress live (outline → sections → finalize)
4. Click **Download PDF** to get a styled PDF of the finished document
