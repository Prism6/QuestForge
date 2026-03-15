"""utils/quest_generator.py 유닛 테스트 (Mock LLMClient 사용)"""

import json

import pytest

from utils.exceptions import QuestGenerationError, QuestParseError, QuestValidationError
from utils.llm_client import LLMClient
from utils.models import QuestData, QuestType
from utils.quest_generator import QuestGenerator

# --- Mock LLMClient ---

VALID_QUEST_JSON = {
    "quest_name": "어둠의 결정 수집",
    "quest_type": "daily",
    "difficulty": 2,
    "description": "마법사의 연구를 위해 어둠의 결정이 필요하다.",
    "npc": {"name": "마법사 엘라", "location": "마법탑 1층"},
    "objective": {
        "type": "collect",
        "target": "어둠의 결정",
        "location": "어두운 숲",
        "count": 10,
    },
    "rewards": {"gold": 200, "exp": 400, "items": []},
    "dialogue": {
        "accept": "부탁하네.",
        "progress": "아직 모으는 중인가?",
        "complete": "잘 했네!",
    },
    "prerequisites": [],
    "next_quest": None,
}


class MockLLMClient(LLMClient):
    """테스트용 Mock LLMClient. 지정한 응답을 그대로 반환합니다."""

    def __init__(self, response: str):
        self._response = response

    def complete(self, prompt: str) -> str:
        return self._response


class ErrorLLMClient(LLMClient):
    """테스트용 에러 발생 LLMClient."""

    def complete(self, prompt: str) -> str:
        raise RuntimeError("API 연결 실패")


# --- QuestGenerator 테스트 ---

class TestQuestGeneratorGenerateQuest:
    def _make_generator(self, response: str) -> QuestGenerator:
        return QuestGenerator(llm_client=MockLLMClient(response))

    def test_generate_quest_returns_quest_data(self):
        generator = self._make_generator(json.dumps(VALID_QUEST_JSON))
        quest = generator.generate_quest(
            genre="RPG", theme="중세 판타지", difficulty=2, quest_type="일일"
        )
        assert isinstance(quest, QuestData)
        assert quest.quest_name == "어둠의 결정 수집"
        assert quest.quest_type == QuestType.DAILY

    def test_generate_quest_attaches_genre_and_theme(self):
        generator = self._make_generator(json.dumps(VALID_QUEST_JSON))
        quest = generator.generate_quest(
            genre="RPG", theme="중세 판타지", difficulty=2, quest_type="일일"
        )
        assert quest.genre == "RPG"
        assert quest.theme == "중세 판타지"

    def test_generate_quest_with_code_block_response(self):
        wrapped = f"```json\n{json.dumps(VALID_QUEST_JSON)}\n```"
        generator = self._make_generator(wrapped)
        quest = generator.generate_quest(
            genre="RPG", theme="중세 판타지", difficulty=2, quest_type="일일"
        )
        assert quest.quest_name == "어둠의 결정 수집"

    def test_invalid_json_raises_parse_error(self):
        generator = self._make_generator("이것은 JSON 이 아닙니다")
        with pytest.raises(QuestParseError):
            generator.generate_quest(
                genre="RPG", theme="테마", difficulty=1, quest_type="서브"
            )

    def test_api_error_raises_generation_error(self):
        generator = QuestGenerator(llm_client=ErrorLLMClient())
        with pytest.raises(QuestGenerationError):
            generator.generate_quest(
                genre="RPG", theme="테마", difficulty=1, quest_type="서브"
            )

    def test_missing_field_in_response_raises_validation_error(self):
        incomplete = {k: v for k, v in VALID_QUEST_JSON.items() if k != "quest_name"}
        generator = self._make_generator(json.dumps(incomplete))
        with pytest.raises(QuestValidationError):
            generator.generate_quest(
                genre="RPG", theme="테마", difficulty=2, quest_type="일일"
            )


class TestQuestGeneratorRegenerateQuest:
    def test_regenerate_preserves_genre_and_theme(self):
        original = QuestData.from_dict(VALID_QUEST_JSON)
        original.genre = "액션"
        original.theme = "사이버펑크"

        new_data = {**VALID_QUEST_JSON, "quest_name": "새 퀘스트"}
        generator = QuestGenerator(llm_client=MockLLMClient(json.dumps(new_data)))
        regenerated = generator.regenerate_quest(original)

        assert regenerated.genre == "액션"
        assert regenerated.theme == "사이버펑크"
