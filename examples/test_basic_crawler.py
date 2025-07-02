#!/usr/bin/env python3
"""
로그인 없이 공개 정보만 크롤링하는 테스트 스크립트
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 프로젝트 루트를 파이썬 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.everytime_crawler.crawler import EverytimeCrawler


def test_crawler_without_login():
    """로그인 없이 크롤러 기본 기능 테스트"""
    print("🧪 에브리타임 크롤러 테스트 (로그인 없음)")
    print("=" * 50)
    
    crawler = None
    try:
        # 크롤러 인스턴스 생성
        crawler = EverytimeCrawler()
        
        print("🔧 WebDriver 설정 중...")
        crawler.setup_driver(headless=False)  # 브라우저 보이도록 설정
        
        # 메인 페이지 접속 테스트
        print("🌐 메인 페이지 접속 테스트...")
        crawler.driver.get("https://everytime.kr")
        time.sleep(3)
        
        print(f"현재 페이지: {crawler.driver.current_url}")
        print(f"페이지 제목: {crawler.driver.title}")
        
        # 페이지 로딩 확인
        if "에브리타임" in crawler.driver.title:
            print("✅ 메인 페이지 접속 성공!")
        else:
            print("❌ 메인 페이지 접속 실패")
            
        # 몇 초 대기하여 페이지 확인
        print("⏳ 페이지 확인을 위해 5초 대기...")
        time.sleep(5)
        
        print("✅ 기본 크롤러 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("🔒 브라우저 종료...")
        if crawler and crawler.driver:
            crawler.close()


def main():
    """메인 함수"""
    test_crawler_without_login()


if __name__ == "__main__":
    main()
