"""
에브리타임 크롤러 패키지

이 패키지는 에브리타임에서 다음과 같은 정보를 수집할 수 있습니다:
- 시간표 정보 (과목명, 교수, 강의실, 시간)
- 게시판 글 목록 (제목, 작성자, 시간, 댓글수)
- 개별 게시글 상세 정보 (내용, 댓글)

주요 기능:
- 최신 에브리타임 HTML 구조에 최적화된 파싱
- CSV, JSON 형태로 데이터 저장
- 게시판별 크롤링 지원
- 디버깅 및 분석 도구 제공
"""

__version__ = "1.0.0"
__author__ = "GEON AN(<geon.0078@g.eulji.ac.kr>, <EuljiUniversity>)"
__description__ = "에브리타임에서 강의 시간표, 게시판 글 등을 수집하는 파이썬 기반 크롤러"

from .crawler import EverytimeCrawler
from .utils import DataManager, TimetableAnalyzer, BoardAnalyzer, ScheduledCrawler

# 게시판 ID 매핑
BOARD_MAP = {
    "free": "자유게시판",
    "secret": "비밀게시판", 
    "freshman": "새내기게시판",
    "graduate": "졸업생게시판",
    "job": "취업게시판",
    "exam": "시험정보게시판",
    "club": "동아리게시판",
    "market": "장터게시판"
}

__all__ = [
    'EverytimeCrawler',
    'DataManager', 
    'TimetableAnalyzer',
    'BoardAnalyzer',
    'ScheduledCrawler',
    'BOARD_MAP'
]
