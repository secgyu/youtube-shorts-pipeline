"""AI 모듈 테스트 스크립트

실행: python -m tests.test_ai

주의: OPENAI_API_KEY가 .env에 설정되어 있어야 합니다.
"""
import asyncio
import sys
from pathlib import Path

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawlers import GoogleNewsCrawler
from src.ai import NewsSelector, ScriptWriter
from src.utils.logger import setup_logger, get_logger


async def test_news_selection():
    """뉴스 선별 테스트"""
    print("\n" + "=" * 50)
    print("[TEST] 뉴스 선별 테스트")
    print("=" * 50)
    
    # 먼저 뉴스 크롤링
    crawler = GoogleNewsCrawler()
    news_items = await crawler.fetch(query="AI 인공지능", limit=10)
    
    print(f"\n수집된 뉴스: {len(news_items)}개")
    
    # 뉴스 선별
    selector = NewsSelector()
    selected = await selector.select(news_items, count=2)
    
    print(f"\n[OK] {len(selected)}개 뉴스 선별 완료\n")
    
    for i, item in enumerate(selected, 1):
        print(f"[{i}] {item.news_item.title}")
        print(f"    이유: {item.selection_reason}")
        print(f"    훅 아이디어: {item.hook_idea}")
        print()
    
    return selected


async def test_script_generation(selected_news_list):
    """스크립트 생성 테스트"""
    print("\n" + "=" * 50)
    print("[TEST] 스크립트 생성 테스트")
    print("=" * 50)
    
    if not selected_news_list:
        print("[SKIP] 선별된 뉴스 없음")
        return []
    
    writer = ScriptWriter()
    
    # 첫 번째 뉴스만 테스트
    selected = selected_news_list[0]
    script = await writer.write(selected)
    
    print(f"\n[OK] 스크립트 생성 완료\n")
    print(f"제목: {script.title}")
    print(f"글자수: {script.character_count}자")
    print(f"예상 길이: {script.estimated_duration:.1f}초")
    print(f"\n--- 스크립트 ---")
    print(f"[훅] {script.hook}")
    print(f"[본문] {script.body[:200]}...")
    print(f"[아웃트로] {script.outro}")
    print(f"\n키워드: {', '.join(script.keywords)}")
    print(f"해시태그: {' '.join(script.hashtags)}")
    
    return [script]


async def main():
    setup_logger(log_level="INFO")
    
    print("\n[START] AI 모듈 테스트 시작")
    print("주의: OPENAI_API_KEY가 필요합니다.\n")
    
    try:
        # 뉴스 선별 테스트
        selected = await test_news_selection()
        
        # 스크립트 생성 테스트
        scripts = await test_script_generation(selected)
        
        print("\n" + "=" * 50)
        print("[SUMMARY] 테스트 결과 요약")
        print("=" * 50)
        print(f"선별된 뉴스: {len(selected)}개")
        print(f"생성된 스크립트: {len(scripts)}개")
        print("\n[DONE] 테스트 완료!")
        
    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        print("OPENAI_API_KEY가 .env에 설정되어 있는지 확인하세요.")
        raise


if __name__ == "__main__":
    asyncio.run(main())


