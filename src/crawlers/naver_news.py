import asyncio
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup

from src.crawlers.base import BaseCrawler
from src.models import NewsItem, NewsSource
from src.utils.logger import get_logger


logger = get_logger(__name__)


class NaverNewsCrawler(BaseCrawler):
    """네이버 뉴스 크롤러 (IT/과학 섹션)"""
    
    # 네이버 뉴스 IT/과학 섹션
    SECTION_URL = "https://news.naver.com/section/105"
    SEARCH_URL = "https://search.naver.com/search.naver"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    def get_source_name(self) -> str:
        return "Naver News"
    
    async def fetch(self, query: str = "", limit: int = 10) -> list[NewsItem]:
        """네이버 뉴스에서 IT/과학 뉴스를 가져옵니다."""
        
        if query:
            return await self._search_news(query, limit)
        else:
            return await self._fetch_section_news(limit)
    
    async def _fetch_section_news(self, limit: int) -> list[NewsItem]:
        """IT/과학 섹션의 최신 뉴스 가져오기"""
        
        logger.info("Fetching Naver IT/Science section news")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.SECTION_URL,
                    headers=self.HEADERS,
                    timeout=10.0
                )
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            news_items = []
            
            # 헤드라인 뉴스
            headline_list = soup.select("div.section_article ul li")
            
            for item in headline_list[:limit]:
                news_item = self._parse_section_item(item)
                if news_item:
                    news_items.append(news_item)
            
            logger.info(f"Fetched {len(news_items)} news items from Naver section")
            return news_items
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching Naver section: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Naver section: {e}")
            return []
    
    async def _search_news(self, query: str, limit: int) -> list[NewsItem]:
        """네이버 뉴스 검색"""
        
        logger.info(f"Searching Naver News: {query}")
        
        params = {
            "where": "news",
            "query": query,
            "sort": "1",  # 최신순
        }
        
        url = f"{self.SEARCH_URL}?{urlencode(params)}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.HEADERS,
                    timeout=10.0
                )
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            news_items = []
            
            # 뉴스 검색 결과
            news_list = soup.select("div.news_area")
            
            for item in news_list[:limit]:
                news_item = self._parse_search_item(item)
                if news_item:
                    news_items.append(news_item)
            
            logger.info(f"Fetched {len(news_items)} news items from Naver search")
            return news_items
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching Naver: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching Naver: {e}")
            return []
    
    def _parse_section_item(self, item) -> Optional[NewsItem]:
        """섹션 뉴스 아이템 파싱"""
        try:
            # 제목과 링크
            title_elem = item.select_one("a.sa_text_title")
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            url = title_elem.get("href", "")
            
            # 요약
            summary_elem = item.select_one("div.sa_text_lede")
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # 언론사
            source_elem = item.select_one("div.sa_text_press")
            source_name = source_elem.get_text(strip=True) if source_elem else "네이버 뉴스"
            
            # 이미지
            img_elem = item.select_one("img")
            image_url = img_elem.get("src") if img_elem else None
            
            return NewsItem(
                title=title,
                summary=summary[:500] if summary else "",
                url=url,
                source=NewsSource.NAVER_NEWS,
                source_name=source_name,
                image_url=image_url,
            )
            
        except Exception as e:
            logger.warning(f"Error parsing section item: {e}")
            return None
    
    def _parse_search_item(self, item) -> Optional[NewsItem]:
        """검색 결과 아이템 파싱"""
        try:
            # 제목과 링크
            title_elem = item.select_one("a.news_tit")
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            url = title_elem.get("href", "")
            
            # 요약
            summary_elem = item.select_one("div.news_dsc")
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # 언론사
            source_elem = item.select_one("a.info.press")
            source_name = source_elem.get_text(strip=True) if source_elem else "Unknown"
            
            # 이미지
            img_elem = item.select_one("img.thumb")
            image_url = img_elem.get("src") if img_elem else None
            
            return NewsItem(
                title=title,
                summary=summary[:500] if summary else "",
                url=url,
                source=NewsSource.NAVER_NEWS,
                source_name=source_name,
                image_url=image_url,
            )
            
        except Exception as e:
            logger.warning(f"Error parsing search item: {e}")
            return None

