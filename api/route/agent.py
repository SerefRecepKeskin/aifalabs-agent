from fastapi import APIRouter, Depends, HTTPException, Request
from api.schema import MessageRequest, MessageResult
from api.exception.agent import AgentProcessingError
from api.service import AgentService
from chatbot.worker import AgentWorker
chat_router = APIRouter(tags=["chat"])

async def get_agent_worker(request: Request) -> AgentWorker:
    """
    Initialize chatbot worker once when the application is up
    """
    return request.app.state.agent_worker


@chat_router.post("/chat", response_model=MessageResult)
async def chat(request: MessageRequest,
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
