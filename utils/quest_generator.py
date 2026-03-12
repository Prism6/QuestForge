"""
퀘스트 생성기 모듈

LLMClient 인터페이스를 주입받아 퀘스트를 생성합니다.
구체적인 LLM 공급자(Anthropic 등)와 완전히 분리됩니다 (DIP).
"""

import json
import logging
import re
from typing import Dict

from dotenv import load_dotenv

from .llm_client import LLMClient
from .models import QuestData
from .prompts import PromptBuilder

logger = logging.getLogger(__name__)

load_dotenv()


class QuestGenerator:
    """
    LLMClient 를 사용한 퀘스트 생성기.

    LLMClient 인터페이스에만 의존하므로 API 공급자를 교체해도
    이 클래스를 수정할 필요가 없습니다 (DIP, OCP).
    """

    def __init__(self, llm_client: LLMClient):
        """
        QuestGenerator 초기화.

        Args:
            llm_client: LLMClient 구현체 (의존성 주입)
        """
        self._llm_client = llm_client
        logger.info("QuestGenerator 초기화 완료")

    def generate_quest(
        self,
        genre: str,
        theme: str,
        difficulty: int,
        quest_type: str,
    ) -> QuestData:
        """
        새로운 퀘스트를 생성합니다.

        Args:
            genre: 게임 장르
            theme: 테마/세계관
            difficulty: 난이도 (1~5)
            quest_type: 퀘스트 타입 (메인/서브/일일/반복)

        Returns:
            QuestData: 생성된 퀘스트 도메인 객체

        Raises:
            ValueError: 응답에서 필수 필드를 파싱하지 못한 경우
            Exception: API 호출 실패 시
        """
        try:
            prompt = PromptBuilder.create_quest_prompt(genre, theme, difficulty, quest_type)
            logger.info(
                "퀘스트 생성 요청 - 장르: %s, 테마: %s, 난이도: %d, 타입: %s",
                genre, theme, difficulty, quest_type,
            )

            response_text = self._llm_client.complete(prompt)
            logger.info("API 응답 수신 (길이: %d자)", len(response_text))

            raw = self._parse_json_response(response_text)
            raw["genre"] = genre
            raw["theme"] = theme

            quest = QuestData.from_dict(raw)
            logger.info("퀘스트 생성 성공: %s", quest.quest_name)
            return quest

        except (ValueError, json.JSONDecodeError) as e:
            logger.error("퀘스트 데이터 파싱 실패: %s", str(e))
            raise
        except Exception as e:
            logger.error("퀘스트 생성 실패: %s", str(e))
            raise Exception(f"퀘스트 생성 실패: {str(e)}") from e

    def regenerate_quest(
        self,
        original_quest: QuestData,
        feedback: str = "",
    ) -> QuestData:
        """
        기존 퀘스트를 재생성합니다.

        Args:
            original_quest: 기존 QuestData 객체
            feedback: 사용자 피드백

        Returns:
            QuestData: 재생성된 퀘스트 도메인 객체
        """
        try:
            prompt = PromptBuilder.create_regeneration_prompt(original_quest, feedback)
            logger.info("퀘스트 재생성 요청 - 원본: %s", original_quest.quest_name)

            response_text = self._llm_client.complete(prompt)
            logger.info("재생성 API 응답 수신 (길이: %d자)", len(response_text))

            raw = self._parse_json_response(response_text)
            raw["genre"] = original_quest.genre
            raw["theme"] = original_quest.theme

            quest = QuestData.from_dict(raw)
            logger.info("퀘스트 재생성 성공: %s", quest.quest_name)
            return quest

        except (ValueError, json.JSONDecodeError) as e:
            logger.error("재생성 데이터 파싱 실패: %s", str(e))
            raise
        except Exception as e:
            logger.error("퀘스트 재생성 실패: %s", str(e))
            raise Exception(f"퀘스트 재생성 실패: {str(e)}") from e

    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Claude 응답에서 JSON을 추출하고 파싱합니다.

        Args:
            response_text: LLM API 응답 텍스트

        Returns:
            Dict: 파싱된 JSON 딕셔너리

        Raises:
            json.JSONDecodeError: JSON 파싱 실패 시
        """
        text = response_text.strip()

        # 1차: 코드 블록 내 JSON 추출 (```json ... ``` 또는 ``` ... ```)
        json_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
        if json_block_match:
            text = json_block_match.group(1).strip()
            logger.debug("코드 블록에서 JSON 추출 성공")
            return json.loads(text)

        # 2차: 코드 블록 마커만 제거
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        # 3차: JSON 객체 범위만 추출
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
            logger.debug("텍스트에서 JSON 객체 범위 추출 (start=%d, end=%d)", start, end)

        return json.loads(text)
