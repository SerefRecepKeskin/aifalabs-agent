from typing import Dict, List, Any
from .base_agent import BaseAgent
from db.connector import get_connection
from llama_index.core.base.llms.types import ChatMessage

PRODUCT_AGENT_PROMPT = """You are a helpful assistant specializing in providing information about products in our database.
You can search for products and provide details about them including name, description, price, and other specifications.
Always respond in a friendly and informative manner.
"""

CONFIDENCE_PROMPT = """Determine if the following query is asking about a product in our database.
Query: "{query}"
Respond with a confidence score between 0 and 1, where 1 means you're certain this is about a product.
Only respond with the number.
"""

class ProductAgent(BaseAgent):
    """Agent handling product database queries"""
    
    def __init__(self):
        super().__init__(system_prompt=PRODUCT_AGENT_PROMPT)
        
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
            return 0.3  # Default to lower confidence
        
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a product query"""
        # Extract product name using LLM
        extract_prompt = "Extract the name or type of product from this query: {query}"
        extract_messages = [
            ChatMessage(role="system", content=extract_prompt.format(query=query)),
            ChatMessage(role="user", content=query)
        ]
        product_name = await self._get_llm_response(extract_messages)
        
        # Query the database
        async with get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT name, description, price FROM products WHERE name ILIKE %s OR description ILIKE %s",
                    (f"%{product_name}%", f"%{product_name}%")
                )
                products = await cursor.fetchall()
        
        # Format the response with context
        context_data = {"products": products, "query": product_name}
        system_content = self.system_prompt + "\nHere is information about the query: " + str(context_data)
        response_messages = [
            ChatMessage(role="system", content=system_content),
            ChatMessage(role="user", content=query)
        ]
        
        return await self._get_llm_response(response_messages)