# 에브리타임 크롤러

에브리타임에서 강의 시간표, 게시판 글 등을 수집하는 파이썬 기반 크롤러입니다.

## ✨ 주요 기능

- 🕐 **시간표 크롤링**: 개인 시간표 정보 자동 수집 및 CSV 저장
- 📝 **게시판 크롤링**: 다양한 게시판의 글 목록 수집
- 🔍 **정확한 파싱**: 최신 에브리타임 HTML 구조에 맞춰 최적화
- 📊 **데이터 분석**: 시간표 충돌 검사 및 분석 도구 제공
- 🛠️ **디버깅 도구**: HTML 구조 분석 및 디버깅 스크립트

## 📦 설치

### 방법 1: 개발용 설치 (권장)

```bash
# 저장소 클론
git clone https://github.com/yourusername/everytime-crawler.git
cd everytime-crawler

# 가상환경 생성 및 활성화
conda create -n everytime python=3.11 -y
conda activate everytime

# 패키지 설치 (개발 모드)
pip install -e .

# 또는 개발 도구 포함 설치
pip install -e ".[dev]"
```

### 방법 2: pip 설치

```bash
pip install everytime-crawler
```

## ⚙️ 환경 설정

`.env` 파일을 생성하고 계정 정보를 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```env
EVERYTIME_USERNAME=your_username
EVERYTIME_PASSWORD=your_password
```

## 🚀 사용법

### 빠른 시작

```python
from src.everytime_crawler import EverytimeCrawler

crawler = EverytimeCrawler()

# 로그인
if crawler.login():
    # 시간표 크롤링 (2025년 1학기)
    timetable = crawler.get_timetable(year=2025, semester=1)
    
    # CSV로 저장
    crawler.save_timetable_to_csv(timetable, "data/my_timetable.csv")
    
    # 게시판 글 수집
    posts = crawler.get_board_posts("free", pages=3)
    
    # 브라우저 종료
    crawler.quit()
```

### 시간표 크롤링

```python
# 시간표 정보 수집
timetable = crawler.get_timetable(year=2025, semester=1)

# 수집된 데이터 확인
for subject in timetable:
    print(f"과목: {subject['subject']}")
    print(f"교수: {subject['professor']}")
    print(f"시간: {subject['time']}")
    print(f"강의실: {subject['room']}")
    print("---")
```

### 게시판 크롤링

```python
# 자유게시판 3페이지 크롤링
posts = crawler.get_board_posts("free", pages=3, delay=2)

for post in posts:
    print(f"제목: {post['title']}")
    print(f"작성자: {post['author']}")
    print(f"날짜: {post['created_time']}")
    print(f"댓글: {post['comment_count']}개")
    if post.get('post_link'):
        print(f"링크: {post['post_link']}")
    print("---")

# CSV/JSON 파일로 저장
crawler.save_board_posts_to_csv(posts)
crawler.save_board_posts_to_json(posts)

# 개별 게시글 상세 정보
if posts and posts[0].get('post_link'):
    detail = crawler.get_post_detail(posts[0]['post_link'])
    print(f"내용: {detail['content']}")
    print(f"댓글: {len(detail['comments'])}개")
```

### 대량 게시판 크롤링 (최근 2년치)

```python
# 모든 게시판의 최근 2년치 데이터 크롤링
python examples/massive_board_crawling.py

# 또는 GUI 도구 사용
python examples/crawling_gui.py
```

**주요 특징:**
- 🕒 **자동 날짜 필터링**: 2년 이전 데이터 감지 시 자동 중단
- 🛡️ **안전한 크롤링**: 서버 부하 방지를 위한 적절한 대기시간
- 💾 **중간 저장**: 메모리 효율성을 위한 주기적 데이터 저장
- 🔄 **중단/재개**: Ctrl+C로 안전한 중단 및 재개 지원
- 📊 **진행률 표시**: 실시간 크롤링 진행 상황 모니터링

### 지원하는 게시판

