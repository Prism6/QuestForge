"""
LLM 클라이언트 추상 인터페이스 모듈

LLMClient ABC 만 정의합니다. 구체적인 공급자 구현체는 별도 모듈에 위치합니다.
  - Anthropic: utils/anthropic_client.py

이 파일은 anthropic·openai 등 특정 라이브러리를 임포트하지 않으므로
테스트 환경에서 Mock LLMClient 를 사용할 때 외부 의존성이 필요 없습니다 (DIP 완전 분리).
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """
    LLM API 호출 추상 인터페이스.

    QuestGenerator 는 이 인터페이스에만 의존하며,
    구체적인 API 구현(AnthropicLLMClient 등)은 런타임에 주입됩니다.
    """

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """
        프롬프트를 전달하고 LLM 응답 텍스트를 반환합니다.

        Args:
            prompt: 사용자 프롬프트

        Returns:
            str: LLM 응답 텍스트
        """
