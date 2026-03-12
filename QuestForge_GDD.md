# QuestForge - AI 퀘스트 생성기

## 1. 프로젝트 개요

### 1.1 프로젝트 정보
| 항목 | 내용 |
|------|------|
| 프로젝트명 | QuestForge |
| 버전 | 1.3.0 |
| 작성자 | 한상범 |
| 작성일 | 2025.03 |
| 최종 수정 | 2026.03.12 |
| 기술 스택 | Python 3.11+, Streamlit, Claude API, pandas, openpyxl |

---

### 1.2 기획 의도

게임 업계에서 퀘스트 1개를 처음부터 기획·작성하는 데 숙련된 기획자도 평균 30분~1시간이 소요된다. 중소 개발사나 인디 팀은 기획 인력 자체가 부족하고, 대형 스튜디오에서도 반복적인 서브 퀘스트·일일 퀘스트 초안 작업은 고급 기획자의 시간을 잠식하는 비효율 영역이다.

**QuestForge는 이 문제를 정면으로 해결한다.**

장르·테마·난이도·타입이라는 4가지 조건만 입력하면, Claude AI가 스토리·NPC·목표·보상·대사를 포함한 완성도 높은 퀘스트 초안을 30초 이내에 생성한다. 기획자는 "무엇을 만들지" 고민하는 시간 대신 **"어떻게 더 좋게 만들지"에만 집중**할 수 있다.

단순 텍스트 생성에 그치지 않고, 즉시 게임 데이터 파이프라인에 투입 가능한 **JSON·Excel 포맷**으로 출력하여 실무 워크플로우에 바로 연결된다. 결과가 마음에 들지 않으면 한 번의 클릭으로 재생성하고, 전체 히스토리를 일괄 Excel로 내보내 데이터 테이블에 붙여 넣으면 된다.

이 툴이 팀에 정착되는 순간, 퀘스트 초안 작업의 속도는 **10배 이상** 빨라진다.

---

### 1.3 타겟 유저
| 유저 유형 | 사용 목적 |
|----------|----------|
| 게임 기획자 | 퀘스트 초안 빠른 생성, 아이디어 발상 |
| 인디 개발자 | 1인 개발 시 기획 리소스 절감 |
| 게임 PD/디렉터 | 퀘스트 방향성 검토용 샘플 생성 |

### 1.4 핵심 가치 (USP)
1. **속도**: 퀘스트 1개 생성에 30초 이내
2. **일관성**: 정해진 포맷(QuestData 스키마)으로 출력하여 즉시 실무 활용 가능
3. **커스터마이징**: 장르 6종 × 테마 자유입력 × 난이도 5단계 × 타입 4종 조합
4. **내보내기**: JSON(단건) / Excel(전체 히스토리) 포맷으로 데이터 테이블 직접 연동

---

## 2. 기능 정의

### 2.1 핵심 기능 (MVP)

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| 장르 선택 | RPG·액션·시뮬레이션·어드벤처·MMORPG·로그라이크 (드롭다운) | P0 |
| 테마 입력 | 세계관/배경 자유 텍스트 입력 (예: "판타지 왕국", "사이버펑크 도시") | P0 |
| 난이도 설정 | 1~5단계 슬라이더. 단계별로 보상 골드 범위가 다름 (단계 1: 100~200G, 단계 5: 1000~2000G) | P0 |
| 퀘스트 타입 | 메인·서브·일일·반복 (드롭다운). 타입별로 프롬프트 내 스토리 방향이 다르게 제어됨 | P0 |
| 퀘스트 생성 | 사이드바 조건을 조합한 프롬프트를 `PromptBuilder`가 생성 → `LLMClient`를 통해 Claude API 호출 → 응답 JSON을 `QuestData` 도메인 객체로 파싱 | P0 |
| 결과 출력 | 퀘스트명·설명(description)·장르·타입·난이도·보상 골드·NPC 정보·목표·보상 상세·수락/진행/완료 대사를 메인 영역에 표시 | P0 |

**퀘스트 타입별 생성 방향:**
| 타입 | 스토리 방향 |
|------|-------------|
| 메인 | 스토리 중심, 세계관에 영향을 주는 사건, 주요 NPC와 상호작용 |
| 서브 | 지역 주민의 일상 문제 해결, 소소하지만 개성 있는 스토리 |
| 일일 | 간단하고 반복 가능한 작업, 명확한 목표와 즉각적인 보상 |
| 반복 | 수집·처치 중심의 단순 과제, 효율적인 설명 |

