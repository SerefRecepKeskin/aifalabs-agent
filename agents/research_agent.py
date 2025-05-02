from typing import Dict, List, Any
import aiohttp
from .base_agent import BaseAgent
from external_api import search_research_topic
from  llama_index.core.base.llms.types import ChatMessage

RESEARCH_AGENT_PROMPT = """You are a helpful assistant specializing in providing information about research topics.
You can search for research papers and articles and provide concise summaries of findings.
Always respond in a scholarly yet accessible manner.
"""

CONFIDENCE_PROMPT = """Determine if the following query is asking about a research topic.
Query: "{query}"
Respond with a confidence score between 0 and 1, where 1 means you're certain this is about research.
Only respond with the number.
"""

class ResearchAgent(BaseAgent):
    """Agent handling research topic information"""
    
    def __init__(self):
        super().__init__(system_prompt=RESEARCH_AGENT_PROMPT)
        
    async def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the query"""
        messages = [
            ChatMessage(role="system", content=CONFIDENCE_PROMPT.format(query=query)),
            ChatMessage(role="user", content="Determine confidence score")
        ]
        response = await self._get_llm_response(messages)
        try:
            confidence = float(response.strip())
            return min(max(confidence, 0.0), 1.0)  # Ensure between 0 and 1
        except ValueError:
            return 0.4  # Default to moderate confidence
        
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a research topic query"""
        # Extract research topic using LLM
        extract_prompt = "Extract the research topic from this query: {query}"
        extract_messages = [
            ChatMessage(role="system", content=extract_prompt.format(query=query)),
            ChatMessage(role="user", content=query)
        ]
        research_topic = await self._get_llm_response(extract_messages)
        
        # Get research information
        research_data = await search_research_topic(research_topic)
        
        # Format response with context
        context_data = {"topic": research_topic, "research_data": research_data}
        system_content = self.system_prompt + "\nHere is information about the query: " + str(context_data)
        response_messages = [
            ChatMessage(role="system", content=system_content),
            ChatMessage(role="user", content=query)
        ]
        
        return await self._get_llm_response(response_messages)