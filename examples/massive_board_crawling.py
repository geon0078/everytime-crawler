"""
에브리타임 대량 게시판 데이터 크롤링 스크립트
최근 2년간의 모든 게시판 데이터를 체계적으로 수집
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 환경변수 로드
load_dotenv()

from everytime_crawler import EverytimeCrawler, BOARD_MAP
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import threading
import queue
import signal


class MassiveBoardCrawler:
    """대량 게시판 크롤링 전용 클래스"""
    
    def __init__(self):
        self.crawler = None
        self.total_posts = 0
        self.total_boards = 0
        self.failed_boards = []
        self.success_boards = []
        self.start_time = None
        self.stop_crawling = False
        
        # 안전한 종료를 위한 시그널 핸들러
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """안전한 종료를 위한 시그널 핸들러"""
        print(f"\n⚠️ 종료 신호 감지 (Signal {signum})")
        print("안전한 종료를 위해 현재 작업을 완료하는 중...")
        self.stop_crawling = True
    
    def estimate_crawling_scope(self):
        """크롤링 범위 추정"""
        print("📊 크롤링 범위 추정")
        print("=" * 60)
        
        # 게시판별 예상 페이지 수 (경험적 추정)
        board_estimates = {
            "free": 1000,      # 자유게시판 - 가장 활발
            "secret": 800,     # 비밀게시판
            "freshman": 300,   # 새내기게시판
            "graduate": 200,   # 졸업생게시판
            "job": 500,        # 취업게시판
            "exam": 400,       # 시험정보게시판
            "club": 150,       # 동아리게시판
            "market": 250      # 장터게시판
        }
        
        total_estimated_pages = sum(board_estimates.values())
        total_estimated_posts = total_estimated_pages * 20  # 페이지당 약 20개 게시글
        
        print(f"📋 대상 게시판: {len(BOARD_MAP)}개")
        print(f"📄 예상 총 페이지: {total_estimated_pages:,}페이지")
        print(f"📝 예상 총 게시글: {total_estimated_posts:,}개")
        
        # 예상 소요 시간 계산 (페이지당 3초 가정)
        estimated_seconds = total_estimated_pages * 3
        estimated_hours = estimated_seconds / 3600
        
        print(f"⏱️ 예상 소요 시간: {estimated_hours:.1f}시간")
        print(f"💾 예상 데이터 크기: {total_estimated_posts * 0.5 / 1024:.1f}MB")
        
        print("\n⚠️ 주의사항:")
        print("- 이는 추정치이며 실제와 다를 수 있습니다")
        print("- 서버 부하 방지를 위해 적절한 대기시간을 설정합니다")
        print("- 언제든지 Ctrl+C로 안전하게 중단할 수 있습니다")
        
        return board_estimates
    
    def crawl_massive_board_data(self, 
                                target_boards=None, 
                                max_pages_per_board=None,
                                delay_between_pages=3,
                                delay_between_boards=10,
                                save_interval=50):
        """
        대량 게시판 데이터 크롤링
        
        Args:
            target_boards (list): 크롤링할 게시판 ID 리스트 (None이면 모든 게시판)
            max_pages_per_board (int): 게시판당 최대 페이지 수 (None이면 제한 없음)
            delay_between_pages (int): 페이지 간 대기 시간(초)
            delay_between_boards (int): 게시판 간 대기 시간(초)
            save_interval (int): 몇 개 게시글마다 중간 저장할지
        """
        
        if target_boards is None:
            target_boards = list(BOARD_MAP.keys())
        
        if max_pages_per_board is None:
            max_pages_per_board = 1000  # 안전한 기본값
        
        print(f"🚀 대량 게시판 크롤링 시작")
        print(f"📋 대상 게시판: {len(target_boards)}개")
        print(f"📄 게시판당 최대 페이지: {max_pages_per_board}")
        print(f"⏱️ 페이지 간 대기: {delay_between_pages}초")
        print(f"⏱️ 게시판 간 대기: {delay_between_boards}초")
        print("=" * 60)
        
        self.start_time = datetime.now()
        self.crawler = EverytimeCrawler()
        
        try:
            # WebDriver 설정 (헤드리스 모드로 리소스 절약)
            self.crawler.setup_driver(headless=True)
            
            # 로그인
            if not self.crawler.login():
                print("❌ 로그인 실패! 크롤링을 중단합니다.")
                return
            
            print("✅ 로그인 성공!")
            
            # 각 게시판별 크롤링
            for board_idx, board_id in enumerate(target_boards, 1):
                if self.stop_crawling:
                    print("\n🛑 사용자에 의해 크롤링이 중단되었습니다.")
                    break
                
                board_name = BOARD_MAP.get(board_id, board_id)
                print(f"\n📋 [{board_idx}/{len(target_boards)}] {board_name} 크롤링 시작...")
                
                try:
                    # 게시판별 크롤링 실행
                    board_posts = self._crawl_single_board_comprehensive(
                        board_id, 
                        max_pages_per_board, 
                        delay_between_pages,
                        save_interval
                    )
                    
                    if board_posts:
                        self.success_boards.append({
                            'board_id': board_id,
                            'board_name': board_name,
                            'post_count': len(board_posts),
                            'completed_at': datetime.now().isoformat()
                        })
                        
                        self.total_posts += len(board_posts)
                        print(f"✅ {board_name} 완료: {len(board_posts)}개 게시글")
                        
                        # 게시판별 결과 저장
                        self._save_board_results(board_id, board_posts)
                        
                    else:
                        print(f"❌ {board_name}: 게시글을 찾을 수 없음")
                        self.failed_boards.append({
                            'board_id': board_id,
                            'board_name': board_name,
                            'error': 'No posts found'
                        })
                
                except Exception as e:
                    print(f"❌ {board_name} 크롤링 실패: {e}")
                    self.failed_boards.append({
                        'board_id': board_id,
                        'board_name': board_name,
                        'error': str(e)
                    })
                
                # 게시판 간 대기 (마지막 게시판이 아닌 경우)
                if board_idx < len(target_boards) and not self.stop_crawling:
                    print(f"⏳ {delay_between_boards}초 대기 중...")
                    time.sleep(delay_between_boards)
            
            # 최종 결과 저장
            self._save_final_summary()
            
        except Exception as e:
            print(f"❌ 크롤링 중 치명적 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.crawler and self.crawler.driver:
                self.crawler.quit()
            
            self._print_final_statistics()
    
    def _crawl_single_board_comprehensive(self, board_id, max_pages, delay, save_interval):
        """단일 게시판의 포괄적 크롤링"""
        all_posts = []
        page = 1
        consecutive_empty_pages = 0
        max_empty_pages = 5  # 연속으로 빈 페이지가 5개 나오면 중단
        
        print(f"   📄 페이지별 크롤링 시작 (최대 {max_pages}페이지)")
        
        while page <= max_pages and consecutive_empty_pages < max_empty_pages:
            if self.stop_crawling:
                break
            
            try:
                # 현재 페이지 크롤링
                page_posts = self.crawler.get_board_posts(
                    board_id=board_id,
                    pages=1,  # 한 페이지씩 처리
                    delay=delay
                )
                
                if page_posts:
                    all_posts.extend(page_posts)
                    consecutive_empty_pages = 0
                    print(f"     페이지 {page}: {len(page_posts)}개 게시글")
                    
                    # 중간 저장 (메모리 관리)
                    if len(all_posts) % save_interval == 0:
                        self._save_intermediate_results(board_id, all_posts[-save_interval:])
                    
                else:
                    consecutive_empty_pages += 1
                    print(f"     페이지 {page}: 빈 페이지 ({consecutive_empty_pages}/{max_empty_pages})")
                
                # 2년치 데이터인지 확인 (날짜 기반 중단)
                if self._should_stop_by_date(page_posts):
                    print(f"     📅 2년 이전 데이터 도달, 크롤링 중단")
                    break
                
                page += 1
                
                # 진행률 표시
                if page % 10 == 0:
                    elapsed = datetime.now() - self.start_time
                    print(f"     📊 진행: {page}페이지, 총 {len(all_posts)}개 게시글, 경과시간: {elapsed}")
                
            except Exception as e:
                print(f"     ❌ 페이지 {page} 크롤링 실패: {e}")
                consecutive_empty_pages += 1
                page += 1
                continue
        
        print(f"   ✅ 게시판 크롤링 완료: 총 {len(all_posts)}개 게시글")
        return all_posts
    
    def _should_stop_by_date(self, posts):
        """날짜 기반으로 크롤링 중단 여부 결정"""
        if not posts:
            return False
        
        # 2년 전 날짜 계산
        two_years_ago = datetime.now() - timedelta(days=730)
        
        for post in posts:
            created_time = post.get('created_time', '')
            if created_time:
                try:
                    # 에브리타임 날짜 형식 파싱 시도
                    # 예: "07/02", "2023/07/02" 등
                    if '/' in created_time:
                        parts = created_time.split('/')
                        if len(parts) == 2:  # "MM/DD" 형식
                            # 현재 연도 기준으로 파싱
                            current_year = datetime.now().year
                            month, day = int(parts[0]), int(parts[1])
                            post_date = datetime(current_year, month, day)
                            
                            # 만약 미래 날짜라면 작년 데이터로 간주
                            if post_date > datetime.now():
                                post_date = datetime(current_year - 1, month, day)
                            
                        elif len(parts) == 3:  # "YYYY/MM/DD" 형식
                            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                            post_date = datetime(year, month, day)
                        else:
                            continue
                        
                        # 2년 이전 데이터인지 확인
                        if post_date < two_years_ago:
                            return True
                            
                except (ValueError, IndexError):
                    continue
        
        return False
    
    def _save_intermediate_results(self, board_id, posts):
        """중간 결과 저장 (메모리 관리용)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/intermediate_{board_id}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"     ⚠️ 중간 저장 실패: {e}")
    
    def _save_board_results(self, board_id, posts):
        """게시판별 최종 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 저장
        json_filename = f"data/massive_crawl_{board_id}_{timestamp}.json"
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            print(f"     💾 JSON 저장: {json_filename}")
        except Exception as e:
            print(f"     ❌ JSON 저장 실패: {e}")
        
        # CSV 저장
        csv_filename = f"data/massive_crawl_{board_id}_{timestamp}.csv"
        try:
            df = pd.DataFrame(posts)
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"     💾 CSV 저장: {csv_filename}")
        except Exception as e:
            print(f"     ❌ CSV 저장 실패: {e}")
    
    def _save_final_summary(self):
        """최종 크롤링 요약 저장"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        summary = {
            'crawling_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'duration_formatted': str(duration)
            },
            'statistics': {
                'total_posts': self.total_posts,
                'total_boards_attempted': len(BOARD_MAP),
                'successful_boards': len(self.success_boards),
                'failed_boards': len(self.failed_boards)
            },
            'successful_boards': self.success_boards,
            'failed_boards': self.failed_boards
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"data/massive_crawl_summary_{timestamp}.json"
        
        try:
            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"\n📊 크롤링 요약 저장: {summary_filename}")
        except Exception as e:
            print(f"\n❌ 요약 저장 실패: {e}")
    
    def _print_final_statistics(self):
        """최종 통계 출력"""
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else timedelta(0)
        
        print("\n" + "=" * 60)
        print("📊 대량 크롤링 완료 통계")
        print("=" * 60)
        print(f"⏱️ 총 소요 시간: {duration}")
        print(f"📝 총 수집 게시글: {self.total_posts:,}개")
        print(f"✅ 성공한 게시판: {len(self.success_boards)}개")
        print(f"❌ 실패한 게시판: {len(self.failed_boards)}개")
        
        if self.success_boards:
            print("\n✅ 성공한 게시판:")
            for board in self.success_boards:
                print(f"   {board['board_name']}: {board['post_count']:,}개")
        
        if self.failed_boards:
            print("\n❌ 실패한 게시판:")
            for board in self.failed_boards:
                print(f"   {board['board_name']}: {board['error']}")
        
        if self.total_posts > 0:
            avg_time_per_post = duration.total_seconds() / self.total_posts
            print(f"\n📈 평균 게시글당 소요시간: {avg_time_per_post:.2f}초")
        
        print("\n💾 저장된 파일들:")
        print("   data/massive_crawl_*.json - 게시판별 JSON 데이터")
        print("   data/massive_crawl_*.csv - 게시판별 CSV 데이터")
        print("   data/massive_crawl_summary_*.json - 크롤링 요약")