### 2.2 부가 기능

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| JSON 내보내기 | 현재 표시 중인 퀘스트 1건을 JSON 파일로 다운로드. 파일명 형식: `quest_YYYYMMDD_HHMMSS.json` | P1 |
| Excel 내보내기 | 세션 내 생성된 전체 퀘스트 히스토리를 단일 Excel 파일로 내보내기. 파일명 형식: `quest_YYYYMMDD_HHMMSS.xlsx`. 21개 컬럼을 평면 구조로 정규화하여 출력 (4.3 참조) | P1 |
| 히스토리 | 세션 내 생성된 퀘스트 목록을 사이드바에 최근 5건 표시 (quest_name·genre·difficulty·quest_type). 세션 종료 시 초기화됨 | P1 |
| 재생성 | 현재 퀘스트의 quest_id·genre·theme·difficulty·quest_type을 유지한 채 새로운 스토리로 재생성. 히스토리에서도 동일 quest_id의 항목이 갱신됨 | P1 |
| 히스토리 초기화 | 버튼 클릭으로 전체 히스토리와 현재 퀘스트를 초기화 | P1 |

### 2.3 향후 확장 기능 (v2.0)

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| 유닛 테스트 | `QuestData.from_dict()`, `ExportStrategy`, `QuestGenerator` Mock 테스트 | P1 |
| 커스텀 예외 클래스 | `QuestGenerationError`, `QuestValidationError` 도입으로 에러 타입 구체화 | P1 |
| `QuestType` Enum | 문자열 리터럴 `"main"` 등을 `QuestType(str, Enum)`으로 교체하여 타입 안전성 강화 | P2 |
| 히스토리 영속성 | 세션 재시작 시 히스토리 소멸 문제 해결. 로컬 JSON 파일 또는 SQLite 저장 | P2 |
| 퀘스트 체인 생성 | 연속 퀘스트(next_quest 필드 활용) 자동 설계 | P2 |
| 보상 밸런스 계산기 | 난이도 대비 보상 적정성 분석 및 시각화 | P2 |
| pydantic 마이그레이션 | 현재 `dataclass` 기반 `QuestData`를 `pydantic.BaseModel`로 교체. 자동 유효성 검증·JSON 직렬화 내장 | P2 |
| 다국어 지원 | UI 문자열을 i18n 파일로 분리, 한/영 전환 기능 | P3 |
| 커스텀 프롬프트 | 고급 유저용 프롬프트 직접 편집 모드 | P3 |

---

## 3. UI/UX 설계

### 3.1 화면 구성

```
┌─────────────────────────────────────────────────────────┐
│  QuestForge - AI 퀘스트 생성기              [GitHub]    │
├─────────────────┬───────────────────────────────────────┤
│                 │                                       │
│  [사이드바]      │  [메인 영역]                          │
│                 │                                       │
│  📌 장르 선택    │  ┌─────────────────────────────────┐  │
│  [RPG ▼]        │  │  🎯 퀘스트명                     │  │
│                 │  │                                 │  │
│  📝 테마 입력    │  │  [설명 카드 — 스토리 2~3문장]    │  │
│  [___________]  │  │                                 │  │
│                 │  │  장르 | 타입 | 난이도 | 골드     │  │
│  ⚔️ 난이도      │  │                                 │  │
│  [●●●○○]       │  │  NPC 정보 | 목표               │  │
│                 │  │                                 │  │
│  📋 퀘스트 타입  │  │  보상 (골드/경험치/아이템)       │  │
│  [메인 ▼]       │  │                                 │  │
│                 │  │  [수락 대사] [진행 대사] [완료 대사] │
│  [🔮 생성하기]   │  └─────────────────────────────────┘  │
│                 │                                       │
│  ─────────────  │  [📥 JSON] [📥 Excel] [🔄 재생성]    │
│  📚 히스토리     │  [🗑️ 히스토리 초기화]                 │
│  (최근 5건)      │                                       │
├─────────────────┴───────────────────────────────────────┤
│  © 2025 한상범 | 서강대학교 가상융합전문대학원            │
└─────────────────────────────────────────────────────────┘
```

### 3.2 유저 플로우

