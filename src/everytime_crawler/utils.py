"""
에브리타임 크롤러 유틸리티 함수들
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import os
import time

class DataManager:
    """데이터 관리 유틸리티 클래스"""
    
    @staticmethod
    def save_to_json(data, filename=None):
        """데이터를 JSON 파일로 저장"""
        if filename is None:
            filename = f"everytime_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"데이터가 {filename}에 저장되었습니다.")
        return filename
    
    @staticmethod
    def load_from_json(filename):
        """JSON 파일에서 데이터 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"파일 {filename}을 찾을 수 없습니다.")
            return None
        except json.JSONDecodeError:
            print(f"파일 {filename}의 JSON 형식이 올바르지 않습니다.")
            return None
    
    @staticmethod
    def save_to_excel(data, filename=None):
        """데이터를 Excel 파일로 저장"""
        if filename is None:
            filename = f"everytime_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        if isinstance(data, dict):
            # 딕셔너리인 경우 각 키를 시트로 저장
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, sheet_data in data.items():
                    if isinstance(sheet_data, list) and sheet_data:
                        df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # 리스트인 경우 단일 시트로 저장
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
        
        print(f"데이터가 {filename}에 저장되었습니다.")
        return filename
    
    @staticmethod
    def merge_csv_files(file_pattern, output_filename=None):
        """같은 형식의 CSV 파일들을 하나로 합치기"""
        import glob
        
        csv_files = glob.glob(file_pattern)
        if not csv_files:
            print(f"패턴 {file_pattern}에 해당하는 파일이 없습니다.")
            return None
        
        all_data = []
        for file in csv_files:
            df = pd.read_csv(file, encoding='utf-8-sig')
            all_data.append(df)
        
        merged_df = pd.concat(all_data, ignore_index=True)
        
        if output_filename is None:
            output_filename = f"merged_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        merged_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"파일 {len(csv_files)}개를 {output_filename}으로 합쳤습니다.")
        return output_filename

class TimetableAnalyzer:
    """시간표 분석 유틸리티 클래스"""
    
    @staticmethod
    def parse_time_string(time_str):
        """시간 문자열 파싱 (예: '월 3,4교시' -> 요일과 교시 정보)"""
        import re
        
        days = {'월': 'Monday', '화': 'Tuesday', '수': 'Wednesday', 
                '목': 'Thursday', '금': 'Friday', '토': 'Saturday', '일': 'Sunday'}
        
        # 요일 추출
        day_match = re.search(r'[월화수목금토일]', time_str)
        day = days.get(day_match.group()) if day_match else None
        
        # 교시 추출
        period_match = re.findall(r'\d+', time_str)
        periods = [int(p) for p in period_match] if period_match else []
        
        return {
            'day': day,
            'periods': periods,
            'original': time_str
        }
    
    @staticmethod
    def check_time_conflicts(timetable_data):
        """시간표 충돌 확인"""
        conflicts = []
        parsed_schedule = []
        
        for subject in timetable_data:
            time_info = TimetableAnalyzer.parse_time_string(subject.get('time', ''))
            parsed_schedule.append({
                'subject': subject,
                'time_info': time_info
            })
        
        # 충돌 확인
        for i in range(len(parsed_schedule)):
            for j in range(i + 1, len(parsed_schedule)):
                schedule1 = parsed_schedule[i]
                schedule2 = parsed_schedule[j]
                
                # 같은 요일인지 확인
                if schedule1['time_info']['day'] == schedule2['time_info']['day']:
                    # 교시 겹치는지 확인
                    periods1 = set(schedule1['time_info']['periods'])
                    periods2 = set(schedule2['time_info']['periods'])
                    
                    if periods1.intersection(periods2):
                        conflicts.append({
                            'subject1': schedule1['subject']['subject_name'],
                            'subject2': schedule2['subject']['subject_name'],
                            'day': schedule1['time_info']['day'],
                            'conflicted_periods': list(periods1.intersection(periods2))
                        })
        
        return conflicts
    
    @staticmethod
    def generate_weekly_schedule(timetable_data):
        """주간 시간표 매트릭스 생성"""
        schedule_matrix = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            schedule_matrix[day] = {}
        
        for subject in timetable_data:
            time_info = TimetableAnalyzer.parse_time_string(subject.get('time', ''))
            day = time_info['day']
            periods = time_info['periods']
            
            if day and periods:
                for period in periods:
                    if period not in schedule_matrix[day]:
                        schedule_matrix[day][period] = []
                    schedule_matrix[day][period].append({
                        'subject': subject['subject_name'],
                        'professor': subject.get('professor', ''),
                        'room': subject.get('room', '')
                    })
        
        return schedule_matrix

