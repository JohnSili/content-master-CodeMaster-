import aiohttp
from app.config import settings

class NewsService:
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/top-headlines"

    async def get_top_headlines(self, category: str = "general", country: str = "us", page_size: int = 10):
        async with aiohttp.ClientSession() as session:
            params = {
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": page_size
            }
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["articles"]
                else:
                    return []

news_service = NewsService()