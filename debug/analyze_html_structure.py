#!/usr/bin/env python3
"""
에브리타임 게시판 HTML 구조 분석 스크립트
"""

import sys
import os
from dotenv import load_dotenv

# 프로젝트 루트를 파이썬 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 환경변수 로드
load_dotenv()

from src.everytime_crawler.crawler import EverytimeCrawler
from bs4 import BeautifulSoup
import time


def analyze_board_html():
    """게시판 HTML 구조 분석"""
    print("🔍 에브리타임 게시판 HTML 구조 분석")
    print("=" * 50)
    
    crawler = EverytimeCrawler()
    
    try:
        print("🔧 WebDriver 설정 중...")
        crawler.setup_driver(headless=False)
        
        print("🔐 로그인 시도...")
        if not crawler.login():
            print("❌ 로그인 실패!")
            return
        
        print("✅ 로그인 성공!")
        
        # 자유게시판 분석
        board_url = "https://everytime.kr/387605"
        print(f"\n📋 게시판 페이지 분석: {board_url}")
        
        crawler.driver.get(board_url)
        time.sleep(5)
        
        # 페이지 HTML 저장
        html_content = crawler.driver.page_source
        with open("debug/board_html_analysis.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("💾 HTML 내용을 debug/board_html_analysis.html에 저장")
        
        # BeautifulSoup으로 분석
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 가능한 게시글 요소들 찾기
        print("\n🔍 게시글 요소 분석:")
        
        # article 태그 분석
        articles = soup.find_all('article')
        print(f"📄 article 태그: {len(articles)}개")
        if articles:
            first_article = articles[0]
            print("첫 번째 article의 클래스:", first_article.get('class'))
            print("첫 번째 article 내용 미리보기:")
            print(first_article.prettify()[:500])
            
        # a 태그 (링크) 분석
        links = soup.find_all('a', href=True)
        board_links = [link for link in links if '/v/' in link.get('href', '')]
        print(f"\n🔗 게시글 링크: {len(board_links)}개")
        if board_links:
            print("첫 번째 게시글 링크:")
            print(board_links[0].prettify()[:300])
            
        # 제목이 포함될 수 있는 요소들 찾기
        print("\n📝 제목 요소 분석:")
        potential_titles = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"제목 태그들: {len(potential_titles)}개")
        for i, title in enumerate(potential_titles[:5]):
            print(f"  {i+1}. {title.name}: {title.get_text(strip=True)[:50]}")
            
        # 클래스명 분석
        print("\n🏷️ 주요 클래스명 분석:")
        all_elements = soup.find_all(class_=True)
        class_names = set()
        for elem in all_elements:
            classes = elem.get('class', [])
            class_names.update(classes)
        
        relevant_classes = [cls for cls in class_names if any(keyword in cls.lower() 
                          for keyword in ['title', 'subject', 'article', 'post', 'content', 'text'])]
        print("관련 클래스명들:", sorted(relevant_classes))
        
        print("\n✅ HTML 구조 분석 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler.driver:
            print("\n🔒 브라우저 종료...")
            crawler.close()


if __name__ == "__main__":
    analyze_board_html()
