"""
퀘스트 도메인 모델 모듈

퀘스트를 구성하는 데이터 클래스를 정의합니다.
Dict 대신 타입 안전한 객체를 사용하여 추상화 수준을 높입니다.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NPC:
    """NPC 정보"""
    name: str
    location: str


@dataclass
class Objective:
    """퀘스트 목표"""
    type: str
    target: str
    location: str
    count: Optional[int] = None


@dataclass
class Rewards:
    """퀘스트 보상"""
    gold: int
    exp: int
    items: List[str] = field(default_factory=list)


@dataclass
class Dialogue:
    """NPC 대사"""
    accept: str
    progress: str
    complete: str


@dataclass
class QuestData:
    """
    퀘스트 전체 데이터 모델.

    from_dict() / to_dict() 를 통해 API 응답(Dict)과 도메인 객체 사이를
    변환합니다. 필수 필드 누락 시 ValueError를 발생시켜 조기 실패(fail-fast)합니다.
    """

    quest_name: str
    quest_type: str
    difficulty: int
    npc: NPC
    objective: Objective
    rewards: Rewards
    dialogue: Dialogue
    description: str = ""
    prerequisites: List[str] = field(default_factory=list)
    next_quest: Optional[str] = None
    quest_id: str = ""
    genre: str = ""
    theme: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestData":
        """
        딕셔너리로부터 QuestData 인스턴스를 생성합니다.

        Args:
            data: API 응답 또는 저장된 퀘스트 딕셔너리

        Returns:
            QuestData: 도메인 객체

        Raises:
            ValueError: 필수 필드가 없거나 타입이 잘못된 경우
        """
        try:
            return cls(
                quest_name=data["quest_name"],
                quest_type=data["quest_type"],
                difficulty=int(data["difficulty"]),
                description=data.get("description", ""),
                npc=NPC(
                    name=data["npc"]["name"],
                    location=data["npc"]["location"],
                ),
                objective=Objective(
                    type=data["objective"]["type"],
                    target=data["objective"]["target"],
                    location=data["objective"]["location"],
                    count=data["objective"].get("count"),
                ),
                rewards=Rewards(
                    gold=int(data["rewards"]["gold"]),
                    exp=int(data["rewards"]["exp"]),
                    items=data["rewards"].get("items", []),
                ),
                dialogue=Dialogue(
                    accept=data["dialogue"]["accept"],
                    progress=data["dialogue"]["progress"],
                    complete=data["dialogue"]["complete"],
                ),
                prerequisites=data.get("prerequisites", []),
                next_quest=data.get("next_quest"),
                quest_id=data.get("quest_id", ""),
                genre=data.get("genre", ""),
                theme=data.get("theme", ""),
            )
        except KeyError as e:
            raise ValueError(f"퀘스트 데이터에 필수 필드가 없습니다: {e}") from e
        except (TypeError, ValueError) as e:
            raise ValueError(f"퀘스트 데이터 형식이 올바르지 않습니다: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """
        QuestData 인스턴스를 딕셔너리로 변환합니다.

        Returns:
            Dict: JSON 직렬화 가능한 퀘스트 딕셔너리
        """
        return {
            "quest_id": self.quest_id,
            "quest_name": self.quest_name,
            "quest_type": self.quest_type,
            "difficulty": self.difficulty,
            "genre": self.genre,
            "theme": self.theme,
            "description": self.description,
            "npc": {
                "name": self.npc.name,
                "location": self.npc.location,
            },
            "objective": {
                "type": self.objective.type,
                "target": self.objective.target,
                "location": self.objective.location,
                "count": self.objective.count,
            },
            "rewards": {
                "gold": self.rewards.gold,
                "exp": self.rewards.exp,
                "items": self.rewards.items,
            },
            "dialogue": {
                "accept": self.dialogue.accept,
                "progress": self.dialogue.progress,
                "complete": self.dialogue.complete,
            },
            "prerequisites": self.prerequisites,
            "next_quest": self.next_quest,
        }
