"""AI 면접 코치 메인 애플리케이션"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime

from .core.interviewer import MockInterviewer
from .core.session import InterviewSession
from .utils.validation import enforce_limits
from .utils.export import InterviewExporter
from .stats.storage import FileStatisticsManager
from .config.settings import Settings, get_api_key
from .config.constants import VERSION, VERSION_INFO
from .config.constants import POSITION_TOPICS
from .ui.renderers import (
    render_conversation,
    render_position_selection,
    render_status_bar,
    render_control_buttons,
    render_answer_input,
    render_final_evaluation
)
from .ui.components.react_components import DASHBOARD_COMPONENT

def initialize_session():
    """세션 초기화"""
    if 'session' not in st.session_state:
        st.session_state.session = InterviewSession()
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

def create_react_container(root_id: str, data: dict) -> str:
    """React 컴포넌트를 위한 HTML 컨테이너 생성"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 1rem; }}
        </style>
    </head>
    <body>
        <div id="{root_id}"></div>
        <script>
            {DASHBOARD_COMPONENT}
            
            const stats = {json.dumps(data)};
            
            try {{
                ReactDOM.render(
                    React.createElement(StatisticsDashboard, {{ 
                        statistics: stats 
                    }}),
                    document.getElementById('{root_id}')
                );
            }} catch (error) {{
                console.error('렌더링 오류:', error);
                document.getElementById('{root_id}').innerHTML = 
                    `<div style="color: red; padding: 1rem;">
                        오류 발생: ${{error.message}}
                        <pre>${{error.stack}}</pre>
                    </div>`;
            }}
        </script>
    </body>
    </html>
    """

def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(**Settings.PAGE_CONFIG, menu_items=Settings.MENU_ITEMS)
    
    # 제목 및 설명
    st.title("🤖 AI 면접 코치 - 개발자 기술면접 연습")
    st.caption("🌱 면접 연습을 통해 더 나은 개발자로 성장하세요. 여러분의 도전을 응원합니다!")
    
    # 사이드바 - 버전 정보
    with st.sidebar:
        st.write(f"### 📌 v{VERSION}")
        if st.button("릴리즈 노트 보기", key="release_notes"):
            with st.expander("상세 정보", expanded=True):
                st.write(f"**현재 버전:** v{VERSION}")
                st.write(f"**마지막 업데이트:** {VERSION_INFO['마지막 업데이트']}")
                st.write("**주요 기능:**")
                for feature in VERSION_INFO["주요 기능"]:
                    st.write(f"- {feature}")
                st.write("**변경 이력:**")
                for version, changes in VERSION_INFO["변경 이력"].items():
                    st.write(f"- v{version}: {changes}")

    # 세션 초기화
    initialize_session()
    
    # API 키 설정
    api_key = get_api_key()
    if not api_key:
        st.warning("""
        Google API 키가 필요합니다.
        1. https://makersuite.google.com/app/apikey 에서 발급
        2. 발급받은 키를 입력해주세요
        """)
        return
    
    # 면접관 초기화
    if 'interviewer' not in st.session_state:
        st.session_state.interviewer = MockInterviewer(api_key)
    
    session = st.session_state.session
    interviewer = st.session_state.interviewer

    # 포지션 선택
    if not session.position:
        position = render_position_selection()
        if position:
            session.position = position
            st.rerun()
        return

    # 면접 진행 상태 표시
    if session.position:
        completed = len(session.completed_topics)
        total = len(POSITION_TOPICS[session.position])
        render_status_bar(session.position, session.current_topic, completed, total)

    # 면접 진행
    if not session.interview_complete:
        # 현재 주제가 없으면 새 주제 시작
        if not session.current_topic:
            next_topic = interviewer.get_next_topic(session)
            if next_topic:
                with st.spinner('다음 주제를 준비중입니다...'):
                    interviewer.start_topic(session, next_topic)
            else:
                session.interview_complete = True
                st.rerun()
                return
        
        # 현재 대화 표시
        st.write("---")
        if session.current_topic:
            render_conversation(session.get_current_conversation())

        # 컨트롤 버튼
        action = render_control_buttons(session, interviewer)
        if action == "skip_topic":
            session.clear_current_conversation()
            st.rerun()
        elif action == "refresh_question":
            if session.current_topic:
                with st.spinner('새로운 질문을 준비중입니다...'):
                    interviewer.refresh_current_topic(session)
                st.rerun()
            else:
                st.warning("현재 진행 중인 주제가 없습니다.")
        elif action == "end_interview":
            session.interview_complete = True
            st.rerun()

        # 답변 입력 및 처리
        answer = render_answer_input()
        if answer is not None:
            if not answer.strip():
                st.warning("답변을 입력해주세요.")
            else:
                # 사용량 제한 검사
                is_allowed, limit_message = enforce_limits(session, answer)
                if not is_allowed:
                    st.warning(limit_message)
                    return
                
                with st.spinner('답변을 분석중입니다...'):
                    response = interviewer.handle_answer(session, answer)
                    
                    if response['type'] in ['follow_up', 'hint']:
                        st.rerun()
                    else:  # conclude
                        st.success("해당 주제에 대한 평가가 완료되었습니다.")
                        session.clear_current_conversation()
                        st.rerun()

    # 면접 완료 처리
    if session.interview_complete:
        if not session.final_feedback:
            st.write("## 🎉 면접이 모두 완료되었습니다!")
            
            with st.spinner('최종 평가를 작성중입니다...'):
                session.final_feedback = interviewer.generate_final_evaluation(session)
                
                # 통계 업데이트
                stats_manager = FileStatisticsManager()
                stats_manager.update_statistics(session)
                st.rerun()
        
        else:
            # 1. 최종 평가 표시
            st.write("## 📋 최종 면접 평가")
            st.markdown(session.final_feedback)
            
            # 2. 면접 기록 다운로드 옵션
            st.write("### 💾 면접 기록 다운로드")
            txt_data = InterviewExporter.to_txt(session)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            
            st.download_button(
                label="📝 면접 기록 다운로드 (TXT)",
                data=txt_data.encode('utf-8'),
                file_name=f"면접기록_{session.position}_{timestamp}.txt",
                mime="text/plain",
                help="면접 내용과 피드백을 텍스트 파일로 다운로드합니다."
            )
            
            # 3. 새로운 면접 시작 옵션
            if st.button("새로운 면접 시작", key="new_interview", type="primary"):
                st.session_state.session = InterviewSession()
                st.session_state.submitted = False
                st.rerun()

            # 4. 통계 표시
            st.write("### 📊 전체 면접 통계")
            stats_manager = FileStatisticsManager()
            stats_summary = stats_manager.get_statistics_summary()

            # React 컴포넌트 렌더링
            components.html(
                create_react_container("stats-root", stats_summary),
                height=500
            )

if __name__ == "__main__":
    main()