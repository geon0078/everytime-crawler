"""
에브리타임 크롤러 디버그 및 테스트 스크립트
"""

import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 환경변수 로드
load_dotenv()

def test_basic_connection():
    """기본 연결 테스트"""
    print("=== 기본 연결 테스트 ===")
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 로그 줄이기
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("WebDriver 생성 성공")
        
        # 에브리타임 메인 페이지 접속
        driver.get("https://everytime.kr")
        print(f"페이지 제목: {driver.title}")
        print(f"현재 URL: {driver.current_url}")
        
        # 페이지 로드 대기
        time.sleep(3)
        
        # 로그인 링크 찾기
        try:
            login_link = driver.find_element(By.LINK_TEXT, "로그인")
            print("로그인 링크 발견")
            login_link.click()
            time.sleep(3)
            
            print(f"로그인 페이지 URL: {driver.current_url}")
            print(f"로그인 페이지 제목: {driver.title}")
            
        except Exception as e:
            print(f"로그인 링크 클릭 실패: {e}")
            
            # 직접 로그인 페이지로 이동
            driver.get("https://everytime.kr/login")
            time.sleep(3)
            print(f"직접 로그인 페이지 이동: {driver.current_url}")
        
        # 로그인 폼 요소들 찾기
        print("\n로그인 폼 요소 검색 중...")
        
        # 모든 input 요소 찾기
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"발견된 input 요소 수: {len(inputs)}")
        
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get_attribute("type")
            input_name = input_elem.get_attribute("name")
            input_id = input_elem.get_attribute("id")
            input_placeholder = input_elem.get_attribute("placeholder")
            
            print(f"  Input {i+1}: type='{input_type}', name='{input_name}', id='{input_id}', placeholder='{input_placeholder}'")
        
        # 버튼과 submit 요소 찾기
        buttons = driver.find_elements(By.TAG_NAME, "button")
        submits = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
        
        print(f"\n발견된 button 요소 수: {len(buttons)}")
        for i, btn in enumerate(buttons):
            print(f"  Button {i+1}: text='{btn.text}', type='{btn.get_attribute('type')}'")
        
        print(f"\n발견된 submit 요소 수: {len(submits)}")
        for i, submit in enumerate(submits):
            print(f"  Submit {i+1}: value='{submit.get_attribute('value')}'")
        
        # 페이지 소스 일부 저장
        with open("everytime_login_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n페이지 소스가 everytime_login_page.html에 저장되었습니다.")
        
        # 스크린샷 저장
        driver.save_screenshot("everytime_login_page.png")
        print("스크린샷이 everytime_login_page.png에 저장되었습니다.")
        
        driver.quit()
        print("\n기본 연결 테스트 완료")
        
    except Exception as e:
        print(f"기본 연결 테스트 실패: {e}")
        if 'driver' in locals():
            driver.quit()

def test_manual_login():
    """수동 로그인 테스트"""
    print("\n=== 수동 로그인 테스트 ===")
    
    user_id = os.getenv('EVERYTIME_ID')
    password = os.getenv('EVERYTIME_PASSWORD')
    
    if not user_id or not password:
        print("환경변수 EVERYTIME_ID와 EVERYTIME_PASSWORD를 설정해주세요.")
        return
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 헤드리스 모드 비활성화 (디버깅용)
    # chrome_options.add_argument("--headless")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 로그인 페이지로 이동
        driver.get("https://everytime.kr/login")
        time.sleep(3)
        
        print("로그인 페이지 로드 완료")
        print("브라우저에서 수동으로 로그인을 시도해보세요.")
        print("30초 후 자동으로 종료됩니다...")
        
        # 30초 대기
        time.sleep(30)
        
        # 현재 상태 확인
        print(f"최종 URL: {driver.current_url}")
        print(f"최종 제목: {driver.title}")
        
        driver.quit()
        
    except Exception as e:
        print(f"수동 로그인 테스트 실패: {e}")
        if 'driver' in locals():
            driver.quit()

def test_requests_session():
    """requests를 사용한 로그인 테스트"""
    print("\n=== Requests 세션 로그인 테스트 ===")
    
    import requests
    from bs4 import BeautifulSoup
    
    user_id = os.getenv('EVERYTIME_ID')
    password = os.getenv('EVERYTIME_PASSWORD')
    
    if not user_id or not password:
        print("환경변수를 설정해주세요.")
        return
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    try:
        # 로그인 페이지 가져오기
        response = session.get("https://everytime.kr/login")
        print(f"로그인 페이지 상태 코드: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 폼 분석
        forms = soup.find_all('form')
        print(f"발견된 폼 수: {len(forms)}")
        
        for i, form in enumerate(forms):
            print(f"  폼 {i+1}: action='{form.get('action')}', method='{form.get('method')}'")
            
            inputs = form.find_all('input')
            for input_elem in inputs:
                input_type = input_elem.get('type')
                input_name = input_elem.get('name')
                print(f"    Input: type='{input_type}', name='{input_name}'")
        
        # HTML 저장
        with open("everytime_requests_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("requests로 가져온 페이지가 everytime_requests_page.html에 저장되었습니다.")
        
    except Exception as e:
        print(f"Requests 테스트 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("에브리타임 크롤러 디버그 테스트")
    print("=" * 50)
    
    # 환경변수 확인
    user_id = os.getenv('EVERYTIME_ID')
    password = os.getenv('EVERYTIME_PASSWORD')
    
    if user_id:
        print(f"EVERYTIME_ID: {user_id[:3]}***")
    else:
        print("EVERYTIME_ID: 설정되지 않음")
    
    if password:
        print(f"EVERYTIME_PASSWORD: {'*' * len(password)}")
    else:
        print("EVERYTIME_PASSWORD: 설정되지 않음")
    
    print("\n어떤 테스트를 실행하시겠습니까?")
    print("1. 기본 연결 테스트")
    print("2. 수동 로그인 테스트")
    print("3. Requests 세션 테스트")
    print("4. 모든 테스트")
    
    choice = input("선택 (1-4): ").strip()
    
    if choice == "1":
        test_basic_connection()
    elif choice == "2":
        test_manual_login()
    elif choice == "3":
        test_requests_session()
    elif choice == "4":
        test_basic_connection()
        test_manual_login()
        test_requests_session()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()
