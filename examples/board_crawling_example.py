"""
에브리타임 게시판 크롤링 예제
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 환경변수 로드
load_dotenv()

from everytime_crawler import EverytimeCrawler
import time


def main():
    """게시판 크롤링 예제 실행"""
    print("🎯 에브리타임 게시판 크롤링 예제 시작")
    
    # 크롤러 인스턴스 생성
    crawler = EverytimeCrawler()
    
    try:
        # WebDriver 설정 (헤드리스 모드 비활성화로 디버깅 가능)
        crawler.setup_driver(headless=False)
        
        # 로그인
        print("\n🔐 로그인 시도...")
        if crawler.login():
            print("✅ 로그인 성공!")
            
            # 게시판 목록
            boards_to_crawl = [
                ("free", "자유게시판", 2),
                ("secret", "비밀게시판", 1),
                ("freshman", "새내기게시판", 1)
            ]
            
            for board_id, board_name, pages in boards_to_crawl:
                print(f"\n📋 {board_name} 크롤링 시작...")
                
                # 게시글 목록 크롤링
                posts = crawler.get_board_posts(
                    board_id=board_id,
                    pages=pages,
                    delay=3  # 서버 부하 방지를 위한 대기
                )
                
                if posts:
                    print(f"\n📊 {board_name} 크롤링 결과:")
                    print(f"   총 게시글 수: {len(posts)}개")
                    
                    # 첫 3개 게시글 미리보기
                    print("\n📝 게시글 미리보기:")
                    for i, post in enumerate(posts[:3], 1):
                        print(f"   {i}. 제목: {post.get('title', 'N/A')}")
                        print(f"      작성자: {post.get('author', 'N/A')}")
                        print(f"      시간: {post.get('created_time', 'N/A')}")
                        print(f"      댓글: {post.get('comment_count', '0')}개")
                        if post.get('post_link'):
                            print(f"      링크: {post['post_link']}")
                        print()
                    
                    # CSV 파일로 저장
                    crawler.save_board_posts_to_csv(posts)
                    
                    # JSON 파일로 저장
                    crawler.save_board_posts_to_json(posts)
                    
                    # 첫 번째 게시글의 상세 정보 가져오기 (예시)
                    if posts and posts[0].get('post_link'):
                        print(f"\n📖 첫 번째 게시글 상세 정보 확인...")
                        detail = crawler.get_post_detail(posts[0]['post_link'])
                        if detail:
                            print(f"   내용 길이: {len(detail.get('content', ''))}자")
                            print(f"   댓글 수: {detail.get('comment_count', 0)}개")
                else:
                    print(f"❌ {board_name}에서 게시글을 찾을 수 없습니다.")
                
                # 게시판 간 대기
                time.sleep(5)
        
        else:
            print("❌ 로그인 실패!")
            return
            
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 브라우저 종료
        if crawler.driver:
            print("\n🔒 브라우저 종료...")
            crawler.quit()
        
        print("\n✅ 게시판 크롤링 완료!")


def demo_board_analysis():
    """크롤링된 게시판 데이터 분석 예제"""
    print("\n📊 게시판 데이터 분석 예제")
    
    import pandas as pd
    import glob
    
    # 저장된 CSV 파일 찾기
    csv_files = glob.glob("data/board_*.csv")
    
    if not csv_files:
        print("❌ 분석할 게시판 데이터가 없습니다. 먼저 크롤링을 실행하세요.")
        return
    
    for csv_file in csv_files:
        print(f"\n📋 파일 분석: {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            
            print(f"   총 게시글 수: {len(df)}")
            print(f"   컬럼: {list(df.columns)}")
            
            # 작성자별 게시글 수
            if 'author' in df.columns:
                author_counts = df['author'].value_counts().head(5)
                print(f"\n   상위 작성자:")
                for author, count in author_counts.items():
                    print(f"     {author}: {count}개")
            
            # 댓글 수 통계
            if 'comment_count' in df.columns:
                df['comment_count'] = pd.to_numeric(df['comment_count'], errors='coerce').fillna(0)
                avg_comments = df['comment_count'].mean()
                max_comments = df['comment_count'].max()
                print(f"\n   댓글 통계:")
                print(f"     평균 댓글 수: {avg_comments:.1f}개")
                print(f"     최대 댓글 수: {max_comments}개")
                
                # 댓글이 많은 게시글
                top_commented = df.nlargest(3, 'comment_count')
                print(f"\n   댓글 많은 게시글:")
                for _, post in top_commented.iterrows():
                    print(f"     {post.get('title', 'N/A')[:50]}... ({post['comment_count']}개)")
            
        except Exception as e:
            print(f"   ❌ 파일 분석 중 오류: {e}")


if __name__ == "__main__":
    print("🚀 에브리타임 게시판 크롤러 실행")
    print("=" * 50)
    
    # 메인 크롤링 실행
    main()
    
    # 데이터 분석 예제
    demo_board_analysis()
    
    print("\n" + "=" * 50)
    print("✨ 모든 작업 완료!")