class BoardAnalyzer:
    """게시판 분석 유틸리티 클래스"""
    
    @staticmethod
    def get_post_statistics(board_data):
        """게시판 글 통계 분석"""
        if not board_data:
            return {}
        
        df = pd.DataFrame(board_data)
        
        stats = {
            'total_posts': len(df),
            'authors': df['author'].value_counts().to_dict(),
            'posts_by_time': df['created_time'].value_counts().to_dict(),
            'average_comments': 0,
            'popular_posts': []
        }
        
        # 댓글 수 통계
        if 'comment_count' in df.columns:
            df['comment_count_int'] = pd.to_numeric(df['comment_count'], errors='coerce').fillna(0)
            stats['average_comments'] = df['comment_count_int'].mean()
            
            # 인기글 (댓글 많은 순)
            popular = df.nlargest(5, 'comment_count_int')[['title', 'author', 'comment_count']].to_dict('records')
            stats['popular_posts'] = popular
        
        return stats
    
    @staticmethod
    def search_posts(board_data, keyword):
        """게시글에서 키워드 검색"""
        if not board_data:
            return []
        
        df = pd.DataFrame(board_data)
        
        # 제목에서 키워드 검색
        mask = df['title'].str.contains(keyword, case=False, na=False)
        matched_posts = df[mask].to_dict('records')
        
        return matched_posts
    
    @staticmethod
    def get_trending_keywords(board_data, top_n=10):
        """게시판의 트렌드 키워드 추출"""
        if not board_data:
            return []
        
        import re
        from collections import Counter
        
        all_titles = [post.get('title', '') for post in board_data]
        all_text = ' '.join(all_titles)
        
        # 한글 키워드 추출 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', all_text)
        
        # 빈도 계산
        word_counts = Counter(korean_words)
        
        # 상위 키워드 반환
        return word_counts.most_common(top_n)

class ScheduledCrawler:
    """스케줄링된 크롤링 유틸리티"""
    
    def __init__(self, crawler_instance):
        self.crawler = crawler_instance
        self.jobs = []
    
    def add_daily_crawl(self, time_str, target_type, **kwargs):
        """매일 정해진 시간에 크롤링 작업 추가"""
        import schedule
        
        def job():
            try:
                if target_type == 'timetable':
                    data = self.crawler.get_timetable(**kwargs)
                    print(f"[{datetime.now()}] 시간표 {len(data)}개 수집 완료")
                elif target_type == 'board':
                    board_id = kwargs.get('board_id', 'free')
                    data = self.crawler.get_board_posts(board_id, **kwargs)
                    print(f"[{datetime.now()}] 게시판 {len(data)}개 수집 완료")
            except Exception as e:
                print(f"[{datetime.now()}] 크롤링 오류: {e}")
        
        schedule.every().day.at(time_str).do(job)
        self.jobs.append(job)
        print(f"매일 {time_str}에 {target_type} 크롤링 작업이 예약되었습니다.")
    
    def run_scheduled_jobs(self):
        """예약된 작업들 실행"""
        import schedule
        
        print("스케줄된 크롤링 작업을 시작합니다...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
