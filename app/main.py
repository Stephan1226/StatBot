import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat
from app.core.config import settings
from services.agent import create_agent
import uvicorn

app = FastAPI(title="Baseball Sabermetrics MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

agent_executor = None

@app.on_event("startup")
async def startup_event():
    global agent_executor
    try:
        agent_executor = create_agent()
        chat.agent_executor = agent_executor
        print("Agent initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to initialize agent on startup: {e}")
        print("Please ensure GEMINI_API_KEY is set in .env")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)