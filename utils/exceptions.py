"""
QuestForge 커스텀 예외 계층

범용 Exception 대신 의미 있는 예외 타입을 사용하여
호출부에서 예외 종류에 따라 구체적인 대응이 가능합니다 (LSP 보장).
"""


class QuestForgeError(Exception):
    """QuestForge 최상위 예외 클래스. 모든 도메인 예외의 기반."""


class QuestValidationError(QuestForgeError):
    """퀘스트 데이터 유효성 검증 실패 (필수 필드 누락, 값 범위 오류 등)."""


class QuestGenerationError(QuestForgeError):
    """퀘스트 생성 실패 (API 호출 오류, 네트워크 오류 등)."""


class QuestParseError(QuestForgeError):
    """퀘스트 JSON 파싱 실패 (응답 형식 불일치 등)."""