def main():
    """메인 실행 함수"""
    print("🎯 에브리타임 대량 게시판 크롤링")
    print("최근 2년간의 모든 게시판 데이터 수집")
    print("=" * 60)
    
    # 환경변수 확인
    if not os.path.exists('.env'):
        print("❌ .env 파일이 없습니다. .env.example을 참고하여 .env 파일을 생성해주세요.")
        return
    
    # 크롤러 인스턴스 생성
    massive_crawler = MassiveBoardCrawler()
    
    # 크롤링 범위 추정
    board_estimates = massive_crawler.estimate_crawling_scope()
    
    # 사용자 확인
    print("\n" + "=" * 60)
    response = input("대량 크롤링을 시작하시겠습니까? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n🚀 대량 크롤링을 시작합니다...")
        print("언제든지 Ctrl+C를 눌러 안전하게 중단할 수 있습니다.")
        
        # 크롤링 실행
        massive_crawler.crawl_massive_board_data(
            target_boards=None,  # 모든 게시판
            max_pages_per_board=500,  # 게시판당 최대 500페이지 (2년치 추정)
            delay_between_pages=3,  # 페이지 간 3초 대기
            delay_between_boards=10,  # 게시판 간 10초 대기
            save_interval=100  # 100개 게시글마다 중간 저장
        )
        
    else:
        print("❌ 크롤링이 취소되었습니다.")


def quick_test_crawling():
    """빠른 테스트용 크롤링 (소량 데이터)"""
    print("🧪 빠른 테스트 크롤링 (각 게시판 5페이지씩)")
    
    massive_crawler = MassiveBoardCrawler()
    
    # 테스트용 설정
    massive_crawler.crawl_massive_board_data(
        target_boards=['free', 'secret'],  # 2개 게시판만
        max_pages_per_board=5,  # 각 5페이지만
        delay_between_pages=1,  # 빠른 테스트
        delay_between_boards=3,
        save_interval=20
    )


if __name__ == "__main__":
    print("선택하세요:")
    print("1. 전체 대량 크롤링 (2년치)")
    print("2. 빠른 테스트 크롤링")
    
    choice = input("선택 (1/2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        quick_test_crawling()
    else:
        print("잘못된 선택입니다.")