```
[시작]
   │
   ▼
[장르 선택] ──▶ RPG / 액션 / 시뮬레이션 / 어드벤처 / MMORPG / 로그라이크
   │
   ▼
[테마 입력] ──▶ 자유 텍스트 (예: "중세 판타지")  ※ 미입력 시 경고 표시
   │
   ▼
[난이도 설정] ──▶ 1~5 슬라이더 (기본값: 3)
   │
   ▼
[퀘스트 타입] ──▶ 메인 / 서브 / 일일 / 반복
   │
   ▼
[생성 버튼 클릭]
   │
   ▼
[로딩 스피너] ──▶ PromptBuilder → Claude API 호출 → JSON 파싱 → QuestData 객체 생성
   │
   ├──▶ [성공] ──▶ 메인 영역에 퀘스트 표시 + 히스토리에 추가 (quest_id 자동 부여: Q001, Q002...)
   │
   └──▶ [실패] ──▶ 에러 메시지 표시 (API 오류 / JSON 파싱 실패 / 필수 필드 누락)
          │
          ▼
      [원인별 처리]
      - API 키 미설정: 초기화 화면에서 안내
      - JSON 파싱 실패: 재생성 유도
      - 필수 필드 누락: QuestData.from_dict()에서 ValueError 발생

[결과 출력 후]
   │
   ├──▶ [만족] ──▶ [JSON 다운로드] 또는 [Excel 다운로드 (전체)]
   │
   ├──▶ [불만족] ──▶ [재생성 버튼]
   │                    │
   │                    ▼
   │               genre/theme/difficulty/quest_type 유지 + 새 스토리 생성
   │
   └──▶ [초기화] ──▶ 히스토리 전체 삭제 + 현재 퀘스트 초기화
```

---

## 4. 데이터 구조

### 4.1 입력 파라미터

```json
{
  "genre": "RPG",
  "theme": "중세 판타지 왕국",
  "difficulty": 3,
  "quest_type": "메인"
}
```

- `genre`: `PromptBuilder.GENRE_TONE_GUIDE` 키 목록 중 하나 (RPG / 액션 / 시뮬레이션 / 어드벤처 / MMORPG / 로그라이크)
- `theme`: 사용자가 자유롭게 입력하는 세계관 설명 텍스트
- `difficulty`: 정수 1~5. 내부적으로 보상 골드/경험치 범위 가이드에 반영됨
- `quest_type`: 한국어 표기 그대로 입력 (메인·서브·일일·반복). `PromptBuilder`가 영문 코드(main/sub/daily/repeatable)로 변환하여 JSON 출력에 사용

### 4.2 출력 데이터 — QuestData 스키마

```json
{
  "quest_id": "Q001",
  "quest_name": "잃어버린 왕관",
  "quest_type": "main",
  "difficulty": 3,
  "genre": "RPG",
  "theme": "중세 판타지 왕국",
  "description": "왕국의 상징인 황금 왕관이 도적단에게 탈취당했다. 기사단장 로빈은 왕관 없이는 다가오는 대관식이 불가능하다며 용사에게 도움을 청한다. 도적단의 소굴은 북쪽 금지된 숲 깊은 곳에 있다.",
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
    "accept": "용사여, 왕국의 보물인 황금 왕관이 도적들에게 탈취당했소. 대관식이 사흘 앞으로 다가왔는데 이대로는 안 되오. 부탁하오.",
    "progress": "도적단 소굴은 북쪽 금지된 숲 끝에 있소. 조심하시오, 그들은 수가 많소.",
    "complete": "역시 당신이었군요! 왕국을 대신하여 진심으로 감사드리오. 이 은혜는 잊지 않겠소."
  },
  "prerequisites": [],
  "next_quest": null
}
```

