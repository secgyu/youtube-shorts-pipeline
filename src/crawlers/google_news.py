import asyncio
from datetime import datetime
from typing import Optional
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from src.crawlers.base import BaseCrawler
from src.models import NewsItem, NewsSource
from src.utils.logger import get_logger


logger = get_logger(__name__)


class GoogleNewsCrawler(BaseCrawler):
    """Google News RSS 크롤러"""
    
    BASE_URL = "https://news.google.com/rss/search"
    
    def __init__(self, language: str = "ko", country: str = "KR"):
        self.language = language
        self.country = country
    
    def get_source_name(self) -> str:
        return "Google News"
    
    async def fetch(self, query: str = "IT 테크", limit: int = 10) -> list[NewsItem]:
        """Google News RSS에서 뉴스를 가져옵니다."""
        
        params = {
            "q": query,
            "hl": self.language,
            "gl": self.country,
            "ceid": f"{self.country}:{self.language}",
        }
        
        url = f"{self.BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        logger.info(f"Fetching Google News: {query}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                content = response.text
            
            feed = feedparser.parse(content)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            news_items = []
            for entry in feed.entries[:limit]:
                news_item = self._parse_entry(entry)
                if news_item:
                    news_items.append(news_item)
            
            logger.info(f"Fetched {len(news_items)} news items from Google News")
            return news_items
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching Google News: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Google News: {e}")
            return []
    
    def _parse_entry(self, entry: dict) -> Optional[NewsItem]:
        """RSS 엔트리를 NewsItem으로 변환"""
        try:
            title = entry.get("title", "")
            
            # Google News는 제목에 " - 출처" 형식으로 소스가 붙음
            source_name = "Unknown"
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                source_name = parts[1] if len(parts) > 1 else "Unknown"
            
            summary = entry.get("summary", entry.get("description", ""))
            # HTML 태그 간단히 제거
            summary = self._strip_html(summary)
            
            url = entry.get("link", "")
            
            published_at = None
            if "published" in entry:
                try:
                    published_at = parsedate_to_datetime(entry.published)
                except Exception:
                    pass
            
            return NewsItem(
                title=title,
                summary=summary[:500] if summary else "",
                url=url,
                source=NewsSource.GOOGLE_NEWS,
                source_name=source_name,
                published_at=published_at,
            )
            
        except Exception as e:
            logger.warning(f"Error parsing entry: {e}")
            return None
    
    def _strip_html(self, text: str) -> str:
        """간단한 HTML 태그 제거"""
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        clean = clean.replace('&nbsp;', ' ')
        clean = clean.replace('&amp;', '&')
        clean = clean.replace('&lt;', '<')
        clean = clean.replace('&gt;', '>')
        clean = clean.replace('&quot;', '"')
        return clean.strip()

