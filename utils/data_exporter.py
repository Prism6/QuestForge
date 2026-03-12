"""
데이터 내보내기 모듈

ExportStrategy 레지스트리를 관리하고 다운로드 데이터를 생성합니다.
새 형식 지원 추가 시 _REGISTRY 에 항목만 추가하면 됩니다 (OCP).
"""

from typing import Dict, List, Tuple

from .export_strategy import ExcelExportStrategy, ExportStrategy, JsonExportStrategy
from .models import QuestData


class DataExporter:
    """
    ExportStrategy 레지스트리 및 다운로드 데이터 생성기.

    구체적인 직렬화 로직은 각 ExportStrategy 구현체에 위임합니다 (SRP).
    """

    _REGISTRY: Dict[str, ExportStrategy] = {
        "json": JsonExportStrategy(),
        "excel": ExcelExportStrategy(),
    }

    @classmethod
    def create_download_data(
        cls, quests: List[QuestData], format_type: str
    ) -> Tuple[bytes, str, str]:
        """
        다운로드용 바이트 데이터, 파일명, MIME 타입을 생성합니다.

        Args:
            quests: 내보낼 QuestData 리스트
            format_type: 파일 형식 키 ('json' 또는 'excel')

        Returns:
            Tuple[bytes, str, str]: (데이터, 파일명, MIME 타입)

        Raises:
            ValueError: 지원하지 않는 형식일 때
        """
        strategy = cls._REGISTRY.get(format_type)
        if strategy is None:
            supported = ", ".join(cls._REGISTRY.keys())
            raise ValueError(
                f"지원하지 않는 형식: '{format_type}'. 지원 형식: {supported}"
            )
        return strategy.export(quests), strategy.generate_filename(), strategy.mime_type
