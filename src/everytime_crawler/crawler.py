"""
에브리타임 크롤러 메인 모듈
"""

import os
import time
import json
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class EverytimeCrawler:
    def __init__(self):
        """에브리타임 크롤러 초기화"""
        # 환경변수 다시 로드 (확실하게)
        load_dotenv(override=True)
        
        self.base_url = "https://everytime.kr"
        self.session = requests.Session()
        self.driver = None
        
        # 환경변수에서 계정 정보 로드
        self.user_id = os.getenv('EVERYTIME_ID')
        self.password = os.getenv('EVERYTIME_PASSWORD')
        
        # 디버그: 환경변수 확인
        print(f"🔍 크롤러 초기화 - 계정 정보:")
        print(f"   - user_id: {self.user_id}")
        print(f"   - password: {'*' * len(self.password) if self.password else 'None'}")
        
    def setup_driver(self, headless=True):
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # 안정성을 위한 추가 옵션들
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 로그 레벨 설정
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # ChromeDriverManager 사용 시도
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"ChromeDriverManager 실패: {e}")
                # 시스템 PATH에서 chromedriver 찾기 시도
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                except Exception as e2:
                    print(f"시스템 chromedriver 실패: {e2}")
                    # 마지막 시도: 직접 다운로드된 chromedriver 경로 지정
                    import shutil
                    chromedriver_path = shutil.which('chromedriver')
                    if chromedriver_path:
                        service = Service(chromedriver_path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        raise Exception("ChromeDriver를 찾을 수 없습니다. Chrome 브라우저와 호환되는 ChromeDriver를 설치해주세요.")
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("WebDriver 설정 완료")
            return self.driver
            
        except Exception as e:
            print(f"WebDriver 설정 실패: {e}")
            raise
    
    def login(self):
        """에브리타임 로그인"""
        if not self.user_id or not self.password:
            raise ValueError("환경변수에 EVERYTIME_ID와 EVERYTIME_PASSWORD를 설정해주세요.")
            
        try:
            print("에브리타임 로그인 시도 중...")
            
            # 메인 페이지에서 시작 (더 자연스러운 접근)
            self.driver.get("https://everytime.kr")
            print("메인 페이지 로드 완료")
            time.sleep(3)
            
            # 로그인 링크 찾기 및 클릭
            try:
                # 다양한 방법으로 로그인 링크 찾기
                login_link = None
                selectors = [
                    "//a[contains(text(), '로그인')]",
                    "//a[@href='/login']",
                    "//a[contains(@href, 'login')]",
                    ".header a[href*='login']"
                ]
                
                for selector in selectors:
                    try:
                        if selector.startswith("//"):
                            login_link = self.driver.find_element(By.XPATH, selector)
                        else:
                            login_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if login_link:
                    self.driver.execute_script("arguments[0].click();", login_link)
                    print("로그인 링크 클릭 완료")
                    time.sleep(3)
                else:
                    # 직접 로그인 페이지로 이동
                    self.driver.get("https://account.everytime.kr/login")
                    time.sleep(3)
                    
            except:
                # 직접 로그인 페이지로 이동
                self.driver.get("https://account.everytime.kr/login")
                time.sleep(3)
            
            print(f"현재 URL: {self.driver.current_url}")
            
            # 페이지가 완전히 로드될 때까지 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "id"))
            )
            
            # 로그인 폼 입력 필드 찾기
            userid_input = self.driver.find_element(By.NAME, "id")
            password_input = self.driver.find_element(By.NAME, "password")
            
            print("로그인 폼 찾기 성공")
            
            # 입력 필드 클리어 및 천천히 입력 (사람처럼)
            userid_input.clear()
            time.sleep(0.5)
            for char in self.user_id:
                userid_input.send_keys(char)
                time.sleep(0.1)  # 천천히 타이핑
            
            time.sleep(1)
            
            password_input.clear()
            time.sleep(0.5)
            for char in self.password:
                password_input.send_keys(char)
                time.sleep(0.1)  # 천천히 타이핑
            
            time.sleep(2)
            print("로그인 정보 입력 완료")
            
            # 로그인 버튼 찾기 및 클릭
            login_button = None
            button_selectors = [
                "//input[@type='submit' and @value='에브리타임 로그인']",
                "//input[@type='submit']",
                "//button[contains(text(), '로그인')]",
                ".submit",
                "input[type='submit']"
            ]
            
            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if login_button:
                # JavaScript로 클릭 (더 안정적)
                self.driver.execute_script("arguments[0].click();", login_button)
                print("로그인 버튼 클릭 완료")
            else:
                # Enter 키로 로그인 시도
                password_input.send_keys(Keys.RETURN)
                print("Enter 키로 로그인 시도")
            
            # 로그인 결과 확인
            time.sleep(3)
            
            # Alert 확인
            try:
                # Alert가 나타날 때까지 대기 (짧은 시간)
                WebDriverWait(self.driver, 2).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                print(f"로그인 실패: Alert Text: {alert_text}")
                alert.accept()  # Alert 닫기
                return False
            except:
                # Alert가 없으면 로그인 성공 가능성
                pass
            
            # 추가 대기 후 URL 확인
            time.sleep(2)
            current_url = self.driver.current_url
            print(f"로그인 후 URL: {current_url}")
            
            # 로그인 성공 확인 - 메인 페이지로 리다이렉트되면 성공
            if current_url == "https://everytime.kr/" or ("everytime.kr" in current_url and "login" not in current_url and "account" not in current_url):
                print("로그인에 성공했습니다.")
                return True
            else:
                print("로그인에 실패했습니다.")
                return False
            
        except Exception as e:
            print(f"로그인 실패: {e}")
            # 스크린샷 저장
            try:
                self.driver.save_screenshot("login_error_screenshot.png")
                print("오류 스크린샷이 login_error_screenshot.png로 저장되었습니다.")
            except:
                pass
            return False
    
    def get_timetable(self, year=2025, semester=1, save_to_file=True):
        """시간표 정보 수집"""
        try:
            print("시간표 페이지로 이동 중...")
            # 시간표 페이지로 이동
            self.driver.get(f"{self.base_url}/timetable")
            time.sleep(3)
            
            print(f"시간표 페이지 URL: {self.driver.current_url}")
            print(f"시간표 페이지 제목: {self.driver.title}")
            
            # 좌측 학기 선택 영역에서 해당 학기 찾기 및 클릭
            try:
                semester_text = f"{year}년 {semester}학기"
                print(f"'{semester_text}' 선택 시도 중...")
                
                # 학기 선택을 위한 다양한 선택자 시도
                semester_selectors = [
                    f"//a[contains(text(), '{semester_text}')]",
                    f"//div[contains(text(), '{semester_text}')]",
                    f"//span[contains(text(), '{semester_text}')]",
                    f"//li[contains(text(), '{semester_text}')]",
                    f"//button[contains(text(), '{semester_text}')]",
                    f"//option[contains(text(), '{semester_text}')]"
                ]
                
                semester_element = None
                for selector in semester_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            semester_element = elements[0]
                            print(f"학기 선택 요소 발견: {selector}")
                            break
                    except:
                        continue
                
                if semester_element:
                    # 클릭 가능할 때까지 대기
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable(semester_element)
                        )
                        semester_element.click()
                        print(f"'{semester_text}' 선택 완료")
                        time.sleep(3)  # 페이지 로딩 대기
                    except Exception as click_error:
                        print(f"학기 선택 클릭 오류: {click_error}")
                        # JavaScript로 클릭 시도
                        try:
                            self.driver.execute_script("arguments[0].click();", semester_element)
                            print(f"JavaScript로 '{semester_text}' 선택 완료")
                            time.sleep(3)
                        except:
                            print("JavaScript 클릭도 실패")
                else:
                    print(f"'{semester_text}' 선택 요소를 찾을 수 없습니다.")
                    
                    # 현재 페이지의 시간표 관련 링크들 출력
                    print("사용 가능한 학기/시간표 관련 링크들:")
                    time_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'timetable') or contains(text(), '학기') or contains(text(), '년')]")
                    for i, link in enumerate(time_links[:10]):  # 처음 10개만
                        try:
                            print(f"  {i+1}. {link.text.strip()} - {link.get_attribute('href')}")
                        except:
                            pass
                            
            except Exception as e:
                print(f"학기 선택 중 오류: {e}")
                print("기본 시간표를 사용합니다.")
            
            # 시간표 데이터 추출
            timetable_data = []
            
            # 다양한 시간표 셀렉터 시도
            selectors = [
                ".subject",
                ".course", 
                ".lecture",
                ".timetable-subject",
                ".class",
                "tr.course",
                ".schedule-item",
                ".timetable .subject",
                "[class*='subject']",
                "[class*='course']"
            ]
            
            timetable_elements = []
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"시간표 요소를 '{selector}' 셀렉터로 {len(elements)}개 발견")
                    timetable_elements = elements
                    break
            
            if not timetable_elements:
                print("시간표 요소를 찾을 수 없습니다. 페이지 구조를 분석합니다...")
                
                # 페이지 소스 저장
                with open("timetable_debug.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("시간표 페이지가 timetable_debug.html에 저장되었습니다.")
                
                # 스크린샷 저장
                self.driver.save_screenshot("timetable_debug.png")
                print("시간표 스크린샷이 timetable_debug.png에 저장되었습니다.")
                
                # 테이블 요소 찾기
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                print(f"테이블 요소 {len(tables)}개 발견")
                
                for i, table in enumerate(tables):
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    print(f"  테이블 {i+1}: {len(rows)}개 행")
                    
                    if len(rows) > 1:  # 헤더가 있는 테이블
                        for j, row in enumerate(rows[:3]):  # 처음 3행만 출력
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if cells:
                                cell_texts = [cell.text.strip() for cell in cells if cell.text.strip()]
                                if cell_texts:
                                    print(f"    행 {j+1}: {cell_texts}")
                
                return timetable_data
            
            # 시간표 데이터 파싱
            for element in timetable_elements:
                try:
                    # 과목 정보 추출
                    subject_info = {}
                    
                    # 과목명 추출 (h3 태그)
                    try:
                        subject_name_elem = element.find_element(By.TAG_NAME, "h3")
                        subject_info['subject_name'] = subject_name_elem.text.strip()
                    except:
                        subject_info['subject_name'] = "알 수 없음"
                    
                    # p 태그 내에서 교수명과 강의실 추출
                    try:
                        p_elem = element.find_element(By.TAG_NAME, "p")
                        
                        # 교수명 (em 태그)
                        try:
                            professor_elem = p_elem.find_element(By.TAG_NAME, "em")
                            subject_info['professor'] = professor_elem.text.strip()
                        except:
                            subject_info['professor'] = "교수 정보 없음"
                        
                        # 강의실 (span 태그)
                        try:
                            room_elem = p_elem.find_element(By.TAG_NAME, "span")
                            subject_info['room'] = room_elem.text.strip() if room_elem.text.strip() else "강의실 정보 없음"
                        except:
                            subject_info['room'] = "강의실 정보 없음"
                            
                    except:
                        subject_info['professor'] = "교수 정보 없음"
                        subject_info['room'] = "강의실 정보 없음"
                    
                    # 시간 정보 추출 (style 속성에서)
                    try:
                        style_attr = element.get_attribute("style")
                        time_info = self.parse_time_from_style(style_attr)
                        subject_info['time'] = time_info
                    except:
                        subject_info['time'] = "시간 정보 없음"
                    
                    # 기본값 설정
                    subject_data = {
                        'subject_name': subject_info.get('subject_name', '알 수 없음'),
                        'time': subject_info.get('time', '시간 정보 없음'),
                        'room': subject_info.get('room', '강의실 정보 없음'),
                        'professor': subject_info.get('professor', '교수 정보 없음'),
                        'year': year,
                        'semester': semester,
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    # 유효한 데이터만 추가
                    if subject_data['subject_name'] != '알 수 없음':
                        timetable_data.append(subject_data)
                        print(f"과목 추가: {subject_data['subject_name']} - {subject_data['professor']} - {subject_data['room']} - {subject_data['time']}")
                    
                except Exception as e:
                    print(f"시간표 항목 파싱 오류: {e}")
                    continue
            
            if save_to_file and timetable_data:
                # DataFrame으로 변환 후 CSV 저장
                df = pd.DataFrame(timetable_data)
                filename = f"timetable_{year}_{semester}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"시간표 데이터가 {filename}에 저장되었습니다.")
            
            return timetable_data
            
        except Exception as e:
            print(f"시간표 수집 오류: {e}")
            return []
            
        except Exception as e:
            print(f"시간표 수집 오류: {e}")
            return []
    
    def get_board_posts(self, board_id="free", pages=3, delay=2):
        """
        게시판 글 목록 크롤링 (개선된 버전)
        
        Args:
            board_id (str): 게시판 ID (free, secret, freshman 등)
            pages (int): 크롤링할 페이지 수
            delay (int): 페이지 간 대기 시간(초)
            
        Returns:
            list: 게시글 정보 리스트
        """
        # 실제 에브리타임 게시판 URL 매핑 (성남캠 기준)
        board_url_map = {
            "free": "387605",        # 성남캠 자유게시판
            "secret": "375151",      # 비밀게시판
            "graduate": "387612",    # 졸업생게시판
            "freshman": "387615",    # 새내기게시판
        }
        
        board_name_map = {
            "free": "자유게시판",
            "secret": "비밀게시판", 
            "freshman": "새내기게시판",
            "graduate": "졸업생게시판",
        }
        
        if board_id not in board_url_map:
            print(f"❌ 지원하지 않는 게시판: {board_id}")
            print(f"📝 지원하는 게시판: {list(board_url_map.keys())}")
            return []
        
        board_name = board_name_map.get(board_id, board_id)
        board_number = board_url_map[board_id]
        
        print(f"🔍 '{board_name}' 게시판 크롤링 시작...")
        print(f"🌐 게시판 URL: https://everytime.kr/{board_number}")
        
        all_posts = []
        
        try:
            # 게시판 페이지로 이동
            board_url = f"{self.base_url}/{board_number}"
            self.driver.get(board_url)
            time.sleep(3)
            
            print(f"📍 현재 URL: {self.driver.current_url}")
            
            for page in range(1, pages + 1):
                print(f"📄 페이지 {page}/{pages} 크롤링 중...")
                
                # 페이지 이동 (첫 페이지가 아닌 경우)
                if page > 1:
                    page_url = f"{board_url}?page={page}"
                    self.driver.get(page_url)
                    time.sleep(delay)
                
                # 페이지의 게시글 추출
                posts = self._extract_posts_from_current_page(board_id, page)
                all_posts.extend(posts)
                
                print(f"✅ 페이지 {page}에서 {len(posts)}개 게시글 수집")
                
        except Exception as e:
            print(f"❌ 게시판 크롤링 중 오류 발생: {e}")
            self._save_board_debug_info(board_id)
        
        print(f"🎉 총 {len(all_posts)}개 게시글 수집 완료!")
        return all_posts
    
    def _extract_posts_from_current_page(self, board_id, page_num):
        """현재 페이지에서 게시글 정보 추출"""
        posts = []
        
        try:
            # 페이지 로딩 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 에브리타임 게시판 구조 분석을 위한 다양한 셀렉터 시도
            post_selectors = [
                "article.list",           # 일반적인 게시글 구조
                ".article",               # 기본 article 클래스
                "tr.list",               # 테이블 형태 게시판
                ".board-item",           # 커스텀 게시판 아이템
                ".post-item",            # 포스트 아이템
                ".content-wrapper a",    # 링크 형태 게시글
                ".list-item"             # 리스트 아이템
            ]
            
            post_elements = []
            used_selector = None
            
            for selector in post_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    post_elements = elements
                    used_selector = selector
                    print(f"✅ '{selector}' 셀렉터로 {len(elements)}개 요소 발견")
                    break
            
            if not post_elements:
                print("⚠️ 게시글 요소를 찾을 수 없습니다.")
                return posts
            
            # 각 게시글에서 정보 추출
            for idx, element in enumerate(post_elements[:20]):  # 상위 20개만 처리
                try:
                    post_info = self._extract_single_post_info(element, used_selector)
                    if post_info:
                        post_info['board_id'] = board_id
                        post_info['page'] = page_num
                        post_info['collected_at'] = datetime.now().isoformat()
                        posts.append(post_info)
                
                except Exception as e:
                    print(f"⚠️ 게시글 {idx+1} 추출 중 오류: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ 페이지 파싱 중 오류: {e}")
        
        return posts
    
    def _extract_single_post_info(self, element, selector_used):
        """개별 게시글에서 정보 추출 (에브리타임 최신 구조에 최적화)"""
        post_info = {}
        
        try:
            # BeautifulSoup으로 더 정확한 파싱
            soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
            
            # 에브리타임 실제 구조에 맞는 제목 추출
            # <h2 class="medium bold">제목</h2>
            title = "제목 없음"
            title_elem = soup.select_one('h2.medium.bold')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # 대체 제목 셀렉터 시도
            if not title or title == "제목 없음":
                alt_selectors = ['.title', '.subject', 'h3', 'h4', '.article-title']
                for sel in alt_selectors:
                    elem = soup.select_one(sel)
                    if elem and elem.get_text(strip=True):
                        title = elem.get_text(strip=True)
                        break
            
            # 내용 추출
            # <p class="medium">내용</p>
            content = ""
            content_elem = soup.select_one('p.medium')
            if content_elem:
                content = content_elem.get_text(strip=True)
                # <br> 태그를 공백으로 변환
                content = content.replace('\n', ' ').replace('\r', '')
            
            # 작성자 추출  
            # <h3 class="small">익명</h3>
            author = "익명"
            author_elem = soup.select_one('h3.small')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # 작성시간 추출
            # <time class="small">3분 전</time>
            created_time = ""
            time_elem = soup.select_one('time.small')
            if time_elem:
                created_time = time_elem.get_text(strip=True)
            
            # 댓글 수 추출
            # <li title="댓글" class="comment">2</li>
            comment_count = "0"
            comment_elem = soup.select_one('li.comment')
            if comment_elem:
                comment_count = comment_elem.get_text(strip=True)
            
            # 조회수 추출 (있는 경우)
            view_count = None
            view_elem = soup.select_one('li.view')
            if view_elem:
                view_count = view_elem.get_text(strip=True)
            
            # 게시글 링크 추출
            # <a class="article" href="/387605/v/384508581">
            post_link = None
            link_elem = soup.select_one('a.article[href]')
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if href.startswith('/'):
                        post_link = f"{self.base_url}{href}"
                    else:
                        post_link = href
            
            # 게시글 정보 구성
            post_info = {
                'title': title,
                'content': content,
                'author': author,
                'created_time': created_time,
                'comment_count': comment_count,
                'view_count': view_count,
                'post_link': post_link,
                'selector_used': selector_used
            }
            
            return post_info
            
        except Exception as e:
            print(f"⚠️ 게시글 파싱 중 오류: {e}")
            return None
            
            # 조회수 추출 (있는 경우)
            view_selectors = [
                '.view',
                '.views',
                '.hit',
                '.read-count'
            ]
            
            view_count = None
            for view_sel in view_selectors:
                view_elem = soup.select_one(view_sel)
                if view_elem:
                    view_text = view_elem.get_text(strip=True)
                    import re
                    numbers = re.findall(r'\d+', view_text)
                    if numbers:
                        view_count = numbers[0]
                        break
            
            # 최소한 제목이 있는 경우만 반환
            if title and len(title) > 1:
                post_info = {
                    'title': title,
                    'author': author,
                    'created_time': created_time,
                    'comment_count': comment_count,
                    'view_count': view_count,
                    'post_link': post_link,
                    'selector_used': selector_used
                }
                
                return post_info
        
        except Exception as e:
            print(f"⚠️ 게시글 정보 추출 중 오류: {e}")
        
        return None
    
    def get_post_detail(self, post_url):
        """
        개별 게시글의 상세 정보 크롤링 (댓글 포함)
        
        Args:
            post_url (str): 게시글 URL
            
        Returns:
            dict: 게시글 상세 정보
        """
        try:
            print(f"📖 게시글 상세 정보 크롤링: {post_url}")
            
            self.driver.get(post_url)
            time.sleep(3)  # 페이지 로딩 대기
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 게시글 제목 추출
            title = ""
            title_selectors = ['h1', 'h2.large', '.title', '.subject']
            for title_sel in title_selectors:
                title_elem = soup.select_one(title_sel)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title:
                        break
            
            # 게시글 내용 추출 (에브리타임 구조에 맞게)
            content = ""
            content_selectors = [
                '.large',  # 에브리타임 게시글 본문
                '.content',
                '.article-content', 
                '.post-content',
                '.text',
                '.body'
            ]
            
            for content_sel in content_selectors:
                content_elem = soup.select_one(content_sel)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    if content and len(content) > 5:
                        break
            
            # 댓글 추출 (에브리타임 구조 분석)
            comments = []
            
            # 에브리타임 댓글 구조: <ul class="comments"> 내의 <li> 요소들
            comment_list = soup.select_one('ul.comments')
            if comment_list:
                comment_items = comment_list.select('li')
                for item in comment_items:
                    comment_data = self._extract_comment_info(item)
                    if comment_data:
                        comments.append(comment_data)
            
            # 대체 댓글 셀렉터
            if not comments:
                alt_selectors = [
                    '.comment',
                    '.reply',
                    '.comment-item',
                    '.reply-item',
                    '[class*="comment"]'
                ]
                
                for selector in alt_selectors:
                    comment_elems = soup.select(selector)
                    if comment_elems:
                        for elem in comment_elems:
                            comment_data = self._extract_comment_info(elem)
                            if comment_data:
                                comments.append(comment_data)
                        if comments:
                            break
            
            detail_info = {
                'url': post_url,
                'title': title,
                'content': content,
                'comments': comments,
                'comment_count': len(comments),
                'collected_at': datetime.now().isoformat()
            }
            
            print(f"✅ 게시글 상세 정보 수집 완료 (댓글 {len(comments)}개)")
            return detail_info
            
        except Exception as e:
            print(f"❌ 게시글 상세 정보 크롤링 실패: {e}")
            return None
    
    def _extract_comment_info(self, comment_element):
        """댓글 정보 추출"""
        try:
            soup = BeautifulSoup(str(comment_element), 'html.parser')
            
            # 댓글 내용
            content = ""
            content_selectors = ['.large', 'p', '.text', '.content']
            for sel in content_selectors:
                elem = soup.select_one(sel)
                if elem:
                    content = elem.get_text(strip=True)
                    if content:
                        break
            
            # 작성자
            author = "익명"
            author_selectors = ['.small', '.author', '.writer', '.nickname']
            for sel in author_selectors:
                elem = soup.select_one(sel)
                if elem:
                    text = elem.get_text(strip=True)
                    if text and not text.isdigit() and '분' not in text and ':' not in text:
                        author = text
                        break
            
            # 작성시간
            created_time = ""
            time_selectors = ['time', '.time', '.date', '.timestamp']
            for sel in time_selectors:
                elem = soup.select_one(sel)
                if elem:
                    created_time = elem.get_text(strip=True)
                    if created_time:
                        break
            
            if content and len(content) > 1:
                return {
                    'content': content,
                    'author': author,
                    'created_time': created_time
                }
            
        except Exception as e:
            print(f"⚠️ 댓글 파싱 오류: {e}")
        
        return None
    
    def save_board_posts_to_csv(self, posts, filename=None):
        """게시글 목록을 CSV 파일로 저장"""
        if not posts:
            print("⚠️ 저장할 게시글이 없습니다.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            board_id = posts[0].get('board_id', 'unknown')
            filename = f"data/board_{board_id}_{timestamp}.csv"
        
        try:
            df = pd.DataFrame(posts)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"💾 게시글 {len(posts)}개가 '{filename}'에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ CSV 저장 중 오류: {e}")
    
    def save_board_posts_to_json(self, posts, filename=None):
        """게시글 목록을 JSON 파일로 저장"""
        if not posts:
            print("⚠️ 저장할 게시글이 없습니다.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            board_id = posts[0].get('board_id', 'unknown')
            filename = f"data/board_{board_id}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            print(f"💾 게시글 {len(posts)}개가 '{filename}'에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ JSON 저장 중 오류: {e}")
    
    def _save_board_debug_info(self, board_id):
        """디버깅을 위한 페이지 정보 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_filename = f"debug/board_{board_id}_debug_{timestamp}.html"
            
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print(f"🔧 디버그 정보가 '{debug_filename}'에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 디버그 정보 저장 중 오류: {e}")

    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
    
    def quit(self):
        """드라이버 종료 (close와 동일)"""
        self.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def parse_time_from_style(self, style_attr):
        """CSS style 속성에서 시간 정보 파싱"""
        try:
            # style="height: 181px; top: 540px;" 형태에서 top 값 추출
            import re
            
            top_match = re.search(r'top:\s*(\d+)px', style_attr)
            height_match = re.search(r'height:\s*(\d+)px', style_attr)
            
            if not top_match or not height_match:
                return "시간 정보 없음"
            
            top_px = int(top_match.group(1))
            height_px = int(height_match.group(1))
            
            # 에브리타임 시간표에서 1시간 = 약 60px (추정)
            # top 값을 기준으로 시작 시간 계산
            # 일반적으로 오전 8시부터 시작한다고 가정 (top=480 정도가 오전 8시)
            
            # 시간 계산 (대략적인 값)
            base_top = 480  # 오전 8시 기준
            hour_height = 60  # 1시간당 픽셀
            
            start_hour = 8 + ((top_px - base_top) // hour_height)
            duration_hours = height_px // hour_height
            end_hour = start_hour + duration_hours
            
            # 시간 포맷팅
            def format_hour(hour):
                if hour < 12:
                    return f"오전 {hour}시"
                elif hour == 12:
                    return "오후 12시"
                else:
                    return f"오후 {hour-12}시"
            
            if start_hour >= 0 and end_hour >= start_hour:
                return f"{format_hour(start_hour)} - {format_hour(end_hour)}"
            else:
                return f"위치 기반 시간 (top: {top_px}px, height: {height_px}px)"
                
        except Exception as e:
            return f"시간 파싱 오류: {e}"


def main():
    """메인 함수"""
    # 크롤러 인스턴스 생성
    with EverytimeCrawler() as crawler:
        # WebDriver 설정
        crawler.setup_driver(headless=False)  # 디버깅을 위해 headless=False
        
        # 로그인
        if not crawler.login():
            print("로그인에 실패했습니다. 프로그램을 종료합니다.")
            return
        
        # 시간표 수집
        print("시간표 수집 중...")
        timetable = crawler.get_timetable()
        print(f"시간표 {len(timetable)}개 수집 완료")
        
        # 게시판 글 수집 (자유게시판 예시)
        print("게시판 글 수집 중...")
        board_posts = crawler.get_board_posts("free", page_count=3)
        print(f"게시판 글 {len(board_posts)}개 수집 완료")


if __name__ == "__main__":
    main()
