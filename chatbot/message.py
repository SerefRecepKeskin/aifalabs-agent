from typing import AnyStr, List

from llama_index.core.base.llms.types import ChatMessage, MessageRole


class ChatMessageFormatter: 
    def __init__(self, system_prompt: AnyStr):
        self.system_prompt = system_prompt

    def format_messages(
        self,
        chat_history: List[ChatMessage],
        agent_response: AnyStr = None,
        user_message: AnyStr = None
    ) -> List[ChatMessage]:
        """
        Format messages for sending to vLLM

        :param chat_history: user chat history
        :param agent_response: agent response
        :param user_message: user message
        :return: list of chat messages
        """
        formatted_messages = []

        # add system prompt in the system role
        if self.system_prompt:
            formatted_messages.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content=self.system_prompt
            ))

        # add chat history
        chat_messages = []

        for message in chat_history:
            chat_messages.append(ChatMessage(
                role=message.role,
                content=message.content
            ))

        formatted_messages.extend(chat_messages)

        if (user_message is not None) and (agent_response is not None):
            user_message = f'User Message: {user_message}\ Agent Response: {agent_response}'

            formatted_messages.append(ChatMessage(
                role=MessageRole.USER,
                content=user_message
            ))

        elif user_message is not None:

            formatted_messages.append(ChatMessage(
                role=MessageRole.USER,
                content=user_message
            ))

        return formatted_messages
