"""
에브리타임 게시판 크롤링 전용 모듈
"""

import time
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class BoardCrawler:
    """에브리타임 게시판 크롤링 전용 클래스"""
    
    def __init__(self, crawler_instance):
        """
        BoardCrawler 초기화
        
        Args:
            crawler_instance: EverytimeCrawler 인스턴스
        """
        self.crawler = crawler_instance
        self.driver = crawler_instance.driver
        self.base_url = crawler_instance.base_url
        
        # 게시판 ID 매핑
        self.board_map = {
            "free": "자유게시판",
            "secret": "비밀게시판", 
            "freshman": "새내기게시판",
            "graduate": "졸업생게시판",
            "job": "취업게시판",
            "exam": "시험정보게시판",
            "club": "동아리게시판",
            "market": "장터게시판"
        }
    
    def get_board_posts(self, board_id="free", pages=3, delay=2):
        """
        게시판 글 목록 크롤링
        
        Args:
            board_id (str): 게시판 ID (free, secret, freshman 등)
            pages (int): 크롤링할 페이지 수
            delay (int): 페이지 간 대기 시간(초)
            
        Returns:
            list: 게시글 정보 리스트
        """
        print(f"🔍 '{self.board_map.get(board_id, board_id)}' 게시판 크롤링 시작...")
        
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
                posts = self._extract_posts_from_page(board_id, page)
                all_posts.extend(posts)
                
                print(f"✅ 페이지 {page}에서 {len(posts)}개 게시글 수집")
                
        except Exception as e:
            print(f"❌ 게시판 크롤링 중 오류 발생: {e}")
            self._save_debug_info(board_id)
        
        print(f"🎉 총 {len(all_posts)}개 게시글 수집 완료!")
        return all_posts
    
    def _extract_posts_from_page(self, board_id, page_num):
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
                    post_info = self._extract_post_info(element, used_selector)
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
    
    def _extract_post_info(self, element, selector_used):
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
    
    def save_posts_to_csv(self, posts, filename=None):
        """게시글 목록을 CSV 파일로 저장"""
        if not posts:
            print("⚠️ 저장할 게시글이 없습니다.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            board_id = posts[0].get('board_id', 'unknown')
            filename = f"data/board_{board_id}_{timestamp}.csv"
        
        try:
            import pandas as pd
            df = pd.DataFrame(posts)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"💾 게시글 {len(posts)}개가 '{filename}'에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ CSV 저장 중 오류: {e}")
    
    def save_posts_to_json(self, posts, filename=None):
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
    
    def _save_debug_info(self, board_id):
        """디버깅을 위한 페이지 정보 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_filename = f"debug/board_{board_id}_debug_{timestamp}.html"
            
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print(f"🔧 디버그 정보가 '{debug_filename}'에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 디버그 정보 저장 중 오류: {e}")
