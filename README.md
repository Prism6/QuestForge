# QuestForge 🎯

게임 기획자를 위한 AI 퀘스트 생성기

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![Claude](https://img.shields.io/badge/Claude-Sonnet--4-purple)

## 📋 프로젝트 소개

QuestForge는 Claude API를 활용하여 게임 퀘스트를 자동으로 생성해주는 웹 기반 도구입니다.
장르, 테마, 난이도를 설정하면 AI가 퀘스트 이름, NPC, 목표, 보상, 대사까지 자동으로 생성합니다.

### 주요 특징

- ⚡ **빠른 생성**: 30초 이내에 완성도 높은 퀘스트 생성
- 🎨 **맞춤 설정**: 장르/테마/난이도별 커스터마이징
- 📊 **다양한 포맷**: JSON/Excel 내보내기 지원
- 📚 **히스토리 관리**: 생성한 퀘스트 이력 저장
- 🔄 **재생성 기능**: 마음에 들지 않으면 즉시 재생성

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/QuestForge.git
cd QuestForge
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고, Anthropic API 키를 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일을 열어 API 키를 입력하세요:

```
ANTHROPIC_API_KEY=your_api_key_here
```

> API 키는 [Anthropic Console](https://console.anthropic.com/)에서 발급받을 수 있습니다.

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다.

## 📖 사용 방법

### 1. 퀘스트 생성

1. **장르 선택**: RPG, 액션, 시뮬레이션 등 원하는 장르 선택
2. **테마 입력**: 세계관 설정 (예: "중세 판타지 왕국", "사이버펑크 도시")
3. **난이도 설정**: 1~5단계 슬라이더로 조정
4. **퀘스트 타입**: 메인/서브/일일/반복 중 선택
5. **생성 버튼 클릭**: AI가 퀘스트를 자동 생성

### 2. 퀘스트 내보내기

- **JSON 다운로드**: 현재 퀘스트를 JSON 파일로 저장
- **Excel 다운로드**: 전체 히스토리를 Excel 파일로 저장

### 3. 재생성 및 관리

- **재생성**: 같은 조건으로 새로운 퀘스트 생성
- **히스토리**: 왼쪽 사이드바에서 이전 퀘스트 확인
- **초기화**: 히스토리 전체 삭제

## 📁 프로젝트 구조

```
QuestForge/
├── app.py                      # Streamlit 메인 앱
├── utils/
│   ├── __init__.py
│   ├── quest_generator.py      # Claude API 호출 로직
│   ├── data_exporter.py        # JSON/Excel 내보내기
│   └── prompts.py              # 프롬프트 템플릿
├── requirements.txt            # 의존성 목록
├── .env.example                # 환경변수 예제
├── .gitignore                  # Git 제외 파일
├── CLAUDE.md                   # 프로젝트 가이드
├── QuestForge_GDD.md           # 게임 디자인 문서
└── README.md                   # 본 문서
```

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| 언어 | Python 3.11+ |
| 웹 프레임워크 | Streamlit |
| AI 모델 | Claude Sonnet 4 (Anthropic) |
| 데이터 처리 | Pandas |
| 파일 변환 | openpyxl |
| 환경변수 | python-dotenv |

## 📊 생성되는 퀘스트 데이터 구조

```json
{
  "quest_id": "Q001",
  "quest_name": "잃어버린 왕관",
  "quest_type": "main",
  "difficulty": 3,
  "genre": "RPG",
  "theme": "중세 판타지 왕국",
  "npc": {
    "name": "왕실 기사단장 로빈",
    "location": "왕성 대전"
  },
  "objective": {
    "type": "retrieve",
    "target": "황금 왕관",
    "location": "도적단 소굴",
    "count": null
  },
  "rewards": {
    "gold": 500,
    "exp": 1200,
    "items": ["기사단 문장"]
  },
  "dialogue": {
    "accept": "용사여, 왕국의 보물인 황금 왕관이...",
    "progress": "도적단 소굴은 북쪽 숲 끝에 있소...",
    "complete": "역시 당신이었군요! 왕국을 대신하여..."
  },
  "prerequisites": [],
  "next_quest": null
}
```

## 🌐 배포 (Streamlit Cloud)

### 1. GitHub 연동

1. GitHub에 저장소 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. "New app" 클릭하여 저장소 연결

### 2. Secrets 설정

Streamlit Cloud 대시보드에서:

```toml
# .streamlit/secrets.toml
ANTHROPIC_API_KEY = "your_api_key_here"
```

### 3. 배포

자동으로 빌드 및 배포가 진행됩니다.

## 🤝 기여하기

기여를 환영합니다! 이슈를 등록하거나 Pull Request를 보내주세요.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 커밋 컨벤션

```
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 리팩토링
test: 테스트 추가
chore: 빌드, 설정 변경
```

## ⚠️ 주의사항

- API 키를 절대 공개 저장소에 커밋하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있습니다
- Claude API 사용량에 따라 비용이 발생할 수 있습니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 👨‍💻 작성자

**한상범**
- 서강대학교 가상융합전문대학원
- 2025년 3월

## 🔗 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Anthropic Claude API 문서](https://docs.anthropic.com/)
- [기획서 (GDD)](./QuestForge_GDD.md)
- [프로젝트 가이드 (CLAUDE.md)](./CLAUDE.md)

---

**QuestForge로 당신의 게임에 생명을 불어넣으세요!** 🎮✨
