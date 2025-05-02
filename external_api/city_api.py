import aiohttp
from typing import Dict, Any
from config import config
from util import logger

async def get_city_info(city_name: str) -> Dict[str, Any]:
    """Get information about a city from Wikipedia API"""
    logger.info(f"Fetching city information for: {city_name}")
    try:
        async with aiohttp.ClientSession() as session:
            # Wikipedia API endpoint from config
            base_url = config.get('wikipedia', {}).get('base_url', "https://en.wikipedia.org/api/rest_v1/page/summary/")
            
            # Fetch city information
            logger.debug(f"Making request to Wikipedia API: {base_url}{city_name}")
            try:
                async with session.get(f"{base_url}{city_name}") as response:
                    if response.status == 200:
                        logger.debug(f"Successfully received response from Wikipedia API for {city_name}")
                        data = await response.json()
                        result = {
                            "title": data.get("title", ""),
                            "extract": data.get("extract", ""),
                            "description": data.get("description", ""),
                            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                        }
                        logger.info(f"Returning city information for: {city_name}")
                        return result
                    else:
                        error_msg = f"Failed to get city information for {city_name}, status code: {response.status}"
                        logger.error(error_msg)
                        return {"error": f"Could not find information for {city_name}", "status": response.status}
            except aiohttp.ClientError as e:
                error_msg = f"Connection error while fetching city data for {city_name}: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error during city information fetch for {city_name}: {str(e)}"
        logger.exception(error_msg)
        return {"error": "An unexpected error occurred while retrieving city information"}

async def get_weather_info(city_name: str) -> Dict[str, Any]:
    """Get weather information for a city from OpenWeatherMap API"""
    logger.info(f"Fetching weather information for: {city_name}")
    try:
        # Get API key from config
        API_KEY = config.get('weather', {}).get('api_key', '')
        if not API_KEY:
            logger.error("Weather API key not found in configuration")
            return {"error": "Weather API key is missing in configuration"}
            
        base_url = config.get('weather', {}).get('openweathermap_url', 'https://api.openweathermap.org/data/2.5/weather')
        
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}?q={city_name}&appid={API_KEY}&units=metric"
            
            logger.debug(f"Making request to OpenWeatherMap API for {city_name}")
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.debug(f"Successfully received weather data for {city_name}")
                        data = await response.json()
                        result = {
                            "temperature": data.get("main", {}).get("temp", ""),
                            "humidity": data.get("main", {}).get("humidity", ""),
                            "conditions": data.get("weather", [{}])[0].get("description", ""),
                            "wind_speed": data.get("wind", {}).get("speed", "")
                        }
                        logger.info(f"Returning weather data for: {city_name}")
                        return result
                    else:
                        error_msg = f"Failed to get weather for {city_name}, status code: {response.status}"
                        logger.error(error_msg)
                        try:
                            error_data = await response.json()
                            logger.error(f"Error details: {error_data}")
                            return {"error": f"Could not find weather for {city_name}", "details": error_data.get("message", "")}
                        except:
                            return {"error": f"Could not find weather for {city_name}", "status": response.status}
            except aiohttp.ClientError as e:
                error_msg = f"Connection error while fetching weather data for {city_name}: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error during weather fetch for {city_name}: {str(e)}"
        logger.exception(error_msg)
        return {"error": "An unexpected error occurred while retrieving weather information"}