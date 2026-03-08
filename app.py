"""
QuestForge - AI 퀘스트 생성기

게임 기획자를 위한 AI 퀘스트 생성 웹 애플리케이션
"""

import os
import streamlit as st
from utils.quest_generator import QuestGenerator
from utils.data_exporter import DataExporter


# 페이지 설정
st.set_page_config(
    page_title="QuestForge - AI 퀘스트 생성기",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """세션 상태 초기화"""
    if "quest_history" not in st.session_state:
        st.session_state.quest_history = []
    if "current_quest" not in st.session_state:
        st.session_state.current_quest = None
    if "generator" not in st.session_state:
        try:
            # Streamlit Cloud Secrets에서 API 키 가져오기 시도
            api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
            if not api_key:
                # 환경변수에서 가져오기
                api_key = os.getenv("ANTHROPIC_API_KEY")
            st.session_state.generator = QuestGenerator(api_key=api_key)
        except Exception as e:
            st.session_state.generator = None
            st.session_state.init_error = str(e)


def display_sidebar():
    """사이드바 UI 렌더링"""
    with st.sidebar:
        st.title("🎯 QuestForge")
        st.markdown("**AI 퀘스트 생성기**")
        st.markdown("---")

        # 장르 선택
        genre = st.selectbox(
            "📌 장르 선택",
            ["RPG", "액션", "시뮬레이션", "어드벤처", "MMORPG", "로그라이크"],
            help="게임의 장르를 선택하세요"
        )

        # 테마 입력
        theme = st.text_input(
            "📝 테마/세계관 입력",
            placeholder="예: 중세 판타지 왕국, 사이버펑크 도시",
            help="퀘스트의 배경이 되는 테마를 입력하세요"
        )

        # 난이도 설정
        difficulty = st.slider(
            "⚔️ 난이도",
            min_value=1,
            max_value=5,
            value=3,
            help="난이도가 높을수록 보상이 증가합니다"
        )

        # 퀘스트 타입
        quest_type = st.selectbox(
            "📋 퀘스트 타입",
            ["메인", "서브", "일일", "반복"],
            help="퀘스트의 유형을 선택하세요"
        )

        st.markdown("---")

        # 생성 버튼
        generate_button = st.button(
            "🔮 퀘스트 생성하기",
            type="primary",
            use_container_width=True
        )

        # 히스토리 영역
        st.markdown("---")
        st.markdown("### 📚 생성 히스토리")

        if st.session_state.quest_history:
            st.caption(f"총 {len(st.session_state.quest_history)}개 생성됨")

            # 히스토리 목록 표시 (최근 5개만)
            for i, quest in enumerate(reversed(st.session_state.quest_history[-5:])):
                with st.expander(f"{quest.get('quest_name', '알 수 없는 퀘스트')}", expanded=False):
                    st.write(f"**장르:** {quest.get('genre', '-')}")
                    st.write(f"**난이도:** {quest.get('difficulty', 0)}/5")
                    st.write(f"**타입:** {quest.get('quest_type', '-')}")
        else:
            st.caption("아직 생성된 퀘스트가 없습니다")

        # 푸터
        st.markdown("---")
        st.caption("© 2025 한상범")
        st.caption("서강대학교 가상융합전문대학원")
        st.markdown("[GitHub](https://github.com)")

        return {
            "genre": genre,
            "theme": theme,
            "difficulty": difficulty,
            "quest_type": quest_type,
            "generate": generate_button
        }


def display_quest(quest_data):
    """퀘스트 데이터 표시"""
    if not quest_data:
        st.info("👈 왼쪽 사이드바에서 조건을 설정하고 퀘스트를 생성해보세요!")
        return

    # 퀘스트 헤더
    st.header(f"🎯 {quest_data.get('quest_name', '퀘스트 이름 없음')}")

    # 기본 정보
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("장르", quest_data.get("genre", "-"))
    with col2:
        st.metric("타입", quest_data.get("quest_type", "-"))
    with col3:
        difficulty_stars = "⭐" * quest_data.get("difficulty", 0)
        st.metric("난이도", difficulty_stars)
    with col4:
        st.metric("보상 골드", f"{quest_data.get('rewards', {}).get('gold', 0):,}")

    st.markdown("---")

    # NPC 정보
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💬 NPC 정보")
        npc = quest_data.get("npc", {})
        st.write(f"**이름:** {npc.get('name', '-')}")
        st.write(f"**위치:** {npc.get('location', '-')}")

    with col2:
        st.subheader("🎯 목표")
        objective = quest_data.get("objective", {})
        st.write(f"**유형:** {objective.get('type', '-')}")
        st.write(f"**대상:** {objective.get('target', '-')}")
        st.write(f"**장소:** {objective.get('location', '-')}")
        if objective.get('count'):
            st.write(f"**수량:** {objective.get('count')}")

    st.markdown("---")

    # 보상 정보
    st.subheader("💰 보상")
    rewards = quest_data.get("rewards", {})
    reward_col1, reward_col2, reward_col3 = st.columns(3)
    with reward_col1:
        st.write(f"**골드:** {rewards.get('gold', 0):,}")
    with reward_col2:
        st.write(f"**경험치:** {rewards.get('exp', 0):,}")
    with reward_col3:
        items = rewards.get('items', [])
        if items:
            st.write(f"**아이템:** {', '.join(items)}")
        else:
            st.write("**아이템:** 없음")

    st.markdown("---")

    # 대사
    st.subheader("💭 대사")
    dialogue = quest_data.get("dialogue", {})

    with st.expander("📜 수락 대사", expanded=True):
        st.write(dialogue.get("accept", "-"))

    with st.expander("🔄 진행 중 대사"):
        st.write(dialogue.get("progress", "-"))

    with st.expander("✅ 완료 대사"):
        st.write(dialogue.get("complete", "-"))


def main():
    """메인 애플리케이션"""
    # 세션 상태 초기화
    init_session_state()

    # 초기화 에러 체크
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

    # 사이드바 렌더링
    sidebar_data = display_sidebar()

    # 퀘스트 생성 로직
    if sidebar_data["generate"]:
        if not sidebar_data["theme"]:
            st.warning("⚠️ 테마/세계관을 입력해주세요!")
        else:
            with st.spinner("🔮 퀘스트를 생성하는 중..."):
                try:
                    # 퀘스트 생성
                    quest_data = st.session_state.generator.generate_quest(
                        genre=sidebar_data["genre"],
                        theme=sidebar_data["theme"],
                        difficulty=sidebar_data["difficulty"],
                        quest_type=sidebar_data["quest_type"]
                    )

                    # 검증
                    if st.session_state.generator.validate_quest_data(quest_data):
                        # quest_id 생성 (히스토리 개수 기반)
                        quest_id = f"Q{len(st.session_state.quest_history) + 1:03d}"
                        quest_data["quest_id"] = quest_id

                        # 현재 퀘스트 및 히스토리에 추가
                        st.session_state.current_quest = quest_data
                        st.session_state.quest_history.append(quest_data)

                        st.success("✅ 퀘스트 생성 완료!")
                    else:
                        st.error("⚠️ 생성된 퀘스트 데이터가 올바르지 않습니다.")

                except Exception as e:
                    st.error(f"❌ 퀘스트 생성 실패: {str(e)}")

    # 메인 영역
    st.title("QuestForge - AI 퀘스트 생성기")
    st.markdown("게임 기획자를 위한 AI 기반 퀘스트 자동 생성 도구")
    st.markdown("---")

    # 퀘스트 표시
    if st.session_state.current_quest:
        display_quest(st.session_state.current_quest)

        st.markdown("---")

        # 액션 버튼들
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # JSON 다운로드
            json_data, json_filename, json_mime = DataExporter.create_download_data(
                [st.session_state.current_quest],
                "json"
            )
            st.download_button(
                label="📥 JSON 다운로드",
                data=json_data,
                file_name=json_filename,
                mime=json_mime,
                use_container_width=True
            )

        with col2:
            # Excel 다운로드 (전체 히스토리)
            if st.session_state.quest_history:
                excel_data, excel_filename, excel_mime = DataExporter.create_download_data(
                    st.session_state.quest_history,
                    "excel"
                )
                st.download_button(
                    label="📥 Excel 다운로드 (전체)",
                    data=excel_data,
                    file_name=excel_filename,
                    mime=excel_mime,
                    use_container_width=True
                )

        with col3:
            # 재생성 버튼
            if st.button("🔄 재생성", use_container_width=True):
                with st.spinner("🔮 퀘스트를 재생성하는 중..."):
                    try:
                        regenerated_quest = st.session_state.generator.regenerate_quest(
                            st.session_state.current_quest
                        )

                        # quest_id 유지
                        regenerated_quest["quest_id"] = st.session_state.current_quest.get("quest_id")

                        # 현재 퀘스트 업데이트
                        st.session_state.current_quest = regenerated_quest

                        # 히스토리에서 같은 ID 찾아서 업데이트
                        for i, quest in enumerate(st.session_state.quest_history):
                            if quest.get("quest_id") == regenerated_quest.get("quest_id"):
                                st.session_state.quest_history[i] = regenerated_quest
                                break

                        st.success("✅ 퀘스트 재생성 완료!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ 재생성 실패: {str(e)}")

        with col4:
            # 히스토리 초기화
            if st.button("🗑️ 히스토리 초기화", use_container_width=True):
                st.session_state.quest_history = []
                st.session_state.current_quest = None
                st.success("✅ 히스토리가 초기화되었습니다")
                st.rerun()

    else:
        # 퀘스트가 없을 때
        display_quest(None)


if __name__ == "__main__":
    main()
