"""크롤러 테스트 스크립트

실행: python -m tests.test_crawlers
"""
import asyncio
import sys
from pathlib import Path

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawlers import GoogleNewsCrawler, NaverNewsCrawler
from src.utils.logger import setup_logger, get_logger


async def test_google_news():
    """Google News 크롤러 테스트"""
    print("\n" + "=" * 50)
    print("[TEST] Google News 크롤러 테스트")
    print("=" * 50)
    
    crawler = GoogleNewsCrawler()
    news_items = await crawler.fetch(query="AI 인공지능", limit=5)
    
    print(f"\n[OK] {len(news_items)}개 뉴스 수집 완료\n")
    
    for i, item in enumerate(news_items, 1):
        print(f"[{i}] {item.title}")
        print(f"    Source: {item.source_name}")
        if item.summary:
            print(f"    Summary: {item.summary[:80]}...")
        print(f"    URL: {item.url[:60]}...")
        print()
    
    return news_items


async def test_naver_news():
    """네이버 뉴스 크롤러 테스트"""
    print("\n" + "=" * 50)
    print("[TEST] 네이버 뉴스 크롤러 테스트 (IT/과학 섹션)")
    print("=" * 50)
    
    crawler = NaverNewsCrawler()
    
    # 섹션 뉴스 테스트
    news_items = await crawler.fetch(limit=5)
    
    print(f"\n[OK] {len(news_items)}개 뉴스 수집 완료\n")
    
    for i, item in enumerate(news_items, 1):
        print(f"[{i}] {item.title}")
        print(f"    Source: {item.source_name}")
        if item.summary:
            print(f"    Summary: {item.summary[:80]}...")
        print()
    
    return news_items


async def test_naver_search():
    """네이버 뉴스 검색 테스트"""
    print("\n" + "=" * 50)
    print("[TEST] 네이버 뉴스 검색 테스트")
    print("=" * 50)
    
    crawler = NaverNewsCrawler()
    news_items = await crawler.fetch(query="챗GPT", limit=5)
    
    print(f"\n[OK] {len(news_items)}개 뉴스 수집 완료\n")
    
    for i, item in enumerate(news_items, 1):
        print(f"[{i}] {item.title}")
        print(f"    Source: {item.source_name}")
        print()
    
    return news_items


async def main():
    setup_logger(log_level="INFO")
    
    print("\n[START] 크롤러 테스트 시작\n")
    
    # Google News 테스트
    google_results = await test_google_news()
    
    # 네이버 섹션 테스트
    naver_results = await test_naver_news()
    
    # 네이버 검색 테스트
    naver_search_results = await test_naver_search()
    
    print("\n" + "=" * 50)
    print("[SUMMARY] 테스트 결과 요약")
    print("=" * 50)
    print(f"Google News: {len(google_results)}개")
    print(f"Naver Section: {len(naver_results)}개")
    print(f"Naver Search: {len(naver_search_results)}개")
    print("\n[DONE] 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())
