"""
에브리타임 크롤러 사용 예제
"""

from everytime_crawler import EverytimeCrawler
import os

def example_timetable_crawling():
    """시간표 크롤링 예제"""
    print("=== 시간표 크롤링 예제 ===")
    
    with EverytimeCrawler() as crawler:
        # WebDriver 설정 (디버깅 시 headless=False 사용)
        crawler.setup_driver(headless=False)
        
        # 로그인
        if crawler.login():
            # 시간표 수집 (2025년 1학기)
            timetable_data = crawler.get_timetable(year=2025, semester=1, save_to_file=True)
            
            # 결과 출력
            print(f"수집된 시간표 수: {len(timetable_data)}")
            for i, subject in enumerate(timetable_data[:3], 1):  # 처음 3개만 출력
                print(f"{i}. {subject['subject_name']} - {subject['time']} - {subject['professor']}")

def example_board_crawling():
    """게시판 크롤링 예제"""
    print("\n=== 게시판 크롤링 예제 ===")
    
    with EverytimeCrawler() as crawler:
        crawler.setup_driver(headless=False)
        
        if crawler.login():
            # 자유게시판 크롤링 (첫 3페이지)
            board_posts = crawler.get_board_posts("free", page_count=3, save_to_file=True)
            
            # 결과 출력
            print(f"수집된 게시글 수: {len(board_posts)}")
            for i, post in enumerate(board_posts[:5], 1):  # 처음 5개만 출력
                print(f"{i}. {post['title']} - {post['author']} - {post['created_time']}")

def example_specific_board_crawling():
    """특정 게시판 크롤링 예제"""
    print("\n=== 특정 게시판 크롤링 예제 ===")
    
    # 인기 게시판 ID들
    popular_boards = {
        "free": "자유게시판",
        "secret": "비밀게시판", 
        "freshman": "새내기게시판",
        "graduate": "졸업생게시판",
        "job": "취업게시판"
    }
    
    with EverytimeCrawler() as crawler:
        crawler.setup_driver(headless=False)
        
        if crawler.login():
            for board_id, board_name in popular_boards.items():
                print(f"\n{board_name} 크롤링 중...")
                try:
                    posts = crawler.get_board_posts(board_id, page_count=2, save_to_file=True)
                    print(f"{board_name}: {len(posts)}개 게시글 수집 완료")
                except Exception as e:
                    print(f"{board_name} 크롤링 실패: {e}")

def example_post_detail_crawling():
    """게시글 상세 정보 크롤링 예제"""
    print("\n=== 게시글 상세 정보 크롤링 예제 ===")
    
    with EverytimeCrawler() as crawler:
        crawler.setup_driver(headless=False)
        
        if crawler.login():
            # 먼저 게시판에서 게시글 목록 가져오기
            board_posts = crawler.get_board_posts("free", page_count=1, save_to_file=False)
            
            if board_posts:
                # 첫 번째 게시글의 상세 정보 가져오기
                first_post = board_posts[0]
                print(f"상세 정보 수집 대상: {first_post['title']}")
                
                detail_info = crawler.get_post_detail(first_post['post_link'])
                if detail_info:
                    print(f"게시글 내용: {detail_info['content'][:100]}...")
                    print(f"댓글 수: {len(detail_info['comments'])}")

def main():
    """메인 실행 함수"""
    print("에브리타임 크롤러 예제 실행")
    print("실행하기 전에 .env 파일에 계정 정보를 설정해주세요!")
    
    # .env 파일 확인
    if not os.path.exists('.env'):
        print("경고: .env 파일이 없습니다. .env.example을 참고하여 .env 파일을 생성해주세요.")
        return
    
    try:
        # 예제 실행 (필요한 것만 주석 해제하여 사용)
        example_timetable_crawling()
        # example_board_crawling()  # 게시판 크롤링도 테스트
        # example_specific_board_crawling()
        # example_post_detail_crawling()
        
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
