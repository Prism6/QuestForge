"""
Anthropic Claude API LLMClient 구현체 모듈

AnthropicLLMClient를 llm_client.py 인터페이스 파일에서 분리합니다.
덕분에 llm_client.py(인터페이스)는 anthropic 라이브러리에 의존하지 않으므로
Mock LLMClient 를 사용하는 테스트 시 anthropic 패키지 없이도 인터페이스만 임포트할 수 있습니다.
"""

import logging

from anthropic import Anthropic

from .llm_client import LLMClient

logger = logging.getLogger(__name__)


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
