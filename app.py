"""
QuestForge - AI 퀘스트 생성기

게임 기획자를 위한 AI 퀘스트 생성 웹 애플리케이션
"""

import os
import logging
from typing import Optional

import streamlit as st

from utils.anthropic_client import AnthropicLLMClient
from utils.data_exporter import DataExporter
from utils.exceptions import QuestForgeError
from utils.models import QuestData
from utils.prompts import PromptBuilder
from utils.quest_generator import QuestGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="QuestForge - AI 퀘스트 생성기",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; }

    .quest-description-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-left: 4px solid #e94560;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        color: #e0e0e0;
        font-style: italic;
        line-height: 1.6;
    }

    .diff-1 { color: #4caf50; font-weight: bold; }
    .diff-2 { color: #8bc34a; font-weight: bold; }
    .diff-3 { color: #ffc107; font-weight: bold; }
    .diff-4 { color: #ff5722; font-weight: bold; }
    .diff-5 { color: #f44336; font-weight: bold; }

    .section-divider { border: none; border-top: 1px solid #333; margin: 1rem 0; }

    .quest-type-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        background-color: #0f3460;
        color: #e94560;
        border: 1px solid #e94560;
    }
</style>
""", unsafe_allow_html=True)

# 난이도 아이콘 상수
DIFFICULTY_COLORS = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "💀"}

# 사이드바 옵션 — PromptBuilder 상수에서 파생 (SSOT)
GENRE_OPTIONS = list(PromptBuilder.GENRE_TONE_GUIDE.keys())
QUEST_TYPE_OPTIONS = list(PromptBuilder.QUEST_TYPE_KO_TO_EN.keys())


def init_session_state() -> None:
    """세션 상태 초기화"""
    if "quest_history" not in st.session_state:
        st.session_state.quest_history = []
    if "current_quest" not in st.session_state:
        st.session_state.current_quest = None
    if "generator" not in st.session_state:
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY")

            # DIP 적용: AnthropicLLMClient 를 QuestGenerator 에 주입
            llm_client = AnthropicLLMClient(api_key=api_key)
            st.session_state.generator = QuestGenerator(llm_client=llm_client)
            logger.info("QuestForge 앱 초기화 완료")
        except Exception as e:
            st.session_state.generator = None
            st.session_state.init_error = str(e)
            logger.error("QuestForge 초기화 실패: %s", str(e))


def display_sidebar() -> dict:
    """사이드바 UI 렌더링"""
    with st.sidebar:
        st.title("🎯 QuestForge")
        st.markdown("**AI 퀘스트 생성기**")
        st.markdown("---")

        genre = st.selectbox(
            "📌 장르 선택",
            GENRE_OPTIONS,
            help="게임의 장르를 선택하세요"
        )

        theme = st.text_input(
            "📝 테마/세계관 입력",
            placeholder="예: 중세 판타지 왕국, 사이버펑크 도시",
            help="퀘스트의 배경이 되는 테마를 입력하세요"
        )

        difficulty = st.slider(
            "⚔️ 난이도",
            min_value=1,
            max_value=5,
            value=3,
            help="난이도가 높을수록 보상이 증가합니다"
        )

        quest_type = st.selectbox(
            "📋 퀘스트 타입",
            QUEST_TYPE_OPTIONS,
            help="퀘스트의 유형을 선택하세요"
        )

        st.markdown("---")
        generate_button = st.button(
            "🔮 퀘스트 생성하기",
            type="primary",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("### 📚 생성 히스토리")

        if st.session_state.quest_history:
            st.caption(f"총 {len(st.session_state.quest_history)}개 생성됨")
            for quest in reversed(st.session_state.quest_history[-5:]):
                with st.expander(quest.quest_name, expanded=False):
                    st.write(f"**장르:** {quest.genre}")
                    st.write(f"**난이도:** {quest.difficulty}/5")
                    st.write(f"**타입:** {quest.quest_type}")
        else:
            st.caption("아직 생성된 퀘스트가 없습니다")

        st.markdown("---")
        st.caption("© 2025 한상범")
        st.caption("서강대학교 가상융합전문대학원")
        st.markdown("[GitHub](https://github.com)")

        return {
            "genre": genre,
            "theme": theme,
            "difficulty": difficulty,
            "quest_type": quest_type,
            "generate": generate_button,
        }


def display_quest(quest: Optional[QuestData]) -> None:
    """
    퀘스트 데이터를 화면에 표시합니다.

    Args:
        quest: 표시할 QuestData 객체. None 이면 안내 메시지를 표시합니다.
    """
    if quest is None:
        st.info("👈 왼쪽 사이드바에서 조건을 설정하고 퀘스트를 생성해보세요!")
        return

    diff_icon = DIFFICULTY_COLORS.get(quest.difficulty, "⭐")
    st.header(f"🎯 {quest.quest_name}")

    if quest.description:
        st.markdown(
            f'<div class="quest-description-card">📖 {quest.description}</div>',
            unsafe_allow_html=True
        )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("장르", quest.genre or "-")
    with col2:
        quest_type_display = PromptBuilder.QUEST_TYPE_EN_TO_KO.get(quest.quest_type, quest.quest_type)
        st.metric("타입", quest_type_display)
    with col3:
        difficulty_stars = f"{diff_icon} {'★' * quest.difficulty}{'☆' * (5 - quest.difficulty)}"
        st.metric("난이도", difficulty_stars)
    with col4:
        st.metric("보상 골드", f"{quest.rewards.gold:,}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💬 NPC 정보")
        st.write(f"**이름:** {quest.npc.name}")
        st.write(f"**위치:** {quest.npc.location}")

    with col2:
        st.subheader("🎯 목표")
        st.write(f"**유형:** {quest.objective.type}")
        st.write(f"**대상:** {quest.objective.target}")
        st.write(f"**장소:** {quest.objective.location}")
        if quest.objective.count:
            st.write(f"**수량:** {quest.objective.count}")

    st.markdown("---")

    st.subheader("💰 보상")
    reward_col1, reward_col2, reward_col3 = st.columns(3)
    with reward_col1:
        st.write(f"**골드:** {quest.rewards.gold:,}")
    with reward_col2:
        st.write(f"**경험치:** {quest.rewards.exp:,}")
    with reward_col3:
        if quest.rewards.items:
            st.write(f"**아이템:** {', '.join(quest.rewards.items)}")
        else:
            st.write("**아이템:** 없음")

    st.markdown("---")

    st.subheader("💭 대사")
    with st.expander("📜 수락 대사", expanded=True):
        st.write(quest.dialogue.accept)
    with st.expander("🔄 진행 중 대사"):
        st.write(quest.dialogue.progress)
    with st.expander("✅ 완료 대사"):
        st.write(quest.dialogue.complete)


def main() -> None:
    """메인 애플리케이션"""
    init_session_state()

    if st.session_state.generator is None:
        st.error("⚠️ QuestForge 초기화 실패")
        st.error(st.session_state.get("init_error", "알 수 없는 오류"))
        st.info("""
        **해결 방법:**
        1. `.env` 파일을 생성하고 `ANTHROPIC_API_KEY`를 설정하세요
        2. 또는 Streamlit Cloud Secrets에 API 키를 등록하세요

        자세한 내용은 README.md를 참고하세요.
        """)
        return

    sidebar_data = display_sidebar()

    if sidebar_data["generate"]:
        if not sidebar_data["theme"]:
            st.warning("⚠️ 테마/세계관을 입력해주세요!")
        else:
            with st.spinner("🔮 퀘스트를 생성하는 중..."):
                try:
                    quest = st.session_state.generator.generate_quest(
                        genre=sidebar_data["genre"],
                        theme=sidebar_data["theme"],
                        difficulty=sidebar_data["difficulty"],
                        quest_type=sidebar_data["quest_type"],
                    )
                    quest.quest_id = f"Q{len(st.session_state.quest_history) + 1:03d}"
                    st.session_state.current_quest = quest
                    st.session_state.quest_history.append(quest)
                    st.success("✅ 퀘스트 생성 완료!")

                except QuestForgeError as e:
                    st.error(f"❌ 퀘스트 생성 실패: {str(e)}")

    st.title("QuestForge - AI 퀘스트 생성기")
    st.markdown("게임 기획자를 위한 AI 기반 퀘스트 자동 생성 도구")
    st.markdown("---")

    if st.session_state.current_quest:
        display_quest(st.session_state.current_quest)
        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            json_data, json_filename, json_mime = DataExporter.create_download_data(
                [st.session_state.current_quest], "json"
            )
            st.download_button(
                label="📥 JSON 다운로드",
                data=json_data,
                file_name=json_filename,
                mime=json_mime,
                use_container_width=True,
            )

        with col2:
            if st.session_state.quest_history:
                excel_data, excel_filename, excel_mime = DataExporter.create_download_data(
                    st.session_state.quest_history, "excel"
                )
                st.download_button(
                    label="📥 Excel 다운로드 (전체)",
                    data=excel_data,
                    file_name=excel_filename,
                    mime=excel_mime,
                    use_container_width=True,
                )

        with col3:
            if st.button("🔄 재생성", use_container_width=True):
                with st.spinner("🔮 퀘스트를 재생성하는 중..."):
                    try:
                        regenerated = st.session_state.generator.regenerate_quest(
                            st.session_state.current_quest
                        )
                        regenerated.quest_id = st.session_state.current_quest.quest_id

                        st.session_state.current_quest = regenerated
                        for i, q in enumerate(st.session_state.quest_history):
                            if q.quest_id == regenerated.quest_id:
                                st.session_state.quest_history[i] = regenerated
                                break

                        st.success("✅ 퀘스트 재생성 완료!")
                        st.rerun()

                    except QuestForgeError as e:
                        st.error(f"❌ 재생성 실패: {str(e)}")

        with col4:
            if st.button("🗑️ 히스토리 초기화", use_container_width=True):
                st.session_state.quest_history = []
                st.session_state.current_quest = None
                st.success("✅ 히스토리가 초기화되었습니다")
                st.rerun()

    else:
        display_quest(None)


if __name__ == "__main__":
    main()
