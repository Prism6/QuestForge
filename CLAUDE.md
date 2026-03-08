# CLAUDE.md - QuestForge

## 프로젝트 개요
QuestForge는 게임 기획자를 위한 AI 퀘스트 생성기입니다.
Streamlit 기반 웹앱으로, Claude API를 사용하여 퀘스트를 자동 생성합니다.

## 기술 스택
- Python 3.11+
- Streamlit (웹 프레임워크)
- Anthropic Claude API (LLM)
- Pandas (데이터 처리)
- openpyxl (엑셀 내보내기)

## 프로젝트 구조
```
QuestForge/
├── app.py              # Streamlit 메인 앱
├── utils/
│   ├── quest_generator.py   # Claude API 호출 로직
│   ├── data_exporter.py     # JSON/Excel 내보내기
│   └── prompts.py           # 프롬프트 템플릿
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 코딩 컨벤션
- 언어: Python
- 스타일: PEP 8 준수
- 함수/변수명: snake_case
- 클래스명: PascalCase
- 독스트링: Google 스타일
- 타입 힌트 사용 권장

## 핵심 기능
1. 장르/테마/난이도 기반 퀘스트 생성
2. JSON 형식 출력
3. Excel 내보내기
4. 생성 히스토리 관리
5. 재생성 기능

## API 사용
- Claude API (claude-sonnet-4-20250514)
- API 키는 환경변수 ANTHROPIC_API_KEY로 관리
- .env 파일은 절대 커밋하지 않음

## 주의사항
- API 키를 코드에 직접 넣지 말 것
- .env 파일은 .gitignore에 포함
- 한국어 UI, 한국어 출력 기본
- 에러 처리 필수 (API 실패, JSON 파싱 실패 등)

## 실행 방법
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 입력

# 앱 실행
streamlit run app.py
```

## 배포
- Streamlit Cloud 사용
- GitHub 연동 자동 배포
- Secrets에 API 키 등록

## 커밋 컨벤션
```
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 리팩토링
test: 테스트 추가
chore: 빌드, 설정 변경
```

## 참고 문서
- 기획서: QuestForge_GDD.md
- Streamlit 문서: https://docs.streamlit.io/
- Anthropic API: https://docs.anthropic.com/
