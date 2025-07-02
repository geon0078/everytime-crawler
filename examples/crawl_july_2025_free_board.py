#!/usr/bin/env python3
"""
2025년 7월 자유게시판 전체 글 크롤링 스크립트
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
from datetime import datetime, timedelta
import re


def parse_everytime_time(time_str):
    """에브리타임 시간 문자열을 datetime 객체로 변환"""
    if not time_str:
        return None
    
    now = datetime.now()
    
    # "3분 전", "17분 전" 형태
    if "분 전" in time_str:
        minutes = int(re.findall(r'\d+', time_str)[0])
        return now - timedelta(minutes=minutes)
    
    # "1시간 전", "2시간 전" 형태
    elif "시간 전" in time_str:
        hours = int(re.findall(r'\d+', time_str)[0])
        return now - timedelta(hours=hours)
    
    # "07/01 09:11", "20:26" 형태
    elif "/" in time_str:
        # "07/01 09:11" 형태
        try:
            month_day, time_part = time_str.split(" ")
            month, day = month_day.split("/")
            hour, minute = time_part.split(":")
            
            # 2025년으로 가정
            return datetime(2025, int(month), int(day), int(hour), int(minute))
        except:
            pass
    
    elif ":" in time_str and len(time_str) == 5:
        # "20:26" 형태 (오늘)
        try:
            hour, minute = time_str.split(":")
            today = now.date()
            return datetime.combine(today, datetime.strptime(f"{hour}:{minute}", "%H:%M").time())
        except:
            pass
    
    return None


def is_july_2025(time_str):
    """주어진 시간 문자열이 2025년 7월에 해당하는지 확인"""
    parsed_time = parse_everytime_time(time_str)
    if parsed_time:
        return parsed_time.year == 2025 and parsed_time.month == 7
    
    # 파싱에 실패한 경우 문자열로 판단
    if "07/" in time_str:  # 07/01, 07/02 등
        return True
    
    # 최근 글 (분 전, 시간 전)도 7월로 간주 (현재가 7월이므로)
    if "분 전" in time_str or "시간 전" in time_str:
        return True
    
    # 오늘 작성된 글 (시:분 형태)도 7월로 간주
    if ":" in time_str and len(time_str) == 5:
        return True
    
    return False


def crawl_july_2025_free_board():
    """2025년 7월 자유게시판 전체 글 크롤링"""
    print("🗓️ 2025년 7월 자유게시판 전체 글 크롤링")
    print("=" * 60)
    
    crawler = EverytimeCrawler()
    all_july_posts = []
    july_detailed_posts = []
    
    try:
        print("🔧 WebDriver 설정 중...")
        crawler.setup_driver(headless=True)  # 대량 크롤링은 headless 모드
        
        print("🔐 로그인 시도...")
        if not crawler.login():
            print("❌ 로그인 실패!")
            return
        
        print("✅ 로그인 성공!")
        print("\n📋 자유게시판 크롤링 시작...")
        
        # 충분한 페이지 수로 크롤링 (7월 전체 데이터 확보)
        max_pages = 50  # 필요에 따라 조정
        current_page = 1
        consecutive_non_july = 0  # 연속으로 7월이 아닌 글 수
        
        while current_page <= max_pages:
            print(f"\n📄 페이지 {current_page} 크롤링 중...")
            
            try:
                # 한 페이지씩 크롤링
                posts = crawler.get_board_posts("free", pages=1, delay=3)
                
                if not posts:
                    print(f"❌ 페이지 {current_page}에서 게시글을 찾을 수 없습니다.")
                    break
                
                page_july_posts = []
                page_non_july_posts = 0
                
                for post in posts:
                    created_time = post.get('created_time', '')
                    
                    if is_july_2025(created_time):
                        page_july_posts.append(post)
                        consecutive_non_july = 0  # 7월 글을 찾았으므로 카운터 리셋
                    else:
                        page_non_july_posts += 1
                        consecutive_non_july += 1
                
                all_july_posts.extend(page_july_posts)
                
                print(f"   📅 7월 게시글: {len(page_july_posts)}개")
                print(f"   📊 누적 7월 게시글: {len(all_july_posts)}개")
                
                # 연속으로 50개 이상의 비-7월 글이 나오면 중단
                if consecutive_non_july >= 50:
                    print(f"\n⏹️ 연속으로 7월이 아닌 글이 {consecutive_non_july}개 나왔으므로 크롤링을 중단합니다.")
                    break
                
                # 페이지에 7월 글이 하나도 없고, 이미 충분한 7월 글을 수집했다면 중단
                if len(page_july_posts) == 0 and len(all_july_posts) > 100:
                    print(f"\n⏹️ 7월 글이 더 이상 없으므로 크롤링을 중단합니다.")
                    break
                
                current_page += 1
                time.sleep(3)  # 페이지 간 대기
                
            except Exception as e:
                print(f"❌ 페이지 {current_page} 크롤링 중 오류: {e}")
                current_page += 1
                time.sleep(5)
                continue
        
        print(f"\n🎉 7월 게시글 수집 완료! 총 {len(all_july_posts)}개")
        
        if not all_july_posts:
            print("❌ 7월 게시글을 찾을 수 없습니다.")
            return
        
        # 댓글이 있는 게시글의 상세 정보 수집
        print("\n💬 댓글이 있는 게시글 상세 정보 수집 중...")
        posts_with_comments = [p for p in all_july_posts if int(p.get('comment_count', '0')) > 0]
        print(f"📊 댓글이 있는 7월 게시글: {len(posts_with_comments)}개")
        
        # 댓글이 있는 게시글 중 최대 30개 상세 크롤링
        max_detailed = min(30, len(posts_with_comments))
        for i, post in enumerate(posts_with_comments[:max_detailed]):
            if post.get('post_link'):
                print(f"   📖 {i+1}/{max_detailed} 게시글 상세 정보 수집 중...")
                detail = crawler.get_post_detail(post['post_link'])
                if detail:
                    combined_post = post.copy()
                    combined_post.update({
                        'full_content': detail.get('content', ''),
                        'comments': detail.get('comments', []),
                        'detailed_comment_count': detail.get('comment_count', 0)
                    })
                    july_detailed_posts.append(combined_post)
                    
                    comment_count = len(detail.get('comments', []))
                    print(f"     💬 댓글 {comment_count}개 수집")
                
                time.sleep(2)  # 요청 간 대기
        
        # 데이터 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 7월 전체 게시글 저장
        print(f"\n💾 데이터 저장 중...")
        
        # CSV 저장
        df = pd.DataFrame(all_july_posts)
        csv_file = f"data/july_2025_free_board_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"📄 전체 게시글 CSV: {csv_file}")
        
        # JSON 저장
        json_file = f"data/july_2025_free_board_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_july_posts, f, ensure_ascii=False, indent=2)
        print(f"📄 전체 게시글 JSON: {json_file}")
        
        # 댓글 포함 상세 정보 저장
        if july_detailed_posts:
            detailed_csv = f"data/july_2025_free_board_detailed_{timestamp}.csv"
            detailed_df = pd.DataFrame([
                {
                    'title': p.get('title', ''),
                    'content': p.get('content', ''),
                    'full_content': p.get('full_content', ''),
                    'author': p.get('author', ''),
                    'created_time': p.get('created_time', ''),
                    'parsed_datetime': parse_everytime_time(p.get('created_time', '')),
                    'comment_count': p.get('comment_count', ''),
                    'detailed_comment_count': p.get('detailed_comment_count', 0),
                    'post_link': p.get('post_link', ''),
                    'comments_json': json.dumps(p.get('comments', []), ensure_ascii=False),
                    'board_id': 'free',
                    'collected_at': p.get('collected_at', '')
                } for p in july_detailed_posts
            ])
            detailed_df.to_csv(detailed_csv, index=False, encoding='utf-8-sig')
            print(f"📄 상세정보 CSV: {detailed_csv}")
            
            detailed_json = f"data/july_2025_free_board_detailed_{timestamp}.json"
            with open(detailed_json, 'w', encoding='utf-8') as f:
                json.dump(july_detailed_posts, f, ensure_ascii=False, indent=2)
            print(f"📄 상세정보 JSON: {detailed_json}")
        
        # 통계 정보 생성
        total_comments = sum(len(p.get('comments', [])) for p in july_detailed_posts)
        
        # 일별 게시글 수 통계
        daily_stats = {}
        for post in all_july_posts:
            parsed_time = parse_everytime_time(post.get('created_time', ''))
            if parsed_time:
                date_key = parsed_time.strftime('%Y-%m-%d')
                daily_stats[date_key] = daily_stats.get(date_key, 0) + 1
        
        # 요약 정보
        summary = {
            'crawl_info': {
                'target_period': '2025년 7월',
                'board_name': '성남캠 자유게시판',
                'crawl_completed_at': datetime.now().isoformat(),
                'pages_crawled': current_page - 1
            },
            'statistics': {
                'total_july_posts': len(all_july_posts),
                'posts_with_comments': len(posts_with_comments),
                'detailed_posts_crawled': len(july_detailed_posts),
                'total_comments_collected': total_comments,
                'daily_post_count': daily_stats
            },
            'files_created': {
                'all_posts_csv': csv_file,
                'all_posts_json': json_file,
                'detailed_csv': detailed_csv if july_detailed_posts else None,
                'detailed_json': detailed_json if july_detailed_posts else None
            }
        }
        
        summary_file = f"data/july_2025_free_board_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"📋 크롤링 요약: {summary_file}")
        
        # 결과 출력
        print("\n" + "="*60)
        print("🎉 2025년 7월 자유게시판 크롤링 완료!")
        print("="*60)
        print(f"📊 수집 결과:")
        print(f"   - 총 게시글: {len(all_july_posts)}개")
        print(f"   - 댓글 있는 게시글: {len(posts_with_comments)}개")
        print(f"   - 상세 수집 게시글: {len(july_detailed_posts)}개")
        print(f"   - 총 수집 댓글: {total_comments}개")
        print(f"   - 크롤링 페이지: {current_page - 1}페이지")
        
        print(f"\n📅 일별 게시글 수:")
        for date, count in sorted(daily_stats.items()):
            print(f"   - {date}: {count}개")
        
    except Exception as e:
        print(f"❌ 크롤링 중 오류: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler.driver:
            print("\n🔒 브라우저 종료...")
            crawler.quit()
        
        print("\n✅ 크롤링 완료!")


if __name__ == "__main__":
    crawl_july_2025_free_board()
