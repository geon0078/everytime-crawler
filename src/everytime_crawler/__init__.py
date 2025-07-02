"""
에브리타임 크롤러 패키지
"""

__version__ = "1.0.0"
__author__ = "GEON AN(<geon.0078@g.eulji.ac.kr>, <EuljiUniversity>)"
__description__ = "에브리타임에서 강의 시간표, 게시판 글 등을 수집하는 파이썬 기반 크롤러"

from .crawler import EverytimeCrawler
from .utils import DataManager, TimetableAnalyzer, BoardAnalyzer, ScheduledCrawler

__all__ = [
    'EverytimeCrawler',
    'DataManager', 
    'TimetableAnalyzer',
    'BoardAnalyzer',
    'ScheduledCrawler'
]
