from typing import AnyStr, Dict

from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.memory import ChatMemoryBuffer

from db.settings import settings
from session.store import CustomPostgresChatStore


class SessionManager:
    def __init__(self):
        self._chat_store = CustomPostgresChatStore.from_uri(
            uri=settings.DATABASE_URL,
            table_name='chat_history'
        )

        self._active_sessions: Dict[AnyStr: ChatMemoryBuffer] = {}

    async def get_or_create_session(
        self,
        user_id: AnyStr,
        session_id: AnyStr
    ) -> ChatMemoryBuffer:
        """
        Get or create user session

        :param user_id: user identifier
        :param session_id: session identifier
        :return: chat memory object
        """
        if session_id not in self._active_sessions:
            chat_memory = ChatMemoryBuffer.from_defaults(
                token_limit=2048,
                chat_store=self._chat_store,
                chat_store_key=f'{user_id}:{session_id}'
            )

            self._active_sessions[session_id] = chat_memory

        return self._active_sessions[session_id]

    async def save_messages(
        self,
        session_id: AnyStr,
        message_identifier: AnyStr,
        user_message: AnyStr,
        assistant_message: AnyStr
    ) -> None:
        """
        Save messages to chat memory

        :param session_id: session identifier
        :param user_message: user message
        :param assistant_message: assistant's message for reply to user message
        :return: chat memory object
        """
        messages = []

        messages.append(ChatMessage(
            role=MessageRole.USER,
            content=user_message,
            additional_kwargs={
                'message_identifier': message_identifier
            }
        ))

        messages.append(ChatMessage(
            role=MessageRole.ASSISTANT,
            content=assistant_message,
            additional_kwargs={
                'message_identifier': message_identifier
            }
        ))

        await self._active_sessions[session_id].aput_messages(messages)

    async def close_session(self, session_id: AnyStr) -> None:
        """
        Close user session and reset memory

        :param session_id: session identifier
        """
        chat_memory = self._active_sessions.pop(session_id)

        chat_memory.reset()
