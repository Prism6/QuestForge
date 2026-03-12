"""
내보내기 전략 모듈

Strategy 패턴으로 JSON·Excel 내보내기를 구현합니다.
새 형식 추가 시 ExportStrategy 서브클래스를 이 모듈에 추가하고
DataExporter._REGISTRY 에 등록하기만 하면 됩니다 (OCP).
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING, List

import pandas as pd
from openpyxl.utils import get_column_letter

if TYPE_CHECKING:
    from .models import QuestData

logger = logging.getLogger(__name__)


class ExportStrategy(ABC):
    """
    내보내기 전략 추상 기반 클래스.

    각 구체 전략은 mime_type, file_extension, export() 를 구현해야 합니다.
    """

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """HTTP Content-Type 에 사용할 MIME 타입."""

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """파일 확장자 (점 없이, 예: 'json', 'xlsx')."""

    @abstractmethod
    def export(self, quests: List["QuestData"]) -> bytes:
        """
        퀘스트 목록을 해당 형식의 바이트로 변환합니다.

        Args:
            quests: 내보낼 QuestData 리스트

        Returns:
            bytes: 직렬화된 파일 데이터
        """

    def generate_filename(self, prefix: str = "quest") -> str:
        """타임스탬프가 포함된 파일명을 생성합니다."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{self.file_extension}"


class JsonExportStrategy(ExportStrategy):
    """JSON 형식 내보내기 전략."""

    @property
    def mime_type(self) -> str:
        return "application/json"

    @property
    def file_extension(self) -> str:
        return "json"

    def export(self, quests: List["QuestData"]) -> bytes:
        if len(quests) == 1:
            payload = quests[0].to_dict()
        else:
            payload = [q.to_dict() for q in quests]
        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


class ExcelExportStrategy(ExportStrategy):
    """Excel 형식 내보내기 전략."""

    COLUMN_ORDER: List[str] = [
        "quest_id", "quest_name", "quest_type", "difficulty", "genre", "theme",
        "description", "npc_name", "npc_location", "objective_type", "objective_target",
        "objective_location", "objective_count", "reward_gold", "reward_exp", "reward_items",
        "dialogue_accept", "dialogue_progress", "dialogue_complete", "prerequisites", "next_quest",
    ]
    MAX_COLUMN_WIDTH: int = 50
    SHEET_NAME: str = "Quests"

    @property
    def mime_type(self) -> str:
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    @property
    def file_extension(self) -> str:
        return "xlsx"

    def export(self, quests: List["QuestData"]) -> bytes:
        flattened = [self._flatten(q) for q in quests]
        df = pd.DataFrame(flattened)
        existing_cols = [c for c in self.COLUMN_ORDER if c in df.columns]
        df = df[existing_cols]

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=self.SHEET_NAME)
            ws = writer.sheets[self.SHEET_NAME]
            for idx, col in enumerate(df.columns):
                width = min(
                    max(df[col].astype(str).apply(len).max(), len(col)),
                    self.MAX_COLUMN_WIDTH,
                )
                ws.column_dimensions[get_column_letter(idx + 1)].width = width + 2

        return output.getvalue()

    @staticmethod
    def _flatten(quest: "QuestData") -> dict:
        """QuestData를 Excel 행(평면 dict)으로 변환합니다."""
        return {
            "quest_id": quest.quest_id,
            "quest_name": quest.quest_name,
            "quest_type": quest.quest_type,
            "difficulty": quest.difficulty,
            "genre": quest.genre,
            "theme": quest.theme,
            "description": quest.description,
            "npc_name": quest.npc.name,
            "npc_location": quest.npc.location,
            "objective_type": quest.objective.type,
            "objective_target": quest.objective.target,
            "objective_location": quest.objective.location,
            "objective_count": quest.objective.count,
            "reward_gold": quest.rewards.gold,
            "reward_exp": quest.rewards.exp,
            "reward_items": ", ".join(quest.rewards.items),
            "dialogue_accept": quest.dialogue.accept,
            "dialogue_progress": quest.dialogue.progress,
            "dialogue_complete": quest.dialogue.complete,
            "prerequisites": ", ".join(quest.prerequisites),
            "next_quest": quest.next_quest or "",
        }
