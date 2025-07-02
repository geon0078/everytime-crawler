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
        self.base_url = "https://everytime.kr"
        self.session = requests.Session()
        self.driver = None
        self.user_id = os.getenv('EVERYTIME_ID')
        self.password = os.getenv('EVERYTIME_PASSWORD')
        
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
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
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
            
            # 메인 페이지에서 로그인 링크 클릭
            self.driver.get(f"{self.base_url}")
            print("메인 페이지 로드 완료")
            time.sleep(2)
            
            # 로그인 링크 클릭
            try:
                login_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "로그인"))
                )
                login_link.click()
                print("로그인 링크 클릭 완료")
                time.sleep(3)
            except:
                # 직접 로그인 페이지로 이동
                self.driver.get("https://account.everytime.kr/login")
                time.sleep(3)
            
            print(f"현재 URL: {self.driver.current_url}")
            
            # 로그인 폼 입력 필드 찾기 (업데이트된 name 속성 사용)
            userid_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "id"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            print("로그인 폼 찾기 성공")
            
            # 로그인 정보 입력
            userid_input.clear()
            userid_input.send_keys(self.user_id)
            time.sleep(1)
            
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            print("로그인 정보 입력 완료")
            
            # 로그인 버튼 클릭 (업데이트된 value 속성 사용)
            login_button = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='에브리타임 로그인']")
            login_button.click()
            print("로그인 버튼 클릭 완료")
            
            # 로그인 결과 확인 (더 긴 대기 시간)
            time.sleep(5)
            
            current_url = self.driver.current_url
            print(f"로그인 후 URL: {current_url}")
            
            # 로그인 성공 확인 - 메인 페이지로 리다이렉트되면 성공
            if current_url == "https://everytime.kr/" or "everytime.kr" in current_url and "login" not in current_url:
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
        board_map = {
            "free": "자유게시판",
            "secret": "비밀게시판", 
            "freshman": "새내기게시판",
            "graduate": "졸업생게시판",
            "job": "취업게시판",
            "exam": "시험정보게시판",
            "club": "동아리게시판",
            "market": "장터게시판"
        }
        
        print(f"🔍 '{board_map.get(board_id, board_id)}' 게시판 크롤링 시작...")
        
        all_posts = []
        
        try:
            # 게시판 메인 페이지로 이동
            board_url = f"{self.base_url}/{board_id}"
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
                
                # 게시글 정보 추출
                for element in post_elements:
                    try:
                        post_data = {
                            'title': '제목 없음',
                            'author': '익명',
                            'created_time': '',
                            'comment_count': '0',
                            'post_link': '',
                            'board_id': board_id,
                            'page': page,
                            'collected_at': datetime.now().isoformat()
                        }
                        
                        # 제목 추출
                        title_selectors = [".title", ".subject", ".headline", "h3", "h4", ".post-title"]
                        for selector in title_selectors:
                            title_elem = element.find_elements(By.CSS_SELECTOR, selector)
                            if title_elem:
                                post_data['title'] = title_elem[0].text.strip()
                                
                                # 링크 추출
                                link_elem = title_elem[0].find_elements(By.TAG_NAME, "a")
                                if link_elem:
                                    href = link_elem[0].get_attribute("href")
                                    if href:
                                        post_data['post_link'] = href
                                break
                        
                        # 작성자 추출
                        author_selectors = [".writer", ".author", ".user", ".nickname"]
                        for selector in author_selectors:
                            author_elem = element.find_elements(By.CSS_SELECTOR, selector)
                            if author_elem:
                                post_data['author'] = author_elem[0].text.strip()
                                break
                        
                        # 작성 시간 추출
                        time_selectors = [".time", ".date", ".created", ".timestamp"]
                        for selector in time_selectors:
                            time_elem = element.find_elements(By.CSS_SELECTOR, selector)
                            if time_elem:
                                post_data['created_time'] = time_elem[0].text.strip()
                                break
                        
                        # 댓글 수 추출
                        comment_selectors = [".commentcount", ".comment-count", ".comments", ".reply-count"]
                        for selector in comment_selectors:
                            comment_elem = element.find_elements(By.CSS_SELECTOR, selector)
                            if comment_elem:
                                post_data['comment_count'] = comment_elem[0].text.strip()
                                break
                        
                        # 유효한 게시글만 추가
                        if post_data['title'] != '제목 없음' and post_data['title'].strip():
                            all_posts.append(post_data)
                            print(f"게시글 추가: {post_data['title'][:30]}...")
                        
                    except Exception as e:
                        print(f"게시글 파싱 오류: {e}")
                        continue
                
                print(f"페이지 {page} 수집 완료: {len([p for p in all_posts if p['page'] == page])}개 게시글")
                time.sleep(1)  # 서버 부하 방지
            
            if save_to_file and all_posts:
                # DataFrame으로 변환 후 CSV 저장
                df = pd.DataFrame(all_posts)
                filename = f"board_{board_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"게시판 데이터가 {filename}에 저장되었습니다.")
            
            return all_posts
            
        except Exception as e:
            print(f"게시판 수집 오류: {e}")
            return []
    
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
        """개별 게시글에서 정보 추출"""
        post_info = {}
        
        try:
            # BeautifulSoup으로 더 정확한 파싱
            soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
            
            # 제목 추출 - 다양한 패턴 시도
            title_selectors = [
                '.title',
                '.subject', 
                'h3',
                'h4',
                '.article-title',
                '.post-title',
                'a[href*="view"]',
                '.text'
            ]
            
            title = None
            for title_sel in title_selectors:
                title_elem = soup.select_one(title_sel)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 2:  # 의미있는 제목만
                        break
            
            # 작성자 추출
            author_selectors = [
                '.writer',
                '.author',
                '.nickname',
                '.user',
                '.name'
            ]
            
            author = "익명"
            for author_sel in author_selectors:
                author_elem = soup.select_one(author_sel)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    if author:
                        break
            
            # 작성시간 추출
            time_selectors = [
                '.time',
                '.date',
                '.created_at',
                '.timestamp',
                '.datetime'
            ]
            
            created_time = None
            for time_sel in time_selectors:
                time_elem = soup.select_one(time_sel)
                if time_elem:
                    created_time = time_elem.get_text(strip=True)
                    if created_time:
                        break
            
            # 댓글 수 추출
            comment_selectors = [
                '.comment',
                '.reply',
                '.comment-count',
                '.reply-count'
            ]
            
            comment_count = "0"
            for comment_sel in comment_selectors:
                comment_elem = soup.select_one(comment_sel)
                if comment_elem:
                    comment_text = comment_elem.get_text(strip=True)
                    # 숫자만 추출
                    import re
                    numbers = re.findall(r'\d+', comment_text)
                    if numbers:
                        comment_count = numbers[0]
                        break
            
            # 게시글 링크 추출
            link_elem = soup.select_one('a[href]')
            post_link = None
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if href.startswith('/'):
                        post_link = f"{self.base_url}{href}"
                    else:
                        post_link = href
            
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
        개별 게시글의 상세 정보 크롤링
        
        Args:
            post_url (str): 게시글 URL
            
        Returns:
            dict: 게시글 상세 정보
        """
        try:
            print(f"📖 게시글 상세 정보 크롤링: {post_url}")
            
            self.driver.get(post_url)
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 게시글 내용 추출
            content_selectors = [
                '.content',
                '.article-content',
                '.post-content',
                '.text',
                '.body',
                'p'
            ]
            
            content = ""
            for content_sel in content_selectors:
                content_elem = soup.select_one(content_sel)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    if content and len(content) > 10:
                        break
            
            # 댓글 추출
            comments = []
            comment_selectors = [
                '.comment',
                '.reply', 
                '.comment-item',
                '.reply-item'
            ]
            
            for comment_sel in comment_selectors:
                comment_elems = soup.select(comment_sel)
                if comment_elems:
                    for comment_elem in comment_elems:
                        comment_text = comment_elem.get_text(strip=True)
                        if comment_text and len(comment_text) > 2:
                            comments.append(comment_text)
                    break
            
            detail_info = {
                'url': post_url,
                'content': content,
                'comments': comments,
                'comment_count': len(comments),
                'collected_at': datetime.now().isoformat()
            }
            
            print(f"✅ 게시글 상세 정보 수집 완료 (댓글 {len(comments)}개)")
            return detail_info
            
        except Exception as e:
            print(f"❌ 게시글 상세 정보 크롤링 중 오류: {e}")
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
