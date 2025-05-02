from abc import ABC, abstractmethod
from typing import Dict, List, Any
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core import Settings
from llama_index.core.chat_engine import SimpleChatEngine

class BaseAgent(ABC):
    """Base class for all domain-specific agents"""
    
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.chat_engine = SimpleChatEngine.from_defaults()
        
    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a user query and return a response"""
        pass
    
    @abstractmethod
    async def can_handle(self, query: str) -> float:
        """
        Determine if this agent can handle the given query
        Returns a confidence score between 0 and 1
        """
        pass
        
    async def _format_messages(self, query: str, context: Dict[str, Any] = None) -> List[ChatMessage]:
        """Format messages for the LLM"""
        messages = [
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=query)
        ]
        return messages
        
    async def _get_llm_response(self, messages: List[ChatMessage]) -> str:
        """Get response from LLM"""
        response = await Settings.llm.achat(messages=messages)
        return response.message.content