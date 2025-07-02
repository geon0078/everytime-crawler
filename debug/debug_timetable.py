"""
시간표 상세 정보 추출을 위한 디버그 크롤러
"""

from everytime_crawler import EverytimeCrawler
import time

def debug_timetable_structure():
    """시간표 페이지 구조를 상세히 분석"""
    print("=== 시간표 구조 디버그 ===")
    
    with EverytimeCrawler() as crawler:
        crawler.setup_driver(headless=False)
        
        if crawler.login():
            # 시간표 페이지로 이동
            crawler.driver.get("https://everytime.kr/timetable")
            time.sleep(3)
            
            # 2025년 1학기 선택
            try:
                option = crawler.driver.find_element_by_xpath("//option[contains(text(), '2025년 1학기')]")
                option.click()
                time.sleep(3)
            except:
                print("학기 선택 실패")
            
            # 시간표 요소들 분석
            subjects = crawler.driver.find_elements_by_css_selector(".subject")
            print(f"발견된 과목 수: {len(subjects)}")
            
            for i, subject in enumerate(subjects[:3], 1):  # 처음 3개만
                print(f"\n--- 과목 {i} 분석 ---")
                print(f"전체 텍스트: {subject.text}")
                print(f"HTML: {subject.get_attribute('outerHTML')[:200]}...")
                
                # 자식 요소들 분석
                children = subject.find_elements_by_xpath("./*")
                for j, child in enumerate(children):
                    print(f"  자식 {j+1}: {child.tag_name} - '{child.text}' - class: {child.get_attribute('class')}")
            
            # 시간표 테이블도 분석
            tables = crawler.driver.find_elements_by_tag_name("table")
            print(f"\n발견된 테이블 수: {len(tables)}")
            
            for i, table in enumerate(tables[:2]):  # 처음 2개만
                rows = table.find_elements_by_tag_name("tr")
                print(f"\n테이블 {i+1}: {len(rows)}개 행")
                
                for j, row in enumerate(rows[:5]):  # 처음 5행만
                    cells = row.find_elements_by_tag_name("td")
                    if cells:
                        cell_texts = [cell.text.strip() for cell in cells]
                        print(f"  행 {j+1}: {cell_texts}")

if __name__ == "__main__":
    debug_timetable_structure()
