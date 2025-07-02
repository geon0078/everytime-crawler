#!/usr/bin/env python3
"""
간단한 게시판 크롤링 실행 스크립트
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 환경변수 로드
load_dotenv()

from everytime_crawler import EverytimeCrawler
import time
from datetime import datetime


def simple_board_crawling():
    """간단한 게시판 크롤링 실행"""
    print("🎯 에브리타임 게시판 크롤링 시작")
    print("=" * 50)
    
    # 크롤러 인스턴스 생성
    crawler = EverytimeCrawler()
    
    try:
        # WebDriver 설정
        print("🔧 WebDriver 설정 중...")
        crawler.setup_driver(headless=False)  # 브라우저 보이도록 설정 (test_login.py와 동일)
        
        # 로그인
        print("🔐 로그인 시도...")
        if crawler.login():
            print("✅ 로그인 성공!")
            
            # 테스트할 게시판 목록 (소량)
            test_boards = [
                ("free", "자유게시판", 2),
                ("secret", "비밀게시판", 1)
            ]
            
            for board_id, board_name, pages in test_boards:
                print(f"\n📋 {board_name} 크롤링 시작...")
                
                try:
                    # 개선된 게시판 크롤링 함수 사용
                    posts = crawler.get_board_posts(board_id, pages=pages, delay=2)
                    
                    if posts:
                        print(f"✅ {len(posts)}개 게시글 수집 성공!")
                        
                        # 상위 3개 게시글의 댓글도 수집
                        print("💬 상위 게시글 댓글 수집 중...")
                        detailed_posts = []
                        
                        for i, post in enumerate(posts[:3]):  # 상위 3개만 상세 크롤링
                            if post.get('post_link'):
                                print(f"   📖 {i+1}번째 게시글 상세 정보 수집 중...")
                                detail = crawler.get_post_detail(post['post_link'])
                                if detail:
                                    # 기본 정보와 상세 정보 합치기
                                    combined_post = post.copy()
                                    combined_post.update({
                                        'full_content': detail.get('content', ''),
                                        'comments': detail.get('comments', []),
                                        'detailed_comment_count': detail.get('comment_count', 0)
                                    })
                                    detailed_posts.append(combined_post)
                                    
                                    # 댓글 수 출력
                                    comment_count = len(detail.get('comments', []))
                                    print(f"     💬 댓글 {comment_count}개 수집")
                                    
                                time.sleep(2)  # 요청 간 대기
                        
                        # 수집된 데이터를 CSV/JSON으로 저장
                        import pandas as pd
                        import json
                        
                        df = pd.DataFrame(posts)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        # 전체 게시글 목록 저장
                        csv_filename = f"data/board_{board_id}_{timestamp}.csv"
                        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                        print(f"💾 CSV 파일: {csv_filename}")
                        
                        json_filename = f"data/board_{board_id}_{timestamp}.json"
                        with open(json_filename, 'w', encoding='utf-8') as f:
                            json.dump(posts, f, ensure_ascii=False, indent=2)
                        print(f"💾 JSON 파일: {json_filename}")
                        
                        # 댓글 포함 상세 정보 저장
                        if detailed_posts:
                            detailed_csv = f"data/board_{board_id}_detailed_{timestamp}.csv"
                            detailed_df = pd.DataFrame([
                                {
                                    'title': p.get('title', ''),
                                    'content': p.get('content', ''), 
                                    'full_content': p.get('full_content', ''),
                                    'author': p.get('author', ''),
                                    'created_time': p.get('created_time', ''),
                                    'comment_count': p.get('comment_count', ''),
                                    'detailed_comment_count': p.get('detailed_comment_count', 0),
                                    'post_link': p.get('post_link', ''),
                                    'comments_json': json.dumps(p.get('comments', []), ensure_ascii=False)
                                } for p in detailed_posts
                            ])
                            detailed_df.to_csv(detailed_csv, index=False, encoding='utf-8-sig')
                            print(f"💾 상세정보 CSV: {detailed_csv}")
                            
                            detailed_json = f"data/board_{board_id}_detailed_{timestamp}.json"
                            with open(detailed_json, 'w', encoding='utf-8') as f:
                                json.dump(detailed_posts, f, ensure_ascii=False, indent=2)
                            print(f"💾 상세정보 JSON: {detailed_json}")
                        
                        # 상위 3개 게시글 제목과 댓글 수 출력
                        print("📋 수집된 게시글 미리보기:")
                        for i, post in enumerate(posts[:3]):
                            title = post.get('title', 'N/A')[:40]
                            comment_count = post.get('comment_count', '0')
                            print(f"  {i+1}. {title}... (댓글: {comment_count}개)")
                            
                        # 댓글 내용 미리보기
                        if detailed_posts:
                            print("\n💬 수집된 댓글 미리보기:")
                            for i, post in enumerate(detailed_posts):
                                comments = post.get('comments', [])
                                print(f"  📝 {post.get('title', 'N/A')[:30]}... 의 댓글:")
                                if comments:
                                    for j, comment in enumerate(comments[:2]):  # 상위 2개 댓글만
                                        content = comment.get('content', '')[:50]
                                        author = comment.get('author', '익명')
                                        print(f"    {j+1}. {author}: {content}...")
                                else:
                                    print("    (댓글 없음)")
                                print()
                            
                    else:
                        print(f"❌ {board_name}에서 게시글을 찾을 수 없습니다.")
                    
                except Exception as e:
                    print(f"❌ {board_name} 크롤링 중 오류: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 게시판 간 대기
                print("⏳ 5초 대기...")
                time.sleep(5)
            
        else:
            print("❌ 로그인 실패!")
            
    except Exception as e:
        print(f"❌ 전체 크롤링 중 오류: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 브라우저 종료
        if crawler.driver:
            print("\n🔒 브라우저 종료...")
            crawler.quit()
        
        print("\n✅ 게시판 크롤링 완료!")


if __name__ == "__main__":
    # 환경변수 확인
    if not os.path.exists('.env'):
        print("❌ .env 파일이 없습니다!")
        print("📝 .env.example을 참고하여 .env 파일을 생성해주세요.")
        sys.exit(1)
    
    # 크롤링 실행
    simple_board_crawling()
