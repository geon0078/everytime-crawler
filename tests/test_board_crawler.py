"""
게시판 크롤링 기능 테스트
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from unittest.mock import Mock, patch
from everytime_crawler import EverytimeCrawler


class TestBoardCrawling(unittest.TestCase):
    """게시판 크롤링 기능 테스트"""
    
    def setUp(self):
        """테스트 셋업"""
        self.crawler = EverytimeCrawler()
    
    def test_board_map_exists(self):
        """게시판 ID 매핑이 존재하는지 확인"""
        from everytime_crawler import BOARD_MAP
        
        self.assertIsInstance(BOARD_MAP, dict)
        self.assertIn("free", BOARD_MAP)
        self.assertIn("secret", BOARD_MAP)
        self.assertEqual(BOARD_MAP["free"], "자유게시판")
    
    def test_get_board_posts_parameters(self):
        """get_board_posts 메서드의 파라미터 검증"""
        # 메서드가 존재하는지 확인
        self.assertTrue(hasattr(self.crawler, 'get_board_posts'))
        
        # 기본 파라미터로 호출 가능한지 확인 (실제 실행은 하지 않음)
        method = getattr(self.crawler, 'get_board_posts')
        self.assertTrue(callable(method))
    
    def test_extract_post_info_methods(self):
        """게시글 정보 추출 메서드들이 존재하는지 확인"""
        required_methods = [
            '_extract_posts_from_current_page',
            '_extract_single_post_info',
            'get_post_detail',
            'save_board_posts_to_csv',
            'save_board_posts_to_json',
            '_save_board_debug_info'
        ]
        
        for method_name in required_methods:
            self.assertTrue(
                hasattr(self.crawler, method_name),
                f"Method {method_name} not found"
            )
    
    def test_save_board_posts_empty_list(self):
        """빈 게시글 리스트 저장 시 처리"""
        # CSV 저장 테스트
        self.crawler.save_board_posts_to_csv([])
        
        # JSON 저장 테스트  
        self.crawler.save_board_posts_to_json([])
        
        # 예외가 발생하지 않으면 성공
        self.assertTrue(True)
    
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_save_board_posts_to_json(self, mock_json_dump, mock_open):
        """JSON 저장 기능 테스트"""
        mock_posts = [
            {
                'title': '테스트 게시글',
                'author': '테스트 사용자',
                'board_id': 'free',
                'created_time': '07/02'
            }
        ]
        
        self.crawler.save_board_posts_to_json(mock_posts, 'test.json')
        
        # 파일이 열렸는지 확인
        mock_open.assert_called_once()
        
        # JSON 덤프가 호출되었는지 확인
        mock_json_dump.assert_called_once()
    
    def test_board_id_validation(self):
        """게시판 ID 검증"""
        from everytime_crawler import BOARD_MAP
        
        valid_boards = list(BOARD_MAP.keys())
        
        # 유효한 게시판 ID들
        for board_id in ['free', 'secret', 'freshman']:
            self.assertIn(board_id, valid_boards)
        
        # 게시판 이름들이 한글인지 확인
        for board_name in BOARD_MAP.values():
            self.assertTrue(any(ord(char) > 127 for char in board_name))  # 한글 포함 확인


class TestBoardCrawlingIntegration(unittest.TestCase):
    """게시판 크롤링 통합 테스트 (실제 네트워크 필요)"""
    
    def setUp(self):
        """테스트 셋업"""
        self.crawler = EverytimeCrawler()
        # 실제 테스트는 환경변수가 설정된 경우만 실행
        self.skip_if_no_credentials()
    
    def skip_if_no_credentials(self):
        """인증 정보가 없으면 테스트 스킵"""
        import os
        if not (os.getenv('EVERYTIME_USERNAME') and os.getenv('EVERYTIME_PASSWORD')):
            self.skipTest("환경변수에 에브리타임 계정 정보가 설정되지 않음")
    
    def test_login_and_board_access(self):
        """로그인 후 게시판 접근 테스트"""
        try:
            # WebDriver 설정
            self.crawler.setup_driver(headless=True)
            
            # 로그인 시도
            login_success = self.crawler.login()
            
            if login_success:
                # 게시판 페이지 접근 테스트
                self.crawler.driver.get(f"{self.crawler.base_url}/free")
                
                # 페이지가 로드되었는지 확인
                self.assertIn("everytime", self.crawler.driver.current_url.lower())
                
                print("✅ 로그인 및 게시판 접근 테스트 성공")
            else:
                self.skipTest("로그인 실패")
                
        except Exception as e:
            self.fail(f"테스트 중 오류 발생: {e}")
            
        finally:
            if hasattr(self.crawler, 'driver') and self.crawler.driver:
                self.crawler.quit()


def run_board_crawling_demo():
    """게시판 크롤링 데모 실행"""
    print("🎯 게시판 크롤링 데모 시작")
    print("=" * 50)
    
    crawler = EverytimeCrawler()
    
    try:
        # 환경변수 확인
        import os
        if not (os.getenv('EVERYTIME_USERNAME') and os.getenv('EVERYTIME_PASSWORD')):
            print("❌ 환경변수에 에브리타임 계정 정보를 설정해주세요.")
            print("   EVERYTIME_USERNAME=your_username")
            print("   EVERYTIME_PASSWORD=your_password")
            return
        
        # WebDriver 설정
        crawler.setup_driver(headless=False)
        
        # 로그인
        if crawler.login():
            print("✅ 로그인 성공!")
            
            # 자유게시판 1페이지만 테스트
            posts = crawler.get_board_posts("free", pages=1, delay=2)
            
            if posts:
                print(f"\n📊 크롤링 결과: {len(posts)}개 게시글")
                
                # 샘플 출력
                for i, post in enumerate(posts[:3], 1):
                    print(f"\n{i}. {post.get('title', 'N/A')}")
                    print(f"   작성자: {post.get('author', 'N/A')}")
                    print(f"   시간: {post.get('created_time', 'N/A')}")
                    print(f"   댓글: {post.get('comment_count', '0')}개")
                
                # 파일 저장
                crawler.save_board_posts_to_json(posts, "data/demo_board_posts.json")
                print("\n💾 결과가 data/demo_board_posts.json에 저장되었습니다.")
                
            else:
                print("❌ 게시글을 찾을 수 없습니다.")
        else:
            print("❌ 로그인 실패!")
            
    except Exception as e:
        print(f"❌ 데모 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler.driver:
            crawler.quit()
        
        print("\n✅ 데모 완료!")


if __name__ == "__main__":
    print("🧪 게시판 크롤링 테스트 실행")
    print("=" * 50)
    
    # 단위 테스트 실행
    print("\n1️⃣ 단위 테스트 실행...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 50)
    
    # 데모 실행
    print("\n2️⃣ 데모 실행...")
    run_board_crawling_demo()
