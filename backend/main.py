from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routes.generate import router as generate_router
from routes.upload import router as upload_router

load_dotenv()

app = FastAPI(
    title="Document Generator Agent",
    description="Agentic document generation powered by Grok / LLaMA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router, prefix="/api/generate", tags=["generate"])
app.include_router(upload_router, prefix="/api/upload-reference", tags=["upload"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "document-generator-agent"}
