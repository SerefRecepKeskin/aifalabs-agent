from fastapi import APIRouter, Depends, HTTPException, Request
from api.schema import ChatRequest, ChatResponse
from api.exception.agent import AgentProcessingError

chat_router = APIRouter(tags=["chat"])

@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    try:
        agent_service = req.app.state.agent_service
        result = await agent_service.process_chat(request.message)
        
        return ChatResponse(
            response=result["response"],
            agent_used=result["agent_used"]
        )
    except Exception as e:
        raise AgentProcessingError(str(e))
