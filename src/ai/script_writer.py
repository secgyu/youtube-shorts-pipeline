from src.ai.client import OpenAIClient
from src.models import SelectedNews, Script
from src.utils.logger import get_logger
from config.prompts import SCRIPT_GENERATION_SYSTEM, SCRIPT_GENERATION_USER


logger = get_logger(__name__)


class ScriptWriter:
    """GPT를 사용하여 쇼츠 스크립트를 생성"""
    
    def __init__(self):
        self.client = OpenAIClient()
    
    async def write(self, selected_news: SelectedNews) -> Script:
        """선별된 뉴스를 바탕으로 쇼츠 스크립트를 생성합니다.
        
        Args:
            selected_news: 선별된 뉴스 정보
            
        Returns:
            생성된 스크립트
        """
        
        news = selected_news.news_item
        logger.info(f"Writing script for: {news.title[:50]}...")
        
        user_prompt = SCRIPT_GENERATION_USER.format(
            title=news.title,
            summary=news.summary or "요약 없음",
            url=news.url,
            hook_idea=selected_news.hook_idea,
        )
        
        try:
            result = await self.client.chat_json(
                system_prompt=SCRIPT_GENERATION_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.7,
            )
            
            script_data = result.get("script", {})
            
            script = Script(
                title=result.get("title", news.title),
                hook=script_data.get("hook", ""),
                body=script_data.get("body", ""),
                outro=script_data.get("outro", ""),
                full_script=result.get("full_script", ""),
                keywords=result.get("keywords", []),
                hashtags=result.get("hashtags", []),
                description=result.get("description", ""),
            )
            
            logger.info(
                f"Script generated: {script.character_count} chars, "
                f"~{script.estimated_duration:.1f}s"
            )
            
            return script
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise
    
    async def write_batch(
        self,
        selected_news_list: list[SelectedNews],
    ) -> list[Script]:
        """여러 뉴스에 대해 스크립트를 일괄 생성합니다."""
        
        scripts = []
        for selected in selected_news_list:
            try:
                script = await self.write(selected)
                scripts.append(script)
            except Exception as e:
                logger.error(f"Failed to write script: {e}")
                continue
        
        logger.info(f"Generated {len(scripts)} scripts")
        return scripts


