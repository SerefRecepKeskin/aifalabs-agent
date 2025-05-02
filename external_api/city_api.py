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

async def get_weather_info(city_name: str, date: str = None) -> Dict[str, Any]:
    """Get weather information for a city from WeatherAPI
    
    Args:
        city_name: The name of the city
        date: Optional specific date in YYYY-MM-DD format
    """
    logger.info(f"Fetching weather information for: {city_name}{' for date: ' + date if date else ''}")
    try:
        # Get API key from config
        API_KEY = config.get('weather', {}).get('api_key', '')
        if not API_KEY:
            logger.error("Weather API key not found in configuration")
            return {"error": "Weather API key is missing in configuration"}
            
        base_url = config.get('weather', {}).get('weatherapi_url', 'http://api.weatherapi.com/v1/current.json')
        
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}?key={API_KEY}&q={city_name}"
            # Add date parameter if provided
            if date:
                url += f"&dt={date}"
            
            logger.debug(f"Making request to WeatherAPI for {city_name}: {url}")
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.debug(f"Successfully received weather data for {city_name}")
                        data = await response.json()
                        current = data.get("current", {})
                        condition = current.get("condition", {})
                        
                        result = {
                            "temperature": current.get("temp_c", ""),
                            "humidity": current.get("humidity", ""),
                            "conditions": condition.get("text", ""),
                            "wind_speed": current.get("wind_kph", ""),
                            "feels_like": current.get("feelslike_c", ""),
                            "uv_index": current.get("uv", ""),
                            "pressure": current.get("pressure_mb", ""),
                            "precipitation": current.get("precip_mm", ""),
                            "last_updated": current.get("last_updated", "")
                        }
                        logger.info(f"Returning weather data for: {city_name}")
                        return result
                    else:
                        error_msg = f"Failed to get weather for {city_name}, status code: {response.status}"
                        logger.error(error_msg)
                        try:
                            error_data = await response.json()
                            logger.error(f"Error details: {error_data}")
                            return {"error": f"Could not find weather for {city_name}", "details": error_data.get("error", {}).get("message", "")}
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