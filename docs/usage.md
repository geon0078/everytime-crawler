# 에브리타임 크롤러 사용법

## 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/everytime-crawler.git
cd everytime-crawler

# 가상환경 생성 및 활성화
conda create -n everytime python=3.11
conda activate everytime

# 패키지 설치
pip install -e .

# 또는 개발 의존성 포함 설치
pip install -e ".[dev]"
```

## 환경 설정

`.env` 파일을 생성하고 에브리타임 계정 정보를 입력하세요:

```env
EVERYTIME_USERNAME=your_username
EVERYTIME_PASSWORD=your_password
```

## 기본 사용법

### 시간표 크롤링

```python
from src.everytime_crawler import EverytimeCrawler

# 크롤러 인스턴스 생성
crawler = EverytimeCrawler()

# 로그인
if crawler.login():
    # 시간표 크롤링 (2025년 1학기)
    timetable = crawler.get_timetable(year=2025, semester=1)
    
    # CSV로 저장
    crawler.save_timetable_to_csv(timetable, "my_timetable.csv")
    
    # 브라우저 종료
    crawler.quit()
```

### 게시판 크롤링

```python
# 자유게시판 글 목록 가져오기
posts = crawler.get_board_posts("free", pages=3)

for post in posts:
    print(f"제목: {post['title']}")
    print(f"작성자: {post['author']}")
    print(f"날짜: {post['date']}")
    print("---")
```

## API 레퍼런스

### EverytimeCrawler 클래스

#### 메서드

- `login()`: 에브리타임에 로그인
- `get_timetable(year, semester)`: 지정된 학기의 시간표 가져오기
- `get_board_posts(board_name, pages=1)`: 게시판 글 목록 가져오기
- `save_timetable_to_csv(timetable, filename)`: 시간표를 CSV 파일로 저장
- `quit()`: 브라우저 종료

#### 시간표 데이터 구조

```python
{
    "subject": "강의명",
    "professor": "교수명", 
    "room": "강의실",
    "time": "월1,2,3"
}
```

## 문제 해결

### 로그인 실패
- `.env` 파일의 계정 정보가 정확한지 확인
- 에브리타임 웹사이트에서 수동 로그인이 가능한지 확인

### 시간표 파싱 오류
- `debug/` 폴더의 분석 스크립트 사용
- 에브리타임 HTML 구조 변경 가능성 확인

### 브라우저 관련 오류
- Chrome 브라우저와 ChromeDriver 버전 호환성 확인
- 헤드리스 모드 비활성화하여 디버깅
