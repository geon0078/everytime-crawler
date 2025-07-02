#!/usr/bin/env python3
"""
댓글 포함 대량 게시판 크롤링 스크립트
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 환경변수 로드
load_dotenv()

from everytime_crawler import EverytimeCrawler
import time
import json
import pandas as pd
from datetime import datetime


def massive_board_crawling_with_comments():
    """댓글 포함 대량 게시판 크롤링"""
    print("🎯 에브리타임 대량 게시판 크롤링 (댓글 포함)")
    print("=" * 60)
    
    crawler = EverytimeCrawler()
    
    try:
        print("🔧 WebDriver 설정 중...")
        crawler.setup_driver(headless=True)  # 대량 크롤링은 headless 모드
        
        print("🔐 로그인 시도...")
        if not crawler.login():
            print("❌ 로그인 실패!")
            return
        
        print("✅ 로그인 성공!")
        
        # 크롤링할 게시판 목록
        boards_to_crawl = [
            ("free", "성남캠 자유게시판", 5),     # 5페이지
            ("secret", "비밀게시판", 3),        # 3페이지
            ("graduate", "졸업생게시판", 2),    # 2페이지
            ("freshman", "새내기게시판", 2),    # 2페이지
        ]
        
        all_results = {}
        
        for board_id, board_name, pages in boards_to_crawl:
            print(f"\n📋 {board_name} 크롤링 시작...")
            
            try:
                # 게시글 목록 수집
                posts = crawler.get_board_posts(board_id, pages=pages, delay=3)
                
                if posts:
                    print(f"✅ {len(posts)}개 게시글 수집 성공!")
                    
                    # 댓글이 있는 게시글의 상세 정보 수집
                    print("💬 댓글이 있는 게시글 상세 정보 수집 중...")
                    detailed_posts = []
                    
                    posts_with_comments = [p for p in posts if int(p.get('comment_count', '0')) > 0]
                    print(f"📊 댓글이 있는 게시글: {len(posts_with_comments)}개")
                    
                    # 댓글이 있는 게시글만 상세 크롤링 (최대 10개)
                    for i, post in enumerate(posts_with_comments[:10]):
                        if post.get('post_link'):
                            print(f"   📖 {i+1}/{min(10, len(posts_with_comments))} 게시글 상세 정보 수집 중...")
                            detail = crawler.get_post_detail(post['post_link'])
                            if detail:
                                combined_post = post.copy()
                                combined_post.update({
                                    'full_content': detail.get('content', ''),
                                    'comments': detail.get('comments', []),
                                    'detailed_comment_count': detail.get('comment_count', 0)
                                })
                                detailed_posts.append(combined_post)
                                
                                comment_count = len(detail.get('comments', []))
                                print(f"     💬 댓글 {comment_count}개 수집")
                            
                            time.sleep(2)  # 요청 간 대기
                    
                    # 데이터 저장
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 전체 게시글 목록
                    df = pd.DataFrame(posts)
                    csv_file = f"data/massive_{board_id}_{timestamp}.csv"
                    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                    
                    json_file = f"data/massive_{board_id}_{timestamp}.json"
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(posts, f, ensure_ascii=False, indent=2)
                    
                    # 댓글 포함 상세 정보
                    if detailed_posts:
                        detailed_csv = f"data/massive_{board_id}_detailed_{timestamp}.csv"
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
                                'comments_json': json.dumps(p.get('comments', []), ensure_ascii=False),
                                'board_id': board_id,
                                'board_name': board_name
                            } for p in detailed_posts
                        ])
                        detailed_df.to_csv(detailed_csv, index=False, encoding='utf-8-sig')
                        
                        detailed_json = f"data/massive_{board_id}_detailed_{timestamp}.json"
                        with open(detailed_json, 'w', encoding='utf-8') as f:
                            json.dump(detailed_posts, f, ensure_ascii=False, indent=2)
                        
                        print(f"💾 상세정보 저장: {len(detailed_posts)}개 게시글")
                    
                    # 결과 요약
                    all_results[board_id] = {
                        'board_name': board_name,
                        'total_posts': len(posts),
                        'posts_with_comments': len(posts_with_comments),
                        'detailed_posts': len(detailed_posts),
                        'total_comments': sum(len(p.get('comments', [])) for p in detailed_posts)
                    }
                    
                    print(f"📊 {board_name} 수집 완료:")
                    print(f"   - 전체 게시글: {len(posts)}개")
                    print(f"   - 댓글 있는 게시글: {len(posts_with_comments)}개")  
                    print(f"   - 상세 수집 게시글: {len(detailed_posts)}개")
                    print(f"   - 총 수집 댓글: {sum(len(p.get('comments', [])) for p in detailed_posts)}개")
                    
                else:
                    print(f"❌ {board_name}에서 게시글을 찾을 수 없습니다.")
                    
            except Exception as e:
                print(f"❌ {board_name} 크롤링 중 오류: {e}")
                import traceback
                traceback.print_exc()
            
            print("⏳ 10초 대기...")
            time.sleep(10)
        
        # 전체 결과 요약
        print("\n" + "="*60)
        print("🎉 대량 크롤링 완료! 전체 결과 요약:")
        print("="*60)
        
        total_posts = 0
        total_comments = 0
        
        for board_id, result in all_results.items():
            print(f"📋 {result['board_name']}:")
            print(f"   - 게시글: {result['total_posts']}개")
            print(f"   - 댓글: {result['total_comments']}개")
            
            total_posts += result['total_posts']
            total_comments += result['total_comments']
        
        print("\n📊 총합:")
        print(f"   - 전체 게시글: {total_posts}개")
        print(f"   - 전체 댓글: {total_comments}개")
        
        # 요약 정보 저장
        summary = {
            'crawl_completed_at': datetime.now().isoformat(),
            'boards': all_results,
            'totals': {
                'total_posts': total_posts,
                'total_comments': total_comments
            }
        }
        
        summary_file = f"data/crawling_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\n📋 크롤링 요약 저장: {summary_file}")
        
    except Exception as e:
        print(f"❌ 전체 크롤링 중 오류: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler.driver:
            print("\n🔒 브라우저 종료...")
            crawler.quit()
        
        print("\n✅ 대량 게시판 크롤링 완료!")


if __name__ == "__main__":
    massive_board_crawling_with_comments()
