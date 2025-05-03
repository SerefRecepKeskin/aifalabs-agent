from typing import Dict, List, Any
from .base_agent import BaseAgent
from db.connector import get_connection, DATABASE_URL
from db.settings import settings
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.indices.struct_store.sql_query import SQLDatabase
from llama_index.core import Settings

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
        # Initialize the SQL database with the existing connection URL
        # We'll use the async version in the process_query method
        connection_string = settings.DATABASE_URL
        # Remove the asyncpg part as SQLDatabase expects SQLAlchemy format
        if 'asyncpg' in connection_string:
            connection_string = connection_string.replace('+asyncpg', '')
        self._sql_database = SQLDatabase.from_uri(connection_string)
        
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
        
    async def process_query(self, query: str) -> str:
        """Process a product query using NLSQLTableQueryEngine"""
        try:
            # Create query engine using the llm from Settings, disable embed_model
            query_engine = NLSQLTableQueryEngine(
                sql_database=self._sql_database,
                tables=["products"],
                llm=Settings.llm,
                synthesize_response=False,  # We'll synthesize the response ourselves
                embed_model='local',  # Explicitly disable embedding model
                sql_only=False  # Return both the query and results
            )
            
            # Query the database using natural language
            response = await query_engine.aquery(query)
            
            # Extract SQL query and results from response metadata
            sql_query = response.metadata.get("sql_query", "No SQL query available")
            
            # Format the response with context
            context_data = {
                "query_result": str(response),
                "query": query,
                "sql_query": sql_query
            }
            
            system_content = self.system_prompt + "\nHere is information about the query: " + str(context_data)
            response_messages = [
                ChatMessage(role="system", content=system_content),
                ChatMessage(role="user", content=query)
            ]
            
            return await self._get_llm_response(response_messages)
            
        except Exception as e:
            # Fallback to the original method if there's an error with the query engine
            return await self._fallback_query(query, str(e))
    
    async def _fallback_query(self, query: str, error: str = "") -> str:
        """Fallback method if there's an issue with the query engine"""
        # Extract product name using LLM
        extract_prompt = "Extract the name or type of product from this query: {query}"
        extract_messages = [
            ChatMessage(role="system", content=extract_prompt.format(query=query)),
            ChatMessage(role="user", content=query)
        ]
        product_name = await self._get_llm_response(extract_messages)
        product_name = product_name.strip()
        
        # Query the database directly
        async with get_connection() as conn:
            products = await conn.fetch(
                "SELECT name, description, price FROM products WHERE name ILIKE $1 OR description ILIKE $2",
                f"%{product_name}%", f"%{product_name}%"
            )
        
        # Format the response with context
        context_data = {
            "products": products, 
            "query": product_name,
            "note": f"Used fallback query method. Error with query engine: {error}"
        }
        system_content = self.system_prompt + "\nHere is information about the query: " + str(context_data)
        response_messages = [
            ChatMessage(role="system", content=system_content),
            ChatMessage(role="user", content=query)
        ]
        
        return await self._get_llm_response(response_messages)