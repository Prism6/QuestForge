"""
LLM 클라이언트 모듈

LLM API 호출을 LLMClient 추상 인터페이스로 감싸
구체적인 공급자(Anthropic, OpenAI 등)와 상위 모듈을 분리합니다 (DIP).

새 공급자 추가 시 LLMClient를 상속한 클래스만 구현하면 됩니다 (OCP).
"""

import logging
from abc import ABC, abstractmethod

from anthropic import Anthropic

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


class AnthropicLLMClient(LLMClient):
    """
    Anthropic Claude API 를 사용하는 LLMClient 구현체.

    클래스 상수로 기본값을 정의하여 인스턴스 생성 시 선택적으로 오버라이드할 수 있습니다.
    """

    MODEL: str = "claude-sonnet-4-20250514"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 1.0

    def __init__(
        self,
        api_key: str,
        model: str = MODEL,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ):
        """
        AnthropicLLMClient 초기화.

        Args:
            api_key: Anthropic API 키
            model: 사용할 모델 ID
            max_tokens: 최대 응답 토큰 수
            temperature: 샘플링 온도
        """
        self._client = Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature
        logger.info("AnthropicLLMClient 초기화 완료 (모델: %s)", self._model)

    def complete(self, prompt: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