**필드 설명:**
| 필드 | 타입 | 설명 |
|------|------|------|
| `quest_id` | str | 앱에서 자동 부여 (`Q001`, `Q002`...). API 응답에는 없으며 파싱 후 세팅 |
| `quest_name` | str | 퀘스트 제목 |
| `quest_type` | str | 영문 코드 (main/sub/daily/repeatable) |
| `difficulty` | int | 1~5 정수 |
| `genre` | str | 입력값 그대로 메타데이터로 추가 |
| `theme` | str | 입력값 그대로 메타데이터로 추가 |
| `description` | str | 퀘스트 배경·스토리 요약 2~3문장. 플레이어 동기 유발용 |
| `npc.name` | str | NPC 이름 |
| `npc.location` | str | NPC 위치 |
| `objective.type` | str | retrieve/kill/collect/escort/explore 중 하나 |
| `objective.target` | str | 목표 대상 (회수 아이템, 처치 몬스터 등) |
| `objective.location` | str | 목표 수행 장소 |
| `objective.count` | int or null | 수량이 있는 목표(수집·처치)일 때 사용, 없으면 null |
| `rewards.gold` | int | 보상 골드. 난이도 1→100~200G, 5→1000~2000G |
| `rewards.exp` | int | 보상 경험치. 골드의 2~3배 수준으로 생성 |
| `rewards.items` | list[str] | 보상 아이템 목록. 빈 리스트 가능 |
| `dialogue.accept` | str | 퀘스트 수락 시 NPC 대사 (최소 2문장) |
| `dialogue.progress` | str | 퀘스트 진행 중 NPC 대사 |
| `dialogue.complete` | str | 퀘스트 완료 시 NPC 대사 |
| `prerequisites` | list[str] | 선행 퀘스트 ID 목록. 현재는 빈 리스트 |
| `next_quest` | str or null | 다음 퀘스트 ID. 현재는 null |

### 4.3 Excel 출력 포맷 — 전체 21컬럼

Excel 내보내기는 `ExcelExportStrategy._flatten()` 이 중첩 구조를 평면화하여 단일 행으로 변환한다.

| 컬럼명 | 원본 필드 경로 |
|--------|--------------|
| quest_id | quest_id |
| quest_name | quest_name |
| quest_type | quest_type |
| difficulty | difficulty |
| genre | genre |
| theme | theme |
| description | description |
| npc_name | npc.name |
| npc_location | npc.location |
| objective_type | objective.type |
| objective_target | objective.target |
| objective_location | objective.location |
| objective_count | objective.count |
| reward_gold | rewards.gold |
| reward_exp | rewards.exp |
| reward_items | rewards.items (쉼표로 join) |
| dialogue_accept | dialogue.accept |
| dialogue_progress | dialogue.progress |
| dialogue_complete | dialogue.complete |
| prerequisites | prerequisites (쉼표로 join) |
| next_quest | next_quest |

---

## 5. 기술 스택

### 5.1 개발 환경

| 항목 | 선택 | 이유 |
|------|------|------|
| 언어 | Python 3.11+ | LLM API 연동 용이, 타입 힌트 및 dataclass 지원 |
| 프레임워크 | Streamlit | UI 코드 최소화, 즉시 배포 가능 |
| LLM | Claude API (claude-sonnet-4-20250514) | 한국어 품질 우수, 구조화 JSON 출력 안정적 |
| 배포 | Streamlit Cloud | 무료, GitHub 연동 자동 배포 |

### 5.2 아키텍처 설계 원칙

현재 코드베이스는 SOLID OOP 원칙을 기반으로 구성된다.

| 모듈 | 클래스 | 역할 |
|------|--------|------|
| `utils/models.py` | `QuestData`, `NPC`, `Objective`, `Rewards`, `Dialogue` | 퀘스트 도메인 모델 (dataclass). `from_dict()` / `to_dict()` 제공 |
| `utils/llm_client.py` | `LLMClient` (ABC), `AnthropicLLMClient` | LLM API 추상화. DIP 적용으로 공급자 교체 가능 |
| `utils/export_strategy.py` | `ExportStrategy` (ABC), `JsonExportStrategy`, `ExcelExportStrategy` | Strategy 패턴으로 내보내기 형식 분리. 새 형식 추가 시 기존 코드 무수정 |
| `utils/data_exporter.py` | `DataExporter` | 전략 레지스트리(`_REGISTRY`) 기반 디스패처. 형식 키로 전략을 조회하여 위임 |
| `utils/prompts.py` | `PromptBuilder` | 장르·타입 매핑을 클래스 상수(`GENRE_TONE_GUIDE` 등)로 관리. 프롬프트 생성 책임 단일화 |
| `utils/quest_generator.py` | `QuestGenerator` | `LLMClient`를 주입받아 생성 흐름 조율. `QuestData` 객체를 반환 |
| `app.py` | — | Streamlit UI 렌더링 및 세션 관리. `AnthropicLLMClient`를 생성해 `QuestGenerator`에 주입 |

### 5.3 의존성

