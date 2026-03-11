"""
데이터 내보내기 모듈

퀘스트 데이터를 JSON 및 Excel 형식으로 내보냅니다.
"""

import json
from typing import Dict, List
from datetime import datetime
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter


class DataExporter:
    """
    퀘스트 데이터 내보내기 클래스
    """

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

    @staticmethod
    def to_excel(quest_data_list: List[Dict]) -> BytesIO:
        """
        퀘스트 데이터 목록을 Excel 파일로 변환합니다.

        Args:
            quest_data_list: 퀘스트 데이터 리스트

        Returns:
            BytesIO: Excel 파일 바이트 스트림
        """
        # 엑셀용 평면 데이터 구조로 변환
        flattened_data = []

        for quest in quest_data_list:
            flat_quest = {
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
                "next_quest": quest.get("next_quest", "")
            }
            flattened_data.append(flat_quest)

        # DataFrame 생성
        df = pd.DataFrame(flattened_data)

        # 컬럼 순서 정의
        column_order = [
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
            "next_quest"
        ]

        # 컬럼이 존재하는 경우에만 재정렬
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]

        # Excel 파일로 변환
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Quests')

            # 워크시트 가져오기
            worksheet = writer.sheets['Quests']

            # 컬럼 너비 자동 조정
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                # 최대 너비 제한
                max_length = min(max_length, 50)
                col_letter = get_column_letter(idx + 1)
                worksheet.column_dimensions[col_letter].width = max_length + 2

        output.seek(0)
        return output

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

    @staticmethod
    def create_download_data(quest_data_list: List[Dict], format_type: str) -> tuple:
        """
        다운로드용 데이터와 파일명을 생성합니다.

        Args:
            quest_data_list: 퀘스트 데이터 리스트
            format_type: 파일 형식 ('json' 또는 'excel')

        Returns:
            tuple: (데이터, 파일명, MIME 타입)
        """
        if format_type == "json":
            # 단일 퀘스트인 경우
            if len(quest_data_list) == 1:
                data = DataExporter.to_json(quest_data_list[0])
            else:
                # 여러 퀘스트인 경우 리스트로
                data = json.dumps(quest_data_list, ensure_ascii=False, indent=2)

            filename = DataExporter.generate_filename("quest", "json")
            mime_type = "application/json"
            return data.encode('utf-8'), filename, mime_type

        elif format_type == "excel":
            data = DataExporter.to_excel(quest_data_list)
            filename = DataExporter.generate_filename("quest", "xlsx")
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return data.getvalue(), filename, mime_type

        else:
            raise ValueError(f"지원하지 않는 형식: {format_type}")
