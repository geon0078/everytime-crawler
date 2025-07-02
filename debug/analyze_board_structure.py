"""
에브리타임 게시판 구조 분석 도구
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from everytime_crawler import EverytimeCrawler
from bs4 import BeautifulSoup
import time
from datetime import datetime


def analyze_board_structure(board_id="free"):
    """
    게시판 HTML 구조 분석
    
    Args:
        board_id (str): 분석할 게시판 ID
    """
    print(f"🔍 '{board_id}' 게시판 구조 분석 시작...")
    
    crawler = EverytimeCrawler()
    
    try:
        # WebDriver 설정
        crawler.setup_driver(headless=False)
        
        # 로그인
        if crawler.login():
            print("✅ 로그인 성공!")
            
            # 게시판 페이지로 이동
            board_url = f"{crawler.base_url}/{board_id}"
            crawler.driver.get(board_url)
            time.sleep(3)
            
            print(f"📍 현재 URL: {crawler.driver.current_url}")
            
            # HTML 소스 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = f"debug/board_{board_id}_structure_{timestamp}.html"
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(crawler.driver.page_source)
            
            print(f"💾 HTML 소스 저장: {debug_file}")
            
            # BeautifulSoup으로 구조 분석
            soup = BeautifulSoup(crawler.driver.page_source, 'html.parser')
            
            print("\n🔍 페이지 구조 분석:")
            
            # 1. 전체 페이지 정보
            title = soup.find('title')
            print(f"   페이지 제목: {title.text if title else 'N/A'}")
            
            # 2. 주요 컨테이너 찾기
            print("\n📦 주요 컨테이너:")
            container_selectors = [
                'main', '.main', '#main',
                'content', '.content', '#content',
                'container', '.container', '#container',
                'wrapper', '.wrapper', '#wrapper'
            ]
            
            for selector in container_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"   {selector}: {len(elements)}개 발견")
            
            # 3. 게시글 관련 요소 찾기
            print("\n📝 게시글 관련 요소:")
            post_selectors = [
                'article', '.article',
                '.post', '.board-item', '.list-item',
                'tr.list', 'li',
                '.content-item', '.item'
            ]
            
            for selector in post_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"   {selector}: {len(elements)}개 발견")
                    
                    # 첫 번째 요소의 구조 분석
                    if elements:
                        first_element = elements[0]
                        print(f"     첫 번째 요소 클래스: {first_element.get('class', [])}")
                        print(f"     첫 번째 요소 ID: {first_element.get('id', 'N/A')}")
                        
                        # 텍스트 내용 미리보기
                        text_content = first_element.get_text(strip=True)[:100]
                        print(f"     텍스트 미리보기: {text_content}...")
            
            # 4. 링크 요소 분석
            print("\n🔗 링크 요소:")
            links = soup.find_all('a', href=True)
            
            view_links = [link for link in links if 'view' in link.get('href', '')]
            post_links = [link for link in links if any(keyword in link.get('href', '') 
                         for keyword in ['board', 'post', 'article'])]
            
            print(f"   전체 링크: {len(links)}개")
            print(f"   'view' 포함 링크: {len(view_links)}개")
            print(f"   게시글 관련 링크: {len(post_links)}개")
            
            if view_links:
                print("   View 링크 샘플:")
                for i, link in enumerate(view_links[:3]):
                    href = link.get('href')
                    text = link.get_text(strip=True)[:50]
                    print(f"     {i+1}. {href} - {text}")
            
            # 5. 폼 요소 분석
            print("\n📋 폼 요소:")
            forms = soup.find_all('form')
            print(f"   폼 개수: {len(forms)}")
            
            for i, form in enumerate(forms):
                action = form.get('action', 'N/A')
                method = form.get('method', 'N/A')
                print(f"     폼 {i+1}: action={action}, method={method}")
            
            # 6. JavaScript 관련 요소
            print("\n⚙️ JavaScript 관련:")
            scripts = soup.find_all('script')
            print(f"   스크립트 태그: {len(scripts)}개")
            
            # React나 Vue 등 프레임워크 사용 여부
            page_source = crawler.driver.page_source.lower()
            frameworks = ['react', 'vue', 'angular', 'jquery']
            
            for framework in frameworks:
                if framework in page_source:
                    print(f"   {framework.capitalize()} 사용 가능성 감지")
            
            # 7. CSS 클래스 분석
            print("\n🎨 CSS 클래스 분석:")
            all_elements = soup.find_all(class_=True)
            all_classes = []
            
            for element in all_elements:
                classes = element.get('class', [])
                all_classes.extend(classes)
            
            from collections import Counter
            class_counts = Counter(all_classes)
            most_common_classes = class_counts.most_common(10)
            
            print("   가장 많이 사용되는 클래스:")
            for class_name, count in most_common_classes:
                print(f"     .{class_name}: {count}회")
            
            # 8. 페이지네이션 분석
            print("\n📄 페이지네이션:")
            pagination_selectors = [
                '.pagination', '.paging', '.page',
                'nav', '.nav', '.navigation'
            ]
            
            for selector in pagination_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"   {selector}: {len(elements)}개 발견")
            
            # 페이지 번호 링크 찾기
            page_links = soup.find_all('a', href=lambda x: x and 'page=' in x)
            print(f"   페이지 링크: {len(page_links)}개")
            
            # 9. 게시글 요소의 상세 구조 분석
            print("\n🔬 게시글 요소 상세 분석:")
            
            # 가장 유력한 게시글 셀렉터 찾기
            article_elements = soup.select('article.list')
            if not article_elements:
                article_elements = soup.select('.article')
            if not article_elements:
                article_elements = soup.select('tr.list')
            
            if article_elements:
                print(f"   게시글 요소 {len(article_elements)}개 발견")
                
                # 첫 번째 게시글의 상세 구조
                first_article = article_elements[0]
                print("\n   첫 번째 게시글 구조:")
                
                # 제목 요소 찾기
                title_candidates = [
                    first_article.select_one('.title'),
                    first_article.select_one('.subject'),
                    first_article.select_one('h3'),
                    first_article.select_one('h4'),
                    first_article.select_one('a[href*="view"]')
                ]
                
                for i, candidate in enumerate(title_candidates):
                    if candidate:
                        print(f"     제목 후보 {i+1}: {candidate.get_text(strip=True)[:50]}")
                
                # 작성자 요소 찾기
                author_candidates = [
                    first_article.select_one('.writer'),
                    first_article.select_one('.author'),
                    first_article.select_one('.nickname'),
                    first_article.select_one('.user')
                ]
                
                for i, candidate in enumerate(author_candidates):
                    if candidate:
                        print(f"     작성자 후보 {i+1}: {candidate.get_text(strip=True)}")
                
                # 시간 요소 찾기
                time_candidates = [
                    first_article.select_one('.time'),
                    first_article.select_one('.date'),
                    first_article.select_one('.created_at')
                ]
                
                for i, candidate in enumerate(time_candidates):
                    if candidate:
                        print(f"     시간 후보 {i+1}: {candidate.get_text(strip=True)}")
            
            print(f"\n✅ 구조 분석 완료! 상세 결과는 {debug_file}을 확인하세요.")
            
        else:
            print("❌ 로그인 실패!")
            
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler.driver:
            crawler.quit()


def analyze_multiple_boards():
    """여러 게시판 구조 비교 분석"""
    boards = ['free', 'secret', 'freshman']
    
    print("🔍 여러 게시판 구조 비교 분석")
    print("=" * 50)
    
    for board_id in boards:
        print(f"\n📋 {board_id} 게시판 분석...")
        analyze_board_structure(board_id)
        time.sleep(5)  # 서버 부하 방지


if __name__ == "__main__":
    print("🔧 에브리타임 게시판 구조 분석 도구")
    print("=" * 50)
    
    # 단일 게시판 분석
    analyze_board_structure("free")
    
    # 여러 게시판 비교 분석 (선택사항)
    # analyze_multiple_boards()
