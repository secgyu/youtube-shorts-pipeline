import json
from typing import Any

from openai import AsyncOpenAI

from config.settings import settings
from src.utils.logger import get_logger


logger = get_logger(__name__)


class OpenAIClient:
    """OpenAI API 클라이언트"""
    
    def __init__(self):
        config = settings()
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model
    
    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """GPT 채팅 완성 요청"""
        
        logger.debug(f"OpenAI request: model={self.model}, temp={temperature}")
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content
        logger.debug(f"OpenAI response: {len(content)} chars")
        
        return content
    
    async def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """GPT 채팅 완성 요청 (JSON 응답)"""
        
        response = await self.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # JSON 파싱 시도
        try:
            # ```json ... ``` 블록 제거
            content = response.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Raw response: {response}")
            raise ValueError(f"GPT 응답을 JSON으로 파싱할 수 없습니다: {e}")


