"""
에브리타임 크롤러 테스트 스크립트
"""

import os
import sys

def test_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트"""
    print("모듈 import 테스트 중...")
    
    try:
        import requests
        print("✓ requests 모듈 로드 성공")
    except ImportError as e:
        print(f"✗ requests 모듈 로드 실패: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup 모듈 로드 성공")
    except ImportError as e:
        print(f"✗ BeautifulSoup 모듈 로드 실패: {e}")
        return False
    
    try:
        from selenium import webdriver
        print("✓ Selenium 모듈 로드 성공")
    except ImportError as e:
        print(f"✗ Selenium 모듈 로드 실패: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ Pandas 모듈 로드 성공")
    except ImportError as e:
        print(f"✗ Pandas 모듈 로드 실패: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv 모듈 로드 성공")
    except ImportError as e:
        print(f"✗ python-dotenv 모듈 로드 실패: {e}")
        return False
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ webdriver-manager 모듈 로드 성공")
    except ImportError as e:
        print(f"✗ webdriver-manager 모듈 로드 실패: {e}")
        return False
    
    return True

def test_environment():
    """환경 설정 테스트"""
    print("\n환경 설정 테스트 중...")
    
    # .env 파일 존재 확인
    if os.path.exists('.env'):
        print("✓ .env 파일이 존재합니다")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv('EVERYTIME_ID'):
            print("✓ EVERYTIME_ID 환경변수가 설정되어 있습니다")
        else:
            print("⚠ EVERYTIME_ID 환경변수가 설정되지 않았습니다")
        
        if os.getenv('EVERYTIME_PASSWORD'):
            print("✓ EVERYTIME_PASSWORD 환경변수가 설정되어 있습니다")
        else:
            print("⚠ EVERYTIME_PASSWORD 환경변수가 설정되지 않았습니다")
    else:
        print("⚠ .env 파일이 없습니다. .env.example을 참고하여 생성해주세요")
    
    return True

def test_webdriver():
    """WebDriver 테스트"""
    print("\nWebDriver 테스트 중...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 간단한 페이지 로드 테스트
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✓ WebDriver 테스트 성공 (페이지 제목: {title})")
        return True
        
    except Exception as e:
        print(f"✗ WebDriver 테스트 실패: {e}")
        return False

def test_crawler_import():
    """크롤러 모듈 import 테스트"""
    print("\n크롤러 모듈 테스트 중...")
    
    try:
        from everytime_crawler import EverytimeCrawler
        print("✓ EverytimeCrawler 클래스 로드 성공")
        
        # 인스턴스 생성 테스트
        crawler = EverytimeCrawler()
        print("✓ EverytimeCrawler 인스턴스 생성 성공")
        
        return True
        
    except Exception as e:
        print(f"✗ 크롤러 모듈 테스트 실패: {e}")
        return False

def test_utils_import():
    """유틸리티 모듈 import 테스트"""
    print("\n유틸리티 모듈 테스트 중...")
    
    try:
        from utils import DataManager, TimetableAnalyzer, BoardAnalyzer
        print("✓ 유틸리티 클래스들 로드 성공")
        return True
        
    except Exception as e:
        print(f"✗ 유틸리티 모듈 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("=== 에브리타임 크롤러 환경 테스트 ===\n")
    
    tests = [
        ("모듈 Import 테스트", test_imports),
        ("환경 설정 테스트", test_environment),
        ("WebDriver 테스트", test_webdriver),
        ("크롤러 모듈 테스트", test_crawler_import),
        ("유틸리티 모듈 테스트", test_utils_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 실행 중 오류: {e}")
            results.append((test_name, False))
        
        print("-" * 50)
    
    # 결과 요약
    print("\n=== 테스트 결과 요약 ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 모든 테스트가 통과했습니다! 크롤러를 사용할 준비가 되었습니다.")
    else:
        print(f"\n⚠️  {total-passed}개의 테스트가 실패했습니다. 위의 오류 메시지를 확인해주세요.")
        print("\n해결 방법:")
        print("1. pip install -r requirements.txt 명령으로 패키지를 다시 설치해보세요")
        print("2. .env 파일에 올바른 계정 정보를 입력했는지 확인해주세요")
        print("3. Chrome 브라우저가 설치되어 있는지 확인해주세요")

if __name__ == "__main__":
    main()
