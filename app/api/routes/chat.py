import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from services.agent import create_agent

router = APIRouter()
agent_executor = None

@router.post("/api/chat", response_model=ChatResponse)
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