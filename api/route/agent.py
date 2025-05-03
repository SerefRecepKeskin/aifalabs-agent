from fastapi import APIRouter, Depends, Header, Request
from api.schema import MessageRequest, MessageResult
from api.exception.agent import AgentProcessingError
from api.service import AgentService
from chatbot.worker import AgentWorker
from api.service.auth import AuthService
from typing import Annotated


chat_router = APIRouter(tags=["chat"])

async def get_agent_worker(request: Request) -> AgentWorker:
    """
    Initialize chatbot worker once when the application is up
    """
    return request.app.state.agent_worker

async def verify_api_key(x_api_key: Annotated[str, Header()]) -> str:
    """
    Verify the API key from request header.
    
    Args:
        x_api_key: API key from request header
    
    Returns:
        str: Verified API key
    
    Raises:
        HTTPException: If API key is invalid
    """
    AuthService.check_auth(x_api_key)
    return x_api_key

@chat_router.post("/chat", response_model=MessageResult)
async def chat(token: Annotated[str, Depends(verify_api_key)],
               request: MessageRequest,
               agent_worker: AgentWorker = Depends(get_agent_worker)
):
    try:
        agent_service = AgentService(agent_worker)

        result = await agent_service.create_bot_response(
            user_message=request.user_message,
            user_identifier=request.user_identifier,
            session_identifier=request.session_identifier,
        )
        
        # Access attributes directly instead of treating result as a dictionary
        return MessageResult(
            bot_message=result.bot_message,
            message_identifier=result.message_identifier
        )
    except Exception as e:
        raise AgentProcessingError(str(e))


@chat_router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify that the API is running
    """
    return {"status": "healthy", "message": "Service is running"}
