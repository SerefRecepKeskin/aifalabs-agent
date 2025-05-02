import aiohttp
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from config import config

logger = logging.getLogger(__name__)

async def search_research_topic(topic: str) -> List[Dict[str, Any]]:
    """Search for research papers or articles about a topic"""
    logger.info(f"Searching for research papers on topic: {topic}")
    # Get API endpoint from config
    semantic_scholar_url = config.get('research', {}).get('semantic_scholar_url', 
                                                          'https://api.semanticscholar.org/graph/v1/paper/search')
    limit = config.get('research', {}).get('results_limit', 5)
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{semantic_scholar_url}?query={topic}&limit={limit}&fields=title,abstract,url,year,authors"
            logger.debug(f"Making API request to: {url}")
            
            async with session.get(url) as response:
                if response.status == 200:
                    logger.info(f"Successfully received response from Semantic Scholar API for topic: {topic}")
                    data = await response.json()
                    papers = data.get("data", [])
                    logger.debug(f"Found {len(papers)} research papers")
                    return [{
                        "title": paper.get("title", ""),
                        "abstract": paper.get("abstract", ""),
                        "year": paper.get("year", ""),
                        "url": paper.get("url", ""),
                        "authors": ", ".join([author.get("name", "") for author in paper.get("authors", [])])
                    } for paper in papers]
                else:
                    logger.warning(f"Semantic Scholar API returned status {response.status}. Falling back to web scraping.")
                    # Fallback to web scraping if API fails
                    return await web_scrape_research(topic)
    except Exception as e:
        logger.error(f"Error while fetching research papers: {str(e)}")
        logger.info("Attempting fallback to web scraping")
        return await web_scrape_research(topic)

async def web_scrape_research(topic: str) -> List[Dict[str, Any]]:
    """Scrape research information from the web"""
    logger.info(f"Web scraping research information for topic: {topic}")
    # Get config values
    scholar_url = config.get('research', {}).get('google_scholar_url', 'https://scholar.google.com/scholar')
    user_agent = config.get('research', {}).get('user_agent', 
                                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    results_limit = config.get('research', {}).get('results_limit', 5)
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{scholar_url}?q={topic.replace(' ', '+')}"
            logger.debug(f"Making request to Google Scholar: {url}")
            
            # Use a user agent to avoid being blocked
            headers = {
                "User-Agent": user_agent
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Successfully received response from Google Scholar for topic: {topic}")
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    items = soup.select('.gs_ri')[:results_limit]
                    logger.debug(f"Found {len(items)} research items from web scraping")
                    
                    for item in items:
                        title_elem = item.select_one('.gs_rt')
                        title = title_elem.text if title_elem else "Title not found"
                        
                        link = ""
                        if title_elem and title_elem.find('a'):
                            link = title_elem.find('a').get('href', "")
                        
                        snippet_elem = item.select_one('.gs_rs')
                        snippet = snippet_elem.text if snippet_elem else "Abstract not available"
                        
                        meta_elem = item.select_one('.gs_a')
                        meta = meta_elem.text if meta_elem else ""
                        
                        results.append({
                            "title": title,
                            "abstract": snippet,
                            "meta": meta,
                            "url": link
                        })
                    
                    logger.info(f"Successfully extracted {len(results)} research items")
                    return results
                else:
                    logger.error(f"Failed to scrape research information, status code: {response.status}")
                    return [{"error": "Could not retrieve research information"}]
    except Exception as e:
        logger.error(f"Error during web scraping: {str(e)}")
        return [{"error": f"Exception during research: {str(e)}"}]