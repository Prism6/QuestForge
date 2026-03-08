"""
퀘스트 생성기 모듈

Claude API를 사용하여 퀘스트를 생성합니다.
"""

import os
import json
from typing import Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

from .prompts import create_quest_prompt, create_regeneration_prompt


# 환경변수 로드
load_dotenv()


class QuestGenerator:
    """
    Claude API를 사용한 퀘스트 생성기 클래스
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        QuestGenerator 초기화

        Args:
            api_key: Anthropic API 키 (없으면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API 키가 설정되지 않았습니다. "
                ".env 파일에 ANTHROPIC_API_KEY를 설정하거나 "
                "Streamlit Secrets에 등록해주세요."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    def generate_quest(
        self,
        genre: str,
        theme: str,
        difficulty: int,
        quest_type: str
    ) -> Dict:
        """
        새로운 퀘스트를 생성합니다.

        Args:
            genre: 게임 장르
            theme: 테마/세계관
            difficulty: 난이도 (1~5)
            quest_type: 퀘스트 타입 (메인/서브/일일/반복)

        Returns:
            Dict: 생성된 퀘스트 데이터

        Raises:
            Exception: API 호출 실패 또는 JSON 파싱 실패 시
        """
        try:
            # 프롬프트 생성
            prompt = create_quest_prompt(genre, theme, difficulty, quest_type)

            # Claude API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=1.0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답 텍스트 추출
            response_text = response.content[0].text

            # JSON 파싱
            quest_data = self._parse_json_response(response_text)

            # 메타데이터 추가
            quest_data["genre"] = genre
            quest_data["theme"] = theme

            return quest_data

        except json.JSONDecodeError as e:
            raise Exception(f"JSON 파싱 실패: {str(e)}\n응답: {response_text}")
        except Exception as e:
            raise Exception(f"퀘스트 생성 실패: {str(e)}")

    def regenerate_quest(
        self,
        original_quest: Dict,
        feedback: str = ""
    ) -> Dict:
        """
        기존 퀘스트를 재생성합니다.

        Args:
            original_quest: 기존 퀘스트 데이터
            feedback: 사용자 피드백

        Returns:
            Dict: 재생성된 퀘스트 데이터

        Raises:
            Exception: API 호출 실패 또는 JSON 파싱 실패 시
        """
        try:
            # 재생성 프롬프트 생성
            prompt = create_regeneration_prompt(original_quest, feedback)

            # Claude API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=1.0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답 텍스트 추출
            response_text = response.content[0].text

            # JSON 파싱
            quest_data = self._parse_json_response(response_text)

            # 메타데이터 추가 (원본에서 가져오기)
            quest_data["genre"] = original_quest.get("genre", "")
            quest_data["theme"] = original_quest.get("theme", "")

            return quest_data

        except json.JSONDecodeError as e:
            raise Exception(f"JSON 파싱 실패: {str(e)}\n응답: {response_text}")
        except Exception as e:
            raise Exception(f"퀘스트 재생성 실패: {str(e)}")

    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Claude 응답에서 JSON을 추출하고 파싱합니다.

        Args:
            response_text: Claude API 응답 텍스트

        Returns:
            Dict: 파싱된 JSON 데이터

        Raises:
            json.JSONDecodeError: JSON 파싱 실패 시
        """
        # 응답에서 JSON 부분만 추출 (마크다운 코드 블록 제거)
        text = response_text.strip()

        # ```json ... ``` 형태 제거
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # JSON 파싱
        return json.loads(text)

    def validate_quest_data(self, quest_data: Dict) -> bool:
        """
        퀘스트 데이터의 필수 필드를 검증합니다.

        Args:
            quest_data: 검증할 퀘스트 데이터

        Returns:
            bool: 검증 통과 여부
        """
        required_fields = [
            "quest_name",
            "quest_type",
            "difficulty",
            "npc",
            "objective",
            "rewards",
            "dialogue"
        ]

        for field in required_fields:
            if field not in quest_data:
                return False

        # 중첩 필드 검증
        if not isinstance(quest_data.get("npc"), dict):
            return False
        if not isinstance(quest_data.get("objective"), dict):
            return False
        if not isinstance(quest_data.get("rewards"), dict):
            return False
        if not isinstance(quest_data.get("dialogue"), dict):
            return False

        return True
