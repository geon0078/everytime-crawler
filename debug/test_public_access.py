"""
로그인 없이 공개 데이터 크롤링 테스트
"""

import os
import sys
import time
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from src.everytime_crawler.crawler import EverytimeCrawler

def test_public_access():
    """로그인 없이 공개 페이지 접근 테스트"""
    crawler = EverytimeCrawler()
    
    try:
        print("🔧 WebDriver 설정 중...")
        crawler.setup_driver(headless=False)
        
        print("🌐 에브리타임 메인 페이지 접근...")
        crawler.driver.get("https://everytime.kr")
        time.sleep(3)
        
        print(f"현재 URL: {crawler.driver.current_url}")
        print(f"페이지 제목: {crawler.driver.title}")
        
        # 페이지 스크린샷 저장
        crawler.driver.save_screenshot("debug/public_access_test.png")
        print("스크린샷 저장: debug/public_access_test.png")
        
        # HTML 소스 저장
        with open("debug/public_access_test.html", "w", encoding="utf-8") as f:
            f.write(crawler.driver.page_source)
        print("HTML 소스 저장: debug/public_access_test.html")
        
        # 공개 게시판 접근 시도
        print("\n🎯 공개 게시판 접근 시도...")
        public_boards = [
            "https://everytime.kr/389176",  # 자유게시판 (학교별로 다를 수 있음)
            "https://everytime.kr/free",    # 자유게시판
            "https://everytime.kr/389175",  # 비밀게시판
            "https://everytime.kr/secret",  # 비밀게시판
        ]
        
        for board_url in public_boards:
            try:
                print(f"\n📍 {board_url} 접근 중...")
                crawler.driver.get(board_url)
                time.sleep(3)
                
                print(f"접근 후 URL: {crawler.driver.current_url}")
                
                # 로그인 페이지로 리다이렉트되었는지 확인
                if "login" in crawler.driver.current_url:
                    print("❌ 로그인이 필요합니다.")
                else:
                    print("✅ 공개 접근 가능!")
                    
                    # 게시글 요소 찾기
                    try:
                        # 다양한 게시글 선택자 시도
                        article_selectors = [
                            "article",
                            ".article",
                            ".post",
                            ".list .article",
                            ".board .article",
                            "[class*='article']",
                            ".item",
                            ".list-item"
                        ]
                        
                        articles_found = 0
                        for selector in article_selectors:
                            try:
                                elements = crawler.driver.find_elements("css selector", selector)
                                if elements:
                                    print(f"게시글 요소 발견: {selector} - {len(elements)}개")
                                    articles_found = len(elements)
                                    break
                            except:
                                continue
                        
                        if articles_found == 0:
                            print("게시글 요소를 찾을 수 없습니다.")
                            
                            # HTML 소스 저장
                            filename = f"debug/board_access_{board_url.split('/')[-1]}.html"
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(crawler.driver.page_source)
                            print(f"HTML 소스 저장: {filename}")
                        
                    except Exception as e:
                        print(f"게시글 검색 오류: {e}")
                        
            except Exception as e:
                print(f"게시판 접근 오류: {e}")
        
        time.sleep(5)  # 사용자가 확인할 수 있도록 대기
        
    except Exception as e:
        print(f"테스트 실행 오류: {e}")
    
    finally:
        if crawler.driver:
            print("\n🔒 브라우저 종료...")
            crawler.driver.quit()

if __name__ == "__main__":
    test_public_access()
