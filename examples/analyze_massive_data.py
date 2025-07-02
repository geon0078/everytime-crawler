"""
대량 크롤링 데이터 분석 도구
"""

import os
import json
import pandas as pd
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re


class MassiveCrawlingAnalyzer:
    """대량 크롤링 데이터 분석 클래스"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.crawling_data = {}
        self.summary_data = None
        
    def load_crawling_data(self):
        """크롤링된 데이터 로드"""
        print("📂 크롤링 데이터 로드 중...")
        
        # JSON 파일들 찾기
        json_files = glob.glob(os.path.join(self.data_dir, "massive_crawl_*.json"))
        summary_files = glob.glob(os.path.join(self.data_dir, "massive_crawl_summary_*.json"))
        
        print(f"   데이터 파일 {len(json_files)}개 발견")
        print(f"   요약 파일 {len(summary_files)}개 발견")
        
        # 게시판별 데이터 로드
        for json_file in json_files:
            filename = os.path.basename(json_file)
            
            # 파일명에서 게시판 ID 추출
            match = re.search(r'massive_crawl_(\w+)_\d+\.json', filename)
            if match:
                board_id = match.group(1)
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.crawling_data[board_id] = data
                    print(f"   ✅ {board_id}: {len(data)}개 게시글 로드")
                    
                except Exception as e:
                    print(f"   ❌ {filename} 로드 실패: {e}")
        
        # 요약 데이터 로드 (가장 최신 것)
        if summary_files:
            latest_summary = max(summary_files, key=os.path.getctime)
            try:
                with open(latest_summary, 'r', encoding='utf-8') as f:
                    self.summary_data = json.load(f)
                print(f"   📊 요약 데이터 로드: {os.path.basename(latest_summary)}")
            except Exception as e:
                print(f"   ❌ 요약 데이터 로드 실패: {e}")
        
        return len(self.crawling_data) > 0
    
    def generate_overall_statistics(self):
        """전체 통계 생성"""
        print("\n📊 전체 통계 분석")
        print("=" * 50)
        
        if not self.crawling_data:
            print("❌ 로드된 데이터가 없습니다.")
            return
        
        total_posts = sum(len(posts) for posts in self.crawling_data.values())
        total_boards = len(self.crawling_data)
        
        print(f"📋 분석된 게시판 수: {total_boards}개")
        print(f"📝 총 게시글 수: {total_posts:,}개")
        
        # 게시판별 게시글 수
        print(f"\n📋 게시판별 게시글 수:")
        board_counts = {}
        for board_id, posts in self.crawling_data.items():
            count = len(posts)
            board_counts[board_id] = count
            print(f"   {board_id}: {count:,}개")
        
        # 가장 활발한 게시판
        most_active_board = max(board_counts, key=board_counts.get)
        print(f"\n🔥 가장 활발한 게시판: {most_active_board} ({board_counts[most_active_board]:,}개)")
        
        return {
            'total_posts': total_posts,
            'total_boards': total_boards,
            'board_counts': board_counts,
            'most_active_board': most_active_board
        }
    
    def analyze_posting_patterns(self):
        """게시글 작성 패턴 분석"""
        print("\n📈 게시글 작성 패턴 분석")
        print("=" * 50)
        
        all_posts = []
        for board_id, posts in self.crawling_data.items():
            for post in posts:
                post['board_id'] = board_id
                all_posts.append(post)
        
        if not all_posts:
            print("❌ 분석할 데이터가 없습니다.")
            return
        
        # DataFrame 생성
        df = pd.DataFrame(all_posts)
        
        print(f"📊 총 분석 대상: {len(df)}개 게시글")
        
        # 작성자 분석
        if 'author' in df.columns:
            author_counts = df['author'].value_counts()
            print(f"\n✍️ 상위 작성자 (TOP 10):")
            for i, (author, count) in enumerate(author_counts.head(10).items(), 1):
                print(f"   {i:2d}. {author}: {count}개")
        
        # 댓글 수 분석
        if 'comment_count' in df.columns:
            df['comment_count'] = pd.to_numeric(df['comment_count'], errors='coerce').fillna(0)
            
            avg_comments = df['comment_count'].mean()
            max_comments = df['comment_count'].max()
            
            print(f"\n💬 댓글 통계:")
            print(f"   평균 댓글 수: {avg_comments:.1f}개")
            print(f"   최대 댓글 수: {max_comments}개")
            
            # 댓글이 많은 게시글
            top_commented = df.nlargest(5, 'comment_count')
            print(f"\n🔥 댓글 많은 게시글 (TOP 5):")
            for i, (_, post) in enumerate(top_commented.iterrows(), 1):
                title = post.get('title', 'N/A')[:50]
                comments = post.get('comment_count', 0)
                board = post.get('board_id', 'N/A')
                print(f"   {i}. [{board}] {title}... ({comments}개)")
        
        # 조회수 분석 (있는 경우)
        if 'view_count' in df.columns:
            df['view_count'] = pd.to_numeric(df['view_count'], errors='coerce').fillna(0)
            
            avg_views = df['view_count'].mean()
            max_views = df['view_count'].max()
            
            print(f"\n👁️ 조회수 통계:")
            print(f"   평균 조회수: {avg_views:.1f}회")
            print(f"   최대 조회수: {max_views}회")
        
        return df
    
    def analyze_content_trends(self):
        """콘텐츠 트렌드 분석"""
        print("\n📝 콘텐츠 트렌드 분석")
        print("=" * 50)
        
        all_titles = []
        for board_id, posts in self.crawling_data.items():
            for post in posts:
                title = post.get('title', '')
                if title:
                    all_titles.append(title)
        
        if not all_titles:
            print("❌ 분석할 제목 데이터가 없습니다.")
            return
        
        print(f"📊 분석 대상 제목: {len(all_titles)}개")
        
        # 단어 빈도 분석 (간단한 키워드 추출)
        all_text = ' '.join(all_titles)
        
        # 한글 키워드 추출 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', all_text)
        
        # 불용어 제거
        stop_words = {'이번', '저번', '다음', '지난', '오늘', '내일', '어제', '그냥', '진짜', '정말', '완전', '너무', '엄청', '되게', '좀'}
        korean_words = [word for word in korean_words if word not in stop_words]
        
        word_counts = Counter(korean_words)
        
        print(f"\n🔍 인기 키워드 (TOP 20):")
        for i, (word, count) in enumerate(word_counts.most_common(20), 1):
            print(f"   {i:2d}. {word}: {count}회")
        
        # 게시판별 인기 키워드
        print(f"\n📋 게시판별 인기 키워드:")
        for board_id, posts in self.crawling_data.items():
            board_titles = [post.get('title', '') for post in posts]
            board_text = ' '.join(board_titles)
            board_words = re.findall(r'[가-힣]{2,}', board_text)
            board_words = [word for word in board_words if word not in stop_words]
            
            if board_words:
                board_word_counts = Counter(board_words)
                top_words = board_word_counts.most_common(5)
                word_str = ', '.join([f"{word}({count})" for word, count in top_words])
                print(f"   {board_id}: {word_str}")
        
        return word_counts
    
    def generate_visualizations(self):
        """시각화 생성"""
        print("\n📊 시각화 생성")
        print("=" * 50)
        
        try:
            # 게시판별 게시글 수 차트
            board_counts = {board_id: len(posts) for board_id, posts in self.crawling_data.items()}
            
            plt.figure(figsize=(12, 8))
            
            # 1. 게시판별 게시글 수
            plt.subplot(2, 2, 1)
            boards = list(board_counts.keys())
            counts = list(board_counts.values())
            
            plt.bar(boards, counts, color='skyblue')
            plt.title('게시판별 게시글 수')
            plt.xlabel('게시판')
            plt.ylabel('게시글 수')
            plt.xticks(rotation=45)
            
            # 2. 게시판별 비율 (파이 차트)
            plt.subplot(2, 2, 2)
            plt.pie(counts, labels=boards, autopct='%1.1f%%')
            plt.title('게시판별 게시글 비율')
            
            # 3. 댓글 수 분포 (모든 게시글)
            all_comments = []
            for posts in self.crawling_data.values():
                for post in posts:
                    comment_count = post.get('comment_count', '0')
                    try:
                        all_comments.append(int(comment_count))
                    except:
                        all_comments.append(0)
            
            if all_comments:
                plt.subplot(2, 2, 3)
                plt.hist(all_comments, bins=20, color='lightgreen', alpha=0.7)
                plt.title('댓글 수 분포')
                plt.xlabel('댓글 수')
                plt.ylabel('게시글 수')
            
            # 4. 게시판별 평균 댓글 수
            plt.subplot(2, 2, 4)
            board_avg_comments = {}
            
            for board_id, posts in self.crawling_data.items():
                comments = []
                for post in posts:
                    comment_count = post.get('comment_count', '0')
                    try:
                        comments.append(int(comment_count))
                    except:
                        comments.append(0)
                
                if comments:
                    board_avg_comments[board_id] = sum(comments) / len(comments)
            
            if board_avg_comments:
                boards = list(board_avg_comments.keys())
                avg_comments = list(board_avg_comments.values())
                
                plt.bar(boards, avg_comments, color='orange')
                plt.title('게시판별 평균 댓글 수')
                plt.xlabel('게시판')
                plt.ylabel('평균 댓글 수')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"data/analysis_charts_{timestamp}.png"
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            
            print(f"📊 차트 저장: {chart_filename}")
            plt.show()
            
        except ImportError:
            print("⚠️ matplotlib가 설치되지 않아 시각화를 생성할 수 없습니다.")
            print("   pip install matplotlib seaborn 으로 설치하세요.")
        except Exception as e:
            print(f"❌ 시각화 생성 중 오류: {e}")
    
    def generate_analysis_report(self):
        """종합 분석 보고서 생성"""
        print("\n📋 종합 분석 보고서 생성")
        print("=" * 50)
        
        # 분석 실행
        overall_stats = self.generate_overall_statistics()
        df = self.analyze_posting_patterns()
        word_counts = self.analyze_content_trends()
        
        # 보고서 생성
        report = {
            'analysis_info': {
                'generated_at': datetime.now().isoformat(),
                'data_source': 'massive board crawling',
                'analyzer_version': '1.0.0'
            },
            'overall_statistics': overall_stats,
            'content_trends': {
                'top_keywords': word_counts.most_common(50) if word_counts else [],
                'total_unique_words': len(word_counts) if word_counts else 0
            }
        }
        
        # DataFrame 통계 추가
        if df is not None and not df.empty:
            report['posting_patterns'] = {
                'total_posts_analyzed': len(df),
                'unique_authors': df['author'].nunique() if 'author' in df.columns else 0,
                'average_comments': float(df['comment_count'].mean()) if 'comment_count' in df.columns else 0,
                'max_comments': int(df['comment_count'].max()) if 'comment_count' in df.columns else 0
            }
        
        # 요약 데이터 추가
        if self.summary_data:
            report['crawling_summary'] = self.summary_data
        
        # 보고서 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"data/analysis_report_{timestamp}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"📋 분석 보고서 저장: {report_filename}")
            
            # 간단한 텍스트 요약도 생성
            summary_filename = f"data/analysis_summary_{timestamp}.txt"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write("에브리타임 대량 크롤링 데이터 분석 요약\n")
                f.write("=" * 50 + "\n\n")
                
                if overall_stats:
                    f.write(f"총 게시판 수: {overall_stats['total_boards']}개\n")
                    f.write(f"총 게시글 수: {overall_stats['total_posts']:,}개\n")
                    f.write(f"가장 활발한 게시판: {overall_stats['most_active_board']}\n\n")
                
                if word_counts:
                    f.write("인기 키워드 TOP 10:\n")
                    for i, (word, count) in enumerate(word_counts.most_common(10), 1):
                        f.write(f"{i:2d}. {word}: {count}회\n")
            
            print(f"📝 요약 파일 저장: {summary_filename}")
            
        except Exception as e:
            print(f"❌ 보고서 저장 실패: {e}")
        
        return report


def main():
    """메인 실행 함수"""
    print("📊 에브리타임 대량 크롤링 데이터 분석")
    print("=" * 60)
    
    # 분석기 인스턴스 생성
    analyzer = MassiveCrawlingAnalyzer()
    
    # 데이터 로드
    if not analyzer.load_crawling_data():
        print("❌ 분석할 크롤링 데이터가 없습니다.")
        print("먼저 massive_board_crawling.py를 실행하여 데이터를 수집하세요.")
        return
    
    try:
        # 종합 분석 실행
        analyzer.generate_analysis_report()
        
        # 시각화 생성 (선택사항)
        create_charts = input("\n시각화 차트를 생성하시겠습니까? (y/N): ").strip().lower()
        if create_charts in ['y', 'yes']:
            analyzer.generate_visualizations()
        
        print("\n✅ 데이터 분석이 완료되었습니다!")
        print("📂 결과 파일들이 data/ 폴더에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
