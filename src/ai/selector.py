from src.ai.client import OpenAIClient
from src.models import NewsItem, SelectedNews
from src.utils.logger import get_logger
from config.prompts import NEWS_SELECTION_SYSTEM, NEWS_SELECTION_USER


logger = get_logger(__name__)


class NewsSelector:
    """GPT를 사용하여 쇼츠에 적합한 뉴스를 선별"""
    
    def __init__(self):
        self.client = OpenAIClient()
    
    async def select(
        self,
        news_items: list[NewsItem],
        count: int = 3,
    ) -> list[SelectedNews]:
        """뉴스 목록에서 쇼츠에 적합한 뉴스를 선별합니다.
        
        Args:
            news_items: 뉴스 아이템 리스트
            count: 선별할 개수
            
        Returns:
            선별된 뉴스 리스트 (SelectedNews)
        """
        
        if not news_items:
            logger.warning("No news items to select from")
            return []
        
        logger.info(f"Selecting {count} news from {len(news_items)} items")
        
        # 뉴스 목록을 텍스트로 변환
        news_list_text = self._format_news_list(news_items)
        
        # GPT에 선별 요청
        user_prompt = NEWS_SELECTION_USER.format(
            count=count,
            news_list=news_list_text,
        )
        
        try:
            result = await self.client.chat_json(
                system_prompt=NEWS_SELECTION_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.5,
            )
            
            selected = []
            for item in result.get("selected", []):
                index = item.get("index", 0)
                
                if 0 <= index < len(news_items):
                    selected_news = SelectedNews(
                        news_item=news_items[index],
                        selection_reason=item.get("reason", ""),
                        hook_idea=item.get("hook_idea", ""),
                    )
                    selected.append(selected_news)
                    logger.info(f"Selected: {news_items[index].title[:50]}...")
            
            logger.info(f"Selected {len(selected)} news items")
            return selected
            
        except Exception as e:
            logger.error(f"News selection failed: {e}")
            raise
    
    def _format_news_list(self, news_items: list[NewsItem]) -> str:
        """뉴스 목록을 GPT 입력용 텍스트로 변환"""
        lines = []
        for i, item in enumerate(news_items):
            lines.append(f"[{i}] 제목: {item.title}")
            lines.append(f"    출처: {item.source_name}")
            if item.summary:
                lines.append(f"    요약: {item.summary[:200]}")
            lines.append("")
        
        return "\n".join(lines)


