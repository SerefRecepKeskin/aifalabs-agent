from util import logger
from api.schema.agent import MessageResult, MessageRequest
from api.exception import ChatResponseError
from uuid import UUID
from typing import AnyStr
from chatbot.worker import AgentWorker 
class AgentService:
    def __init__(self, agent_worker:AgentWorker=None):
        self._chatbot = agent_worker  # Store the agent_worker instance
    
    async def create_bot_response(
        self,
        user_identifier: UUID,
        session_identifier: UUID,
        user_message: AnyStr
    ) -> MessageResult:
        """
        Generates a bot response to a user's message in a specific session

        :param session_identifier: user session identifier
        :param user_message: user message come from chat
        :return: the bot's response as a "MessageResult" object
        """
        try:
            response = await self._chatbot.process_chat(
                user_identifier,
                session_identifier,
                user_message
            )

            result = {
                'bot_message': response['response'],
                'message_identifier': response['message_identifier']
            }

            return MessageResult(**result)
        except Exception as ex:
            logger.error('Unexpected error while creating bot response: %s', ex)
            raise ChatResponseError(
                detail='Failed to create bot response'
            ) from ex

