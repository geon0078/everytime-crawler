# 개발 가이드

## 개발 환경 설정

```bash
# 개발 의존성 설치
pip install -e ".[dev]"

# 코드 포맷팅
black src/ tests/ examples/

# 린팅
flake8 src/ tests/ examples/

# 타입 체킹
mypy src/

# 테스트 실행
pytest tests/
```

## 프로젝트 구조

```
everytime-crawler/
├── src/everytime_crawler/    # 메인 패키지
│   ├── __init__.py
│   ├── crawler.py           # 크롤러 메인 클래스
│   └── utils.py            # 유틸리티 함수
├── examples/               # 사용 예제
│   └── basic_usage.py
├── tests/                 # 테스트 코드
│   └── test_environment.py
├── debug/                 # 디버그/분석 도구
│   ├── analyze_timetable.py
│   ├── debug_test.py
│   └── debug_timetable.py
├── data/                  # 크롤링 결과 데이터
├── docs/                  # 문서
│   ├── usage.md
│   └── development.md
├── .env.example          # 환경변수 예제
├── requirements.txt      # 의존성 목록
├── pyproject.toml       # 프로젝트 설정
└── README.md            # 프로젝트 개요
```

## 코딩 스타일

- **포맷터**: Black (88자 줄 길이)
- **린터**: Flake8
- **타입 힌트**: MyPy를 통한 정적 타입 체킹
- **독스트링**: Google 스타일

## 새 기능 추가

1. `src/everytime_crawler/` 에 새 모듈 추가
2. `tests/` 에 해당 테스트 작성
3. `examples/` 에 사용 예제 추가
4. `docs/` 문서 업데이트

## 디버깅

### 시간표 HTML 구조 분석

```bash
python debug/analyze_timetable.py
```

### 로그인 페이지 분석

```bash
python debug/debug_test.py
```

### 시간표 파싱 디버깅

```bash
python debug/debug_timetable.py
```

## 배포

```bash
# 빌드
python -m build

# PyPI 업로드 (테스트)
python -m twine upload --repository testpypi dist/*

# PyPI 업로드 (실제)
python -m twine upload dist/*
```

## 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Submit a pull request
