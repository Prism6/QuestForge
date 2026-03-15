"""utils/models.py 유닛 테스트"""

import pytest

from utils.exceptions import QuestValidationError
from utils.models import QuestData, QuestType

# --- 테스트 픽스처 ---

VALID_DATA = {
    "quest_name": "불꽃 검 회수",
    "quest_type": "main",
    "difficulty": 3,
    "description": "왕국의 전설적인 검이 도적단에게 탈취당했다.",
    "npc": {"name": "대장장이 이반", "location": "왕도 대장간"},
    "objective": {
        "type": "retrieve",
        "target": "불꽃 검",
        "location": "도적 소굴",
        "count": None,
    },
    "rewards": {"gold": 500, "exp": 1000, "items": ["강화석"]},
    "dialogue": {
        "accept": "꼭 되찾아 주게나.",
        "progress": "아직 찾지 못했나?",
        "complete": "고맙네, 영웅이여.",
    },
    "prerequisites": [],
    "next_quest": None,
}


# --- QuestData.from_dict 테스트 ---

class TestQuestDataFromDict:
    def test_valid_data_returns_quest(self):
        quest = QuestData.from_dict(VALID_DATA)
        assert quest.quest_name == "불꽃 검 회수"
        assert quest.quest_type == QuestType.MAIN
        assert quest.difficulty == 3
        assert quest.npc.name == "대장장이 이반"
        assert quest.rewards.gold == 500

    def test_quest_type_is_enum(self):
        quest = QuestData.from_dict(VALID_DATA)
        assert isinstance(quest.quest_type, QuestType)
        assert quest.quest_type == QuestType.MAIN

    def test_all_quest_types_parsed(self):
        for qt in QuestType:
            data = {**VALID_DATA, "quest_type": qt.value}
            quest = QuestData.from_dict(data)
            assert quest.quest_type == qt

    def test_missing_required_field_raises_validation_error(self):
        data = {k: v for k, v in VALID_DATA.items() if k != "quest_name"}
        with pytest.raises(QuestValidationError):
            QuestData.from_dict(data)

    def test_missing_nested_field_raises_validation_error(self):
        data = {**VALID_DATA, "npc": {"name": "이반"}}  # location 누락
        with pytest.raises(QuestValidationError):
            QuestData.from_dict(data)

    def test_invalid_quest_type_raises_validation_error(self):
        data = {**VALID_DATA, "quest_type": "invalid_type"}
        with pytest.raises(QuestValidationError):
            QuestData.from_dict(data)

    def test_difficulty_below_range_raises_validation_error(self):
        data = {**VALID_DATA, "difficulty": 0}
        with pytest.raises(QuestValidationError):
            QuestData.from_dict(data)

    def test_difficulty_above_range_raises_validation_error(self):
        data = {**VALID_DATA, "difficulty": 6}
        with pytest.raises(QuestValidationError):
            QuestData.from_dict(data)

    def test_difficulty_boundary_values_valid(self):
        for d in [1, 5]:
            data = {**VALID_DATA, "difficulty": d}
            quest = QuestData.from_dict(data)
            assert quest.difficulty == d

    def test_optional_fields_have_defaults(self):
        quest = QuestData.from_dict(VALID_DATA)
        assert quest.description == "왕국의 전설적인 검이 도적단에게 탈취당했다."
        assert quest.quest_id == ""
        assert quest.genre == ""
        assert quest.prerequisites == []
        assert quest.next_quest is None


# --- QuestData.to_dict 테스트 ---

class TestQuestDataToDict:
    def test_round_trip(self):
        quest = QuestData.from_dict(VALID_DATA)
        result = quest.to_dict()
        assert result["quest_name"] == VALID_DATA["quest_name"]
        assert result["quest_type"] == "main"  # QuestType → str 직렬화
        assert result["difficulty"] == 3
        assert result["npc"]["name"] == "대장장이 이반"

    def test_quest_type_serialized_as_string(self):
        quest = QuestData.from_dict(VALID_DATA)
        result = quest.to_dict()
        assert isinstance(result["quest_type"], str)
        assert result["quest_type"] == "main"
