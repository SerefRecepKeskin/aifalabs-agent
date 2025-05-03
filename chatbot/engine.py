from typing import AnyStr, AsyncGenerator, List, Optional

from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.base.response.schema import StreamingResponse
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.chat_engine.types import AgentChatResponse

from prompt.system import CONVERSATIONAL_SYSTEM_PROMPT
from util import logger

from .message import ChatMessageFormatter


class CustomChatEngine(SimpleChatEngine):
    async def achat(
        self,
        message: AnyStr,
        chat_history: Optional[List[ChatMessage]] = None,
        agent_response: Optional[AnyStr] = None,  
    ) -> AgentChatResponse:
        """
        Chat with user chat history

        :param message: user message
        :param chat_history: list of messages in the chat history
        :param agent_response: additional agent response to include
        :return: chat response come from llm server
        """

        formatter = ChatMessageFormatter(
            system_prompt=CONVERSATIONAL_SYSTEM_PROMPT
        )

        # format messages for sending to llm
        messages = formatter.format_messages(
            chat_history=chat_history or [],
            user_message=message)

        response = await self._llm.achat(
            messages=messages
        )

        return response
