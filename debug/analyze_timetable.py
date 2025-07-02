"""
에브리타임 시간표 API 분석 및 실제 데이터 추출
"""

from everytime_crawler import EverytimeCrawler
from selenium.webdriver.common.by import By
import time
import json

def analyze_timetable_api():
    """시간표 API를 분석하여 실제 데이터 추출"""
    print("=== 시간표 API 분석 ===")
    
    with EverytimeCrawler() as crawler:
        crawler.setup_driver(headless=False)
        
        if crawler.login():
            # 시간표 페이지로 이동
            crawler.driver.get("https://everytime.kr/timetable")
            time.sleep(3)
            
            # 2025년 1학기 선택
            try:
                semester_select = crawler.driver.find_element(By.ID, "semesters")
                semester_select.click()
                time.sleep(1)
                
                option = crawler.driver.find_element(By.XPATH, "//option[contains(text(), '2025년 1학기')]")
                option.click()
                time.sleep(5)  # 데이터 로딩 대기
                
                print("2025년 1학기 선택 완료")
                
            except Exception as e:
                print(f"학기 선택 실패: {e}")
            
            # 페이지가 완전히 로드될 때까지 더 기다리기
            time.sleep(5)
            
            # JavaScript를 사용하여 시간표 데이터 추출
            try:
                # 1. subjects div 내용 확인
                subjects_div = crawler.driver.find_element(By.ID, "subjects")
                print(f"subjects div HTML: {subjects_div.get_attribute('innerHTML')[:500]}...")
                
                # 2. 시간표 테이블에서 실제 과목 요소들 찾기
                table_subjects = crawler.driver.find_elements(By.CSS_SELECTOR, ".tablebody .subject")
                print(f"테이블에서 발견된 과목 수: {len(table_subjects)}")
                
                # 3. JavaScript 변수 확인
                grid_info = crawler.driver.execute_script("return window._timetableGridInfo || [];")
                print(f"_timetableGridInfo: {grid_info}")
                
                # 4. 모든 possible 클래스로 시간표 요소 찾기
                possible_classes = [
                    ".subject", ".course", ".lecture", ".class-item",
                    "[data-subject]", "[data-course]", ".timetable-item",
                    "div[style*='position: absolute']"  # 절대 위치 요소들
                ]
                
                for class_name in possible_classes:
                    elements = crawler.driver.find_elements(By.CSS_SELECTOR, class_name)
                    if elements:
                        print(f"'{class_name}' 클래스로 {len(elements)}개 요소 발견")
                        
                        for i, elem in enumerate(elements[:3]):  # 처음 3개만
                            print(f"  요소 {i+1}: {elem.text}")
                            print(f"  HTML: {elem.get_attribute('outerHTML')[:200]}...")
                
                # 5. 시간표 테이블 내 모든 텍스트 요소 분석
                table = crawler.driver.find_element(By.CSS_SELECTOR, ".tablebody")
                all_divs = table.find_elements(By.TAG_NAME, "div")
                
                print(f"\n테이블 내 div 요소 수: {len(all_divs)}")
                text_divs = [div for div in all_divs if div.text.strip() and len(div.text.strip()) > 2]
                print(f"텍스트가 있는 div 수: {len(text_divs)}")
                
                for i, div in enumerate(text_divs[:10]):  # 처음 10개만
                    print(f"  텍스트 div {i+1}: '{div.text}' - class: {div.get_attribute('class')}")
                
                # 6. 네트워크 요청 로그 확인 (개발자 도구)
                print("\n페이지에서 AJAX 요청을 기다리는 중...")
                time.sleep(3)
                
                # 7. 새로고침 후 다시 확인
                crawler.driver.refresh()
                time.sleep(10)
                
                # 다시 과목 검색
                subjects_after_refresh = crawler.driver.find_elements(By.CSS_SELECTOR, ".subject")
                print(f"새로고침 후 발견된 과목 수: {len(subjects_after_refresh)}")
                
                for i, subject in enumerate(subjects_after_refresh):
                    print(f"과목 {i+1}: {subject.text}")
                    print(f"HTML: {subject.get_attribute('outerHTML')}")
                
            except Exception as e:
                print(f"시간표 분석 중 오류: {e}")

if __name__ == "__main__":
    analyze_timetable_api()
