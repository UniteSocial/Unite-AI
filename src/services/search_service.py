import asyncio
import logging
import re
import httpx
from typing import List, Dict
from ..config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for performing web searches using Brave Search API"""
    
    def __init__(self):
        self.api_key = settings.BRAVE_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.enabled = bool(self.api_key and self.api_key != "")
        
        if not self.enabled:
            logger.warning("Brave Search API not configured - web search disabled")
        else:
            logger.info("Brave Search API initialized")
    
    async def search(
        self,
        query: str,
        count: int = 5,
        language: str = "en"
    ) -> List[Dict[str, str]]:
        """
        Perform a web search and return relevant results
        
        Args:
            query: Search query
            count: Number of results to return (max 20)
            language: Language code (en, de, etc.)
            
        Returns:
            List of search results with title, url, and snippet
        """
        if not self.enabled:
            logger.warning("Search attempted but Brave API not configured")
            return []
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": min(count, 20),  # Max 20 results
                "search_lang": language,
                "country": "de" if language == "de" else "us",
                "safesearch": "moderate",
                "freshness": "pm",  # Past month for recent info
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            # Extract web results
            results = []
            web_results = data.get("web", {}).get("results", [])
            
            # HTML stripping regex
            html_pattern = re.compile(r'<[^>]+>')
            
            for result in web_results[:count]:
                # Strip HTML tags from title and snippet to prevent JSON parsing issues
                title = html_pattern.sub('', result.get("title", ""))
                snippet = html_pattern.sub('', result.get("description", ""))
                
                results.append({
                    "title": title,
                    "url": result.get("url", ""),
                    "snippet": snippet,
                    "age": result.get("age", "")
                })
            
            logger.info(f"Search returned {len(results)} results for query: {query}")
            return results
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Brave Search API rate limit hit (429). Retrying after delay...")
                await asyncio.sleep(1.0)
                return []
            logger.error(f"HTTP error during search: {e.response.status_code}: {e}")
            return []
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            return []
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
