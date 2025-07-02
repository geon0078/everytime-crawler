#!/usr/bin/env python3
"""
.env 파일의 계정 정보로 로그인 테스트
"""

import os
import sys
import time
from dotenv import load_dotenv

# 프로젝트 루트를 파이썬 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.everytime_crawler.crawler import EverytimeCrawler

# 환경변수 로드
load_dotenv()

def test_login():
    """로그인 테스트"""
    print("🔐 에브리타임 로그인 테스트")
    print("=" * 50)
    
    # 환경변수 확인
    user_id = os.getenv('EVERYTIME_ID')
    password = os.getenv('EVERYTIME_PASSWORD')
    
    print(f"📝 계정 정보 확인:")
    print(f"   - 사용자 ID: {user_id}")
    print(f"   - 비밀번호: {'*' * len(password) if password else 'None'}")
    
    if not user_id or not password:
        print("❌ 환경변수가 설정되지 않았습니다!")
        return
    
    crawler = None
    try:
        # 크롤러 인스턴스 생성
        crawler = EverytimeCrawler()
        
        print(f"🔧 크롤러 계정 정보:")
        print(f"   - user_id: {crawler.user_id}")
        print(f"   - password: {'*' * len(crawler.password) if crawler.password else 'None'}")
        
        print("🔧 WebDriver 설정 중...")
        crawler.setup_driver(headless=False)  # 브라우저 보이도록 설정
        
        print("🔐 로그인 시도...")
        login_success = crawler.login()
        
        if login_success:
            print("✅ 로그인 성공!")
            
            # 로그인 후 메인 페이지 확인
            print("🏠 메인 페이지 상태 확인...")
            crawler.driver.get("https://everytime.kr")
            time.sleep(3)
            
            print(f"현재 URL: {crawler.driver.current_url}")
            print(f"페이지 제목: {crawler.driver.title}")
            
            # 로그인 상태 확인 (로그아웃 링크가 있는지 확인)
            try:
                logout_element = crawler.driver.find_element_by_link_text("로그아웃")
                print("✅ 로그인 상태 확인됨 (로그아웃 링크 발견)")
            except:
                print("⚠️ 로그인 상태 불확실 (로그아웃 링크 없음)")
            
            # 10초 대기하여 사용자가 확인할 수 있도록
            print("⏳ 10초 대기 중... (브라우저에서 상태 확인)")
            time.sleep(10)
            
        else:
            print("❌ 로그인 실패!")
            
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
    test_login()


if __name__ == "__main__":
    main()