```
streamlit>=1.30.0
anthropic>=0.18.0
pandas>=2.0.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

---

## 6. 개발 일정

### 6.1 마일스톤

| 단계 | 기간 | 목표 | 산출물 | 상태 |
|------|------|------|--------|------|
| 1. 기획 | 1일 | 기능 정의, 데이터 구조 설계 | 기획서 (본 문서) | ✅ 완료 |
| 2. MVP 개발 | 3일 | 핵심 기능 구현 | 동작하는 프로토타입 | ✅ 완료 |
| 3. UI 개선 | 2일 | 디자인 다듬기, UX 개선 | 완성된 UI | ✅ 완료 |
| 4. 내보내기 | 1일 | JSON/Excel 출력 | 내보내기 기능 | ✅ 완료 |
| 5. OOP 리팩토링 | 2일 | 클래스 상수·DIP·Strategy·도메인 모델 적용 | v1.3 코드베이스 | ✅ 완료 |
| 6. 테스트 | 1일 | 유닛 테스트, 버그 수정 | QA 완료 버전 | ⬜ 예정 |
| 7. 배포 | 1일 | Streamlit Cloud 배포 | 라이브 URL | ⬜ 예정 |

### 6.2 상세 일정

```
Week 1
├── Day 1: 기획서 완성 ✓
├── Day 2: 프로젝트 세팅, 기본 UI ✓
├── Day 3: Claude API 연동, 프롬프트 설계 ✓
├── Day 4: 퀘스트 생성 로직 완성 ✓
├── Day 5: UI 스타일링 ✓
Week 2
├── Day 6: JSON/Excel 내보내기 ✓
├── Day 7: 히스토리 기능, 재생성 ✓
├── Day 8: OOP 리팩토링 1차 (클래스 상수, SSOT) ✓
├── Day 9: OOP 리팩토링 2차 (DIP, Strategy, 도메인 모델) ✓
Week 3
├── Day 10: 유닛 테스트 작성
└── Day 11: 배포, README 최종화
```

---

## 7. 프롬프트 설계

`PromptBuilder` 클래스가 장르·타입에 따라 프롬프트를 동적으로 구성한다.
아래는 신규 생성 프롬프트의 실제 구조다.

### 7.1 신규 생성 프롬프트 (`create_quest_prompt`)

```
당신은 게임 퀘스트 디자이너입니다.

다음 조건에 맞는 퀘스트를 생성해주세요:
- 장르: {genre} ({tone_guide})
- 테마/세계관: {theme}
- 난이도: {difficulty}/5
- 퀘스트 타입: {quest_type}

출력 형식은 반드시 아래 JSON 구조를 따라야 합니다:
{
  "quest_name": "퀘스트 이름",
  "quest_type": "{quest_type_en}",
  "difficulty": {difficulty},
  "description": "퀘스트 배경과 스토리를 2~3문장으로 요약. 플레이어가 왜 이 퀘스트를 해야 하는지 동기를 제공하세요.",
  "npc": { "name": "NPC 이름", "location": "NPC 위치" },
  "objective": {
    "type": "retrieve/kill/collect/escort/explore",
    "target": "목표 대상",
    "location": "목표 위치",
    "count": null
  },
  "rewards": { "gold": 숫자, "exp": 숫자, "items": ["아이템명1"] },
  "dialogue": {
    "accept": "퀘스트 수락 시 NPC 대사",
    "progress": "퀘스트 진행 중 NPC 대사",
    "complete": "퀘스트 완료 시 NPC 대사"
  },
  "prerequisites": [],
  "next_quest": null
}

