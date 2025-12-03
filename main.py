from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import create_agent
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Baseball Sabermetrics MCP Server")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

# Initialize agent lazily or on startup
agent_executor = None

@app.on_event("startup")
async def startup_event():
    global agent_executor
    try:
        agent_executor = create_agent()
        print("Agent initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to initialize agent on startup: {e}")
        print("Please ensure GEMINI_API_KEY is set in .env")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global agent_executor
    if not agent_executor:
        try:
            agent_executor = create_agent()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent not initialized: {e}")
            
    try:
        result = await agent_executor.ainvoke({"messages": [("user", req.message)]})
        answer = result["messages"][-1].content
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