```python
from src.everytime_crawler import BOARD_MAP

# 사용 가능한 게시판 목록
for board_id, board_name in BOARD_MAP.items():
    print(f"{board_id}: {board_name}")

# 출력:
# free: 자유게시판
# secret: 비밀게시판
# freshman: 새내기게시판
# graduate: 졸업생게시판
# job: 취업게시판
# exam: 시험정보게시판
# club: 동아리게시판
# market: 장터게시판
```

## 📁 프로젝트 구조

```
everytime-crawler/
├── src/everytime_crawler/    # 📦 메인 패키지
│   ├── __init__.py
│   ├── crawler.py           # 크롤러 메인 클래스
│   └── utils.py            # 유틸리티 함수
├── examples/               # 📋 사용 예제
│   └── basic_usage.py
├── tests/                 # 🧪 테스트 코드
│   └── test_environment.py
├── debug/                 # 🔧 디버그/분석 도구
│   ├── analyze_timetable.py
│   ├── debug_test.py
│   └── debug_timetable.py
├── data/                  # 💾 크롤링 결과 데이터
├── docs/                  # 📚 문서
│   ├── usage.md
│   └── development.md
├── .env.example          # 🔐 환경변수 예제
├── requirements.txt      # 📋 의존성 목록
├── pyproject.toml       # ⚙️ 프로젝트 설정
└── README.md            # 📖 프로젝트 개요
```

### 대량 데이터 분석

```python
# 크롤링된 데이터 분석
python examples/analyze_massive_data.py
```

**분석 기능:**
- 📊 **전체 통계**: 게시판별 게시글 수, 활동량 분석
- 👥 **사용자 패턴**: 작성자별 활동, 댓글 패턴 분석  
- 🔍 **콘텐츠 트렌드**: 인기 키워드, 주제 분석
- 📈 **시각화**: 차트와 그래프로 데이터 시각화
- 📋 **보고서**: JSON/텍스트 형태의 종합 분석 보고서

## 🛠️ 개발 도구

### 분석 및 디버깅

```bash
# 시간표 HTML 구조 분석
python debug/analyze_timetable.py

# 로그인 페이지 디버깅
python debug/debug_test.py

# 시간표 파싱 디버깅
python debug/debug_timetable.py
```
## 📚 문서

더 자세한 정보는 다음 문서를 참조하세요:

- **[사용법 가이드](docs/usage.md)**: 상세한 사용법과 API 레퍼런스
- **[개발 가이드](docs/development.md)**: 개발 환경 설정 및 기여 방법

## ⚠️ 주의사항

**중요**: 이 크롤러는 교육 목적으로만 사용하세요.

- 에브리타임 서비스 약관을 준수하세요
- 과도한 요청으로 서버에 부하를 주지 마세요
- 수집한 데이터는 개인정보 보호법을 준수하여 처리하세요
- 크롤링 간격을 적절히 조절하세요

## 🔧 문제 해결

### Chrome WebDriver 오류
WebDriver Manager가 자동으로 Chrome 버전에 맞는 드라이버를 다운로드합니다.

### 로그인 실패
1. `.env` 파일의 계정 정보 확인
2. 에브리타임 웹사이트에서 직접 로그인 테스트
3. 2단계 인증이 설정된 경우 해제

### 시간표 파싱 오류
에브리타임 HTML 구조가 변경되었을 수 있습니다:
```bash
# 디버그 도구를 사용하여 분석
python debug/analyze_timetable.py
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📧 연락처

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!
├── .env.example         # 환경변수 템플릿
└── README.md           # 프로젝트 문서
```

## 데이터 형식

### 시간표 데이터
```json
{
  "subject_name": "컴퓨터과학개론",
  "time": "월 3,4교시",
  "room": "공학관 101호",
  "professor": "김교수",
  "collected_at": "2025-07-02T10:30:00"
}
```

### 게시판 데이터
```json
{
  "title": "게시글 제목",
  "author": "작성자",
  "created_time": "07/02",
  "comment_count": "5",
  "post_link": "https://everytime.kr/...",
  "board_id": "free",
  "collected_at": "2025-07-02T10:30:00"
}
```

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 면책조항

이 도구는 교육 목적으로만 제공됩니다. 사용자는 관련 법률과 서비스 약관을 준수할 책임이 있습니다.
