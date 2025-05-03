# agents/city_agent.py
from typing import Dict, List, Any
import aiohttp
from .base_agent import BaseAgent
from external_api import get_city_info, get_weather_info
from llama_index.core.base.llms.types import ChatMessage
CITY_AGENT_PROMPT = """You are a helpful assistant specializing in providing information about cities and weather.
You can provide general information about cities and current weather conditions.
Always respond in a friendly and informative manner.
"""

CONFIDENCE_PROMPT = """Determine if the following query is asking about a city or weather information.
Query: "{query}"
Respond with a confidence score between 0 and 1, where 1 means you're certain this is about cities or weather.
Only respond with the number.
"""

QUERY_TYPE_PROMPT = """Determine if the following query is specifically about weather or just general city information.
Query: "{query}"
If it's about weather, respond with "weather".
If it's about general city information, respond with "city".
"""

class CityAgent(BaseAgent):
    """Agent handling city and weather information"""
    
    def __init__(self):
        super().__init__(system_prompt=CITY_AGENT_PROMPT)
        
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
            return 0.5  # Default to moderate confidence
        
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a city or weather query"""
        # Determine if this is about weather or general city info using LLM
        query_type_messages = [
            ChatMessage(role="system", content=QUERY_TYPE_PROMPT.format(query=query)),
            ChatMessage(role="user", content=query)
        ]
        query_type_response = await self._get_llm_response(query_type_messages)
        is_weather_query = "weather" in query_type_response.lower()
        
        # Extract city name using LLM
        extract_prompt = """Extract the name of the city from this query. 
        If no city is mentioned or you can't identify a city, respond with 'unknown_city'.
        Query: {query}"""
        extract_messages = [
            ChatMessage(role="system", content=extract_prompt.format(query=query)),
            ChatMessage(role="user", content=query)
        ]
        city_name = await self._get_llm_response(extract_messages)
        city_name = city_name.strip()
        
        # Handle case where city name extraction failed
        if city_name.lower() in ["unknown_city"]:
            # Fallback: Try a more direct approach to extract location
            fallback_prompt = """The user is asking about a location. 
            Try to identify any geographic location (city, country, region, etc.) in this query.
            If you still can't identify a location, respond with 'unknown'.
            Query: {query}"""
            
            fallback_messages = [
                ChatMessage(role="system", content=fallback_prompt.format(query=query)),
                ChatMessage(role="user", content=query)
            ]
            city_name = await self._get_llm_response(fallback_messages)
            city_name = city_name.strip()
            
            if city_name.lower() == 'unknown':
                return "I'm sorry, I couldn't identify which location you're asking about. Could you please specify a city or location?"
        
        # Get the appropriate information
        if is_weather_query:
            # Extract date if present in the query
            date_extract_prompt = """Extract the specific date from this query in YYYY-MM-DD format.
            If no specific date is mentioned, respond with 'None'.
            Query: {query}"""
            
            date_extract_messages = [
                ChatMessage(role="system", content=date_extract_prompt.format(query=query)),
                ChatMessage(role="user", content=query)
            ]
            
            date = await self._get_llm_response(date_extract_messages)
            # Normalize the date response
            date = date.strip()
            if date.lower() in ['none', 'no date', 'no specific date'] or 'none' in date.lower():
                date = None
                
            try:
                # Call the API with the date parameter
                weather_data = await get_weather_info(city_name, date)
                context_data = {"city": city_name, "weather_data": weather_data, "date": date}
            except Exception as e:
                # Fallback for API errors
                return f"I'm sorry, I couldn't retrieve weather information for {city_name}. Error: {str(e)}"
        else:
            try:
                city_data = await get_city_info(city_name)
                context_data = {"city": city_name, "city_data": city_data}
            except Exception as e:
                # Fallback for API errors
                return f"I'm sorry, I couldn't retrieve information for {city_name}. Error: {str(e)}"
        
        # Format response using LLM
        system_content = self.system_prompt + "\nHere is information about the query: " + str(context_data)
        response_messages = [
            ChatMessage(role="system", content=system_content),
            ChatMessage(role="user", content=query)
        ]
        
        return await self._get_llm_response(response_messages)