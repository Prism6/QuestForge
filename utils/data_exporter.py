"""
데이터 내보내기 모듈

퀘스트 데이터를 JSON 및 Excel 형식으로 내보냅니다.
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter


class DataExporter:
    """
    퀘스트 데이터 내보내기 클래스
    """

    # Excel 컬럼 순서 (OCP: 컬럼 추가 시 이 상수만 수정)
    COLUMN_ORDER: List[str] = [
        "quest_id",
        "quest_name",
        "quest_type",
        "difficulty",
        "genre",
        "theme",
        "description",
        "npc_name",
        "npc_location",
        "objective_type",
        "objective_target",
        "objective_location",
        "objective_count",
        "reward_gold",
        "reward_exp",
        "reward_items",
        "dialogue_accept",
        "dialogue_progress",
        "dialogue_complete",
        "prerequisites",
        "next_quest",
    ]

    # Excel 컬럼 최대 너비
    MAX_COLUMN_WIDTH: int = 50

    # Excel 시트 이름
    SHEET_NAME: str = "Quests"

    # 지원 형식별 MIME 타입
    MIME_TYPES: Dict[str, str] = {
        "json": "application/json",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    @staticmethod
    def to_json(quest_data: Dict) -> str:
        """
        퀘스트 데이터를 JSON 문자열로 변환합니다.

        Args:
            quest_data: 퀘스트 데이터

        Returns:
            str: JSON 문자열
        """
        return json.dumps(quest_data, ensure_ascii=False, indent=2)

    @classmethod
    def to_excel(cls, quest_data_list: List[Dict]) -> BytesIO:
        """
        퀘스트 데이터 목록을 Excel 파일로 변환합니다.

        Args:
            quest_data_list: 퀘스트 데이터 리스트

        Returns:
            BytesIO: Excel 파일 바이트 스트림
        """
        flattened_data = [cls._flatten_quest(quest) for quest in quest_data_list]

        df = pd.DataFrame(flattened_data)

        existing_columns = [col for col in cls.COLUMN_ORDER if col in df.columns]
        df = df[existing_columns]

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=cls.SHEET_NAME)

            worksheet = writer.sheets[cls.SHEET_NAME]

            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                max_length = min(max_length, cls.MAX_COLUMN_WIDTH)
                col_letter = get_column_letter(idx + 1)
                worksheet.column_dimensions[col_letter].width = max_length + 2

        output.seek(0)
        return output

    @staticmethod
    def _flatten_quest(quest: Dict) -> Dict:
        """
        중첩된 퀘스트 딕셔너리를 Excel용 평면 구조로 변환합니다.

        Args:
            quest: 중첩 퀘스트 데이터

        Returns:
            Dict: 평면화된 퀘스트 데이터
        """
        return {
            "quest_id": quest.get("quest_id", ""),
            "quest_name": quest.get("quest_name", ""),
            "quest_type": quest.get("quest_type", ""),
            "difficulty": quest.get("difficulty", 0),
            "genre": quest.get("genre", ""),
            "theme": quest.get("theme", ""),
            "description": quest.get("description", ""),
            "npc_name": quest.get("npc", {}).get("name", ""),
            "npc_location": quest.get("npc", {}).get("location", ""),
            "objective_type": quest.get("objective", {}).get("type", ""),
            "objective_target": quest.get("objective", {}).get("target", ""),
            "objective_location": quest.get("objective", {}).get("location", ""),
            "objective_count": quest.get("objective", {}).get("count", ""),
            "reward_gold": quest.get("rewards", {}).get("gold", 0),
            "reward_exp": quest.get("rewards", {}).get("exp", 0),
            "reward_items": ", ".join(quest.get("rewards", {}).get("items", [])),
            "dialogue_accept": quest.get("dialogue", {}).get("accept", ""),
            "dialogue_progress": quest.get("dialogue", {}).get("progress", ""),
            "dialogue_complete": quest.get("dialogue", {}).get("complete", ""),
            "prerequisites": ", ".join(quest.get("prerequisites", [])),
            "next_quest": quest.get("next_quest", ""),
        }

    @staticmethod
    def generate_filename(prefix: str, extension: str) -> str:
        """
        타임스탬프가 포함된 파일명을 생성합니다.

        Args:
            prefix: 파일명 접두사
            extension: 파일 확장자 (예: 'json', 'xlsx')

        Returns:
            str: 생성된 파일명
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"

    @classmethod
    def create_download_data(
        cls, quest_data_list: List[Dict], format_type: str
    ) -> Tuple[bytes, str, str]:
        """
        다운로드용 데이터와 파일명을 생성합니다.

        Args:
            quest_data_list: 퀘스트 데이터 리스트
            format_type: 파일 형식 ('json' 또는 'excel')

        Returns:
            tuple: (데이터, 파일명, MIME 타입)

        Raises:
            ValueError: 지원하지 않는 형식일 때
        """
        if format_type not in cls.MIME_TYPES:
            raise ValueError(f"지원하지 않는 형식: {format_type}")

        mime_type = cls.MIME_TYPES[format_type]

        if format_type == "json":
            if len(quest_data_list) == 1:
                raw = cls.to_json(quest_data_list[0])
            else:
                raw = json.dumps(quest_data_list, ensure_ascii=False, indent=2)
            filename = cls.generate_filename("quest", "json")
            return raw.encode("utf-8"), filename, mime_type

        # format_type == "excel"
        data = cls.to_excel(quest_data_list)
        filename = cls.generate_filename("quest", "xlsx")
        return data.getvalue(), filename, mime_type