조건:
1. 난이도가 높을수록 보상을 증가시켜주세요 (난이도 1: gold 100~200, 난이도 5: gold 1000~2000)
2. 경험치는 골드의 2~3배 정도로 설정해주세요
3. 테마에 맞는 세계관 용어와 분위기를 사용해주세요
4. NPC 대사는 캐릭터성이 느껴지도록 작성해주세요 (최소 2문장 이상)
5. 퀘스트 타입에 맞게 내용을 구성해주세요 (메인/서브/일일/반복 방향 상이)
6. objective.type은 retrieve/kill/collect/escort/explore 중 하나를 선택하세요
7. JSON만 출력하고 다른 설명이나 마크다운은 하지 마세요
```

**`{tone_guide}` — 장르별 삽입값 (`PromptBuilder.GENRE_TONE_GUIDE`):**
| 장르 | tone_guide |
|------|-----------|
| RPG | 고전적인 판타지 서사, 영웅의 여정, 선악 구도 |
| 액션 | 긴박한 전투 상황, 짧고 강렬한 대사, 즉각적인 보상 |
| 시뮬레이션 | 일상적이고 현실적인 문제, 경제/관계 중심, 차분한 톤 |
| 어드벤처 | 탐험과 발견, 신비로운 분위기, 호기심을 자극하는 내용 |
| MMORPG | 대규모 세계관, 길드/파티 요소, 반복 플레이를 고려한 보상 |
| 로그라이크 | 절차적 생성 느낌, 간결한 설명, 높은 위험/높은 보상 |

**`{quest_type_en}` — 타입 한→영 변환 (`PromptBuilder.QUEST_TYPE_KO_TO_EN`):**
| 한국어 | 영문 코드 |
|--------|---------|
| 메인 | main |
| 서브 | sub |
| 일일 | daily |
| 반복 | repeatable |

### 7.2 재생성 프롬프트 (`create_regeneration_prompt`)

재생성 시에는 원본 `QuestData` 객체에서 `quest_name`, `genre`, `theme`, `difficulty`, `quest_type`을 추출하여 주입한다. 완전히 새로운 스토리를 생성하되 난이도와 타입은 고정된다.

```
당신은 게임 퀘스트 디자이너입니다.
다음 퀘스트를 완전히 새로운 스토리와 내용으로 재생성해주세요.

기존 퀘스트 정보 (난이도/타입은 유지, 나머지는 새롭게):
- 이름: {original_quest.quest_name}
- 장르/테마: {original_quest.genre} / {original_quest.theme}
- 난이도: {difficulty}/5
- 타입: {quest_type_en}
[사용자 피드백 있을 경우: 사용자 요청사항: {feedback}]

(이하 JSON 구조는 신규 생성 프롬프트와 동일)
```

### 7.3 응답 파싱 전략 (`QuestGenerator._parse_json_response`)

LLM 응답에 마크다운 코드 블록이나 부가 설명이 포함될 수 있으므로 3단계 폴백으로 처리한다:

1. **1차**: ` ```json ... ``` ` 또는 ` ``` ... ``` ` 코드 블록 내 JSON 추출
2. **2차**: 코드 블록 마커(` ``` `)만 제거 후 파싱 시도
3. **3차**: `{` ~ `}` 범위를 찾아 JSON 객체 추출

파싱 성공 후 `QuestData.from_dict()` 로 도메인 객체 변환. 필수 필드 누락 시 `ValueError` 발생.

---

## 8. 리스크 및 대응

| 리스크 | 대응 방안 | 현재 구현 상태 |
|--------|----------|--------------|
| API 키 미설정 | 초기화 시 검증, 에러 메시지와 설정 가이드 표시 | ✅ 구현됨 |
| JSON 파싱 실패 | 3단계 폴백 파싱, 실패 시 에러 메시지 + 재생성 유도 | ✅ 구현됨 |
| 필수 필드 누락 | `QuestData.from_dict()` 에서 `ValueError` 발생, UI에서 에러 표시 | ✅ 구현됨 |
| 부적절한 콘텐츠 | 프롬프트에 장르·세계관 톤 가이드 명시, 퀘스트 디자이너 역할 부여 | ✅ 구현됨 |
| LLM 공급자 교체 필요 | `LLMClient` ABC로 추상화. `AnthropicLLMClient` 교체 시 `QuestGenerator` 무수정 | ✅ 구현됨 |
| API 비용 초과 | 일일 생성 횟수 제한, 캐싱 | ⬜ 미구현 (v2.0 예정) |
| Streamlit Cloud 트래픽 한계 | 트래픽 증가 시 유료 플랜 검토 | ⬜ 모니터링 필요 |

---

## 9. 성공 지표

| 지표 | 목표 |
|------|------|
| 퀘스트 생성 성공률 | 95% 이상 |
| 평균 생성 시간 | 10초 이내 |
| JSON 파싱 성공률 | 99% 이상 (3단계 폴백 적용) |
| OOP 품질 점수 | 60점 이상 (현재: 65점) |
| 포트폴리오 반영 | 면접에서 데모 시연 가능 |

---

## 10. 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Anthropic Claude API 문서](https://docs.anthropic.com/)
- [게임 퀘스트 디자인 패턴](https://www.gamedeveloper.com/)

---

**문서 끝**
