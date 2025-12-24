from abc import ABC, abstractmethod
from src.models import NewsItem


class BaseCrawler(ABC):
    """뉴스 크롤러 베이스 클래스"""
    
    @abstractmethod
    async def fetch(self, query: str = "", limit: int = 10) -> list[NewsItem]:
        """뉴스 목록을 가져옵니다.
        
        Args:
            query: 검색어 (빈 문자열이면 기본 IT/테크 뉴스)
            limit: 가져올 최대 개수
            
        Returns:
            NewsItem 리스트
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """크롤러 소스 이름 반환"""
        pass

