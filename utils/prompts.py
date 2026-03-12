"""
프롬프트 템플릿 모듈

Claude API에 전달할 프롬프트를 생성합니다.
"""

from typing import Dict


class PromptBuilder:
    """
    퀘스트 생성 프롬프트를 빌드하는 클래스.

    장르·타입 매핑을 클래스 상수로 관리하여 확장 시
    이 클래스만 수정하면 앱 전체에 반영됩니다.
    """

    # 장르별 톤 가이드 (OCP: 장르 추가 시 이 상수만 수정)
    GENRE_TONE_GUIDE: Dict[str, str] = {
        "RPG": "고전적인 판타지 서사, 영웅의 여정, 선악 구도",
        "액션": "긴박한 전투 상황, 짧고 강렬한 대사, 즉각적인 보상",
        "시뮬레이션": "일상적이고 현실적인 문제, 경제/관계 중심, 차분한 톤",
        "어드벤처": "탐험과 발견, 신비로운 분위기, 호기심을 자극하는 내용",
        "MMORPG": "대규모 세계관, 길드/파티 요소, 반복 플레이를 고려한 보상",
        "로그라이크": "절차적 생성 느낌, 간결한 설명, 높은 위험/높은 보상",
    }

    # 한국어 → 영어 타입 매핑
    QUEST_TYPE_KO_TO_EN: Dict[str, str] = {
        "메인": "main",
        "서브": "sub",
        "일일": "daily",
        "반복": "repeatable",
    }

    # 영어 → 한국어 타입 매핑 (UI 표시용, KO_TO_EN의 역방향)
    QUEST_TYPE_EN_TO_KO: Dict[str, str] = {
        en: ko for ko, en in QUEST_TYPE_KO_TO_EN.items()
    }

    @classmethod
    def create_quest_prompt(
        cls, genre: str, theme: str, difficulty: int, quest_type: str
    ) -> str:
        """
        퀘스트 생성을 위한 프롬프트를 생성합니다.

        Args:
            genre: 게임 장르 (GENRE_TONE_GUIDE 키 중 하나)
            theme: 테마/세계관 (예: 중세 판타지 왕국)
            difficulty: 난이도 (1~5)
            quest_type: 퀘스트 타입 (QUEST_TYPE_KO_TO_EN 키 중 하나)

        Returns:
            str: 생성된 프롬프트
        """
        quest_type_en = cls.QUEST_TYPE_KO_TO_EN.get(quest_type, quest_type.lower())
        tone_guide = cls.GENRE_TONE_GUIDE.get(genre, "장르에 맞는 분위기")

        return f"""당신은 게임 퀘스트 디자이너입니다.

다음 조건에 맞는 퀘스트를 생성해주세요:
- 장르: {genre} ({tone_guide})
- 테마/세계관: {theme}
- 난이도: {difficulty}/5
- 퀘스트 타입: {quest_type}

출력 형식은 반드시 아래 JSON 구조를 따라야 합니다:
{{
  "quest_name": "퀘스트 이름",
  "quest_type": "{quest_type_en}",
  "difficulty": {difficulty},
  "description": "퀘스트 배경과 스토리를 2~3문장으로 요약. 플레이어가 왜 이 퀘스트를 해야 하는지 동기를 제공하세요.",
  "npc": {{
    "name": "NPC 이름",
    "location": "NPC 위치"
  }},
  "objective": {{
    "type": "retrieve/kill/collect/escort/explore",
    "target": "목표 대상",
    "location": "목표 위치",
    "count": null
  }},
  "rewards": {{
    "gold": 숫자,
    "exp": 숫자,
    "items": ["아이템명1", "아이템명2"]
  }},
  "dialogue": {{
    "accept": "퀘스트 수락 시 NPC 대사",
    "progress": "퀘스트 진행 중 NPC 대사",
    "complete": "퀘스트 완료 시 NPC 대사"
  }},
  "prerequisites": [],
  "next_quest": null
}}

조건:
1. 난이도가 높을수록 보상을 증가시켜주세요 (난이도 1: gold 100~200, 난이도 5: gold 1000~2000)
2. 경험치는 골드의 2~3배 정도로 설정해주세요
3. 테마에 맞는 세계관 용어와 분위기를 사용해주세요
4. NPC 대사는 캐릭터성이 느껴지도록 작성해주세요 (최소 2문장 이상)
5. 퀘스트 타입에 맞게 내용을 구성해주세요:
   - 메인: 스토리 중심, 중요한 NPC와 상호작용, 세계관에 영향을 주는 사건
   - 서브: 지역 주민의 일상적인 문제 해결, 소소하지만 개성 있는 스토리
   - 일일: 간단하고 반복 가능한 작업, 명확한 목표와 보상
   - 반복: 수집/처치 중심의 단순 과제, 효율적인 설명
6. objective.type은 retrieve(회수), kill(처치), collect(수집), escort(호위), explore(탐험) 중 하나를 선택하세요
7. JSON만 출력하고 다른 설명이나 마크다운은 하지 마세요
"""

    @classmethod
    def create_regeneration_prompt(
        cls, original_quest: Dict, feedback: str = ""
    ) -> str:
        """
        기존 퀘스트를 기반으로 재생성 프롬프트를 생성합니다.

        Args:
            original_quest: 기존 퀘스트 데이터
            feedback: 사용자 피드백 (선택사항)

        Returns:
            str: 재생성 프롬프트
        """
        difficulty = original_quest.get("difficulty", 3)
        quest_type_en = original_quest.get("quest_type", "main")

        feedback_section = f"\n사용자 요청사항: {feedback}\n" if feedback else ""

        return f"""당신은 게임 퀘스트 디자이너입니다.
다음 퀘스트를 완전히 새로운 스토리와 내용으로 재생성해주세요.

기존 퀘스트 정보 (난이도/타입은 유지, 나머지는 새롭게):
- 이름: {original_quest.get('quest_name', '')}
- 장르/테마: {original_quest.get('genre', '')} / {original_quest.get('theme', '')}
- 난이도: {difficulty}/5
- 타입: {quest_type_en}
{feedback_section}
반드시 아래 JSON 구조로 출력하세요:
{{
  "quest_name": "새로운 퀘스트 이름",
  "quest_type": "{quest_type_en}",
  "difficulty": {difficulty},
  "description": "새로운 퀘스트 배경과 스토리를 2~3문장으로 요약",
  "npc": {{
    "name": "NPC 이름",
    "location": "NPC 위치"
  }},
  "objective": {{
    "type": "retrieve/kill/collect/escort/explore",
    "target": "목표 대상",
    "location": "목표 위치",
    "count": null
  }},
  "rewards": {{
    "gold": 숫자,
    "exp": 숫자,
    "items": ["아이템명1", "아이템명2"]
  }},
  "dialogue": {{
    "accept": "퀘스트 수락 시 NPC 대사",
    "progress": "퀘스트 진행 중 NPC 대사",
    "complete": "퀘스트 완료 시 NPC 대사"
  }},
  "prerequisites": [],
  "next_quest": null
}}

JSON만 출력하고 다른 설명은 하지 마세요.
"""
