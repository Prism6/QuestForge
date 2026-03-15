"""utils/export_strategy.py 유닛 테스트"""

import json

import pytest

from utils.export_strategy import ExcelExportStrategy, JsonExportStrategy
from utils.models import QuestData

# --- 공통 픽스처 ---

QUEST_DATA = {
    "quest_name": "마을 경비",
    "quest_type": "sub",
    "difficulty": 1,
    "description": "마을 경비를 서 달라.",
    "npc": {"name": "촌장 박씨", "location": "마을 입구"},
    "objective": {
        "type": "kill",
        "target": "슬라임",
        "location": "마을 외곽",
        "count": 5,
    },
    "rewards": {"gold": 100, "exp": 200, "items": ["회복 포션"]},
    "dialogue": {
        "accept": "부탁하오.",
        "progress": "아직 처치 중이오?",
        "complete": "고맙소!",
    },
    "prerequisites": [],
    "next_quest": None,
}


@pytest.fixture
def single_quest() -> QuestData:
    return QuestData.from_dict(QUEST_DATA)


@pytest.fixture
def multiple_quests() -> list:
    q1 = QuestData.from_dict(QUEST_DATA)
    q2 = QuestData.from_dict({**QUEST_DATA, "quest_name": "두 번째 퀘스트", "difficulty": 2})
    return [q1, q2]


# --- JsonExportStrategy 테스트 ---

class TestJsonExportStrategy:
    def setup_method(self):
        self.strategy = JsonExportStrategy()

    def test_single_quest_exports_as_dict(self, single_quest):
        result = self.strategy.export([single_quest])
        data = json.loads(result.decode("utf-8"))
        assert isinstance(data, dict)
        assert data["quest_name"] == "마을 경비"

    def test_multiple_quests_exports_as_list(self, multiple_quests):
        result = self.strategy.export(multiple_quests)
        data = json.loads(result.decode("utf-8"))
        assert isinstance(data, list)
        assert len(data) == 2

    def test_quest_type_serialized_as_string(self, single_quest):
        result = self.strategy.export([single_quest])
        data = json.loads(result.decode("utf-8"))
        assert data["quest_type"] == "sub"

    def test_mime_type(self):
        assert self.strategy.mime_type == "application/json"

    def test_file_extension(self):
        assert self.strategy.file_extension == "json"

    def test_generate_filename_has_correct_extension(self):
        filename = self.strategy.generate_filename()
        assert filename.endswith(".json")


# --- ExcelExportStrategy 테스트 ---

class TestExcelExportStrategy:
    def setup_method(self):
        self.strategy = ExcelExportStrategy()

    def test_export_returns_bytes(self, single_quest):
        result = self.strategy.export([single_quest])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_export_multiple_returns_bytes(self, multiple_quests):
        result = self.strategy.export(multiple_quests)
        assert isinstance(result, bytes)

    def test_mime_type(self):
        assert "spreadsheetml" in self.strategy.mime_type

    def test_file_extension(self):
        assert self.strategy.file_extension == "xlsx"

    def test_generate_filename_has_correct_extension(self):
        filename = self.strategy.generate_filename()
        assert filename.endswith(".xlsx")
