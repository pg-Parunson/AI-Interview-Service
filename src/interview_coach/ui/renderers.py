"""UI 렌더링 함수"""

from typing import List

import streamlit as st
import streamlit.components.v1 as components

from ..core.models import Conversation
from .components.react_components import DASHBOARD_COMPONENT

def render_conversation(messages: List[Conversation]) -> None:
    """대화형 UI 렌더링"""
    if not messages:
        return
        
    for msg in messages:
        if msg.role == 'interviewer':
            st.write(f"👤 면접관: {msg.content}")
        else:
            st.write(f"🧑‍💻 지원자: {msg.content}")
        
        if msg.feedback:
            with st.expander("🔍 상세 피드백 보기", expanded=True):
                st.write("### 이해도 평가")
                st.write(msg.feedback['understanding'])
                
                st.write("### 강점")
                for strength in msg.feedback['strengths']:
                    st.write(f"- {strength}")
                
                st.write("### 개선 필요")
                for improvement in msg.feedback['improvements']:
                    st.write(f"- {improvement}")
                
                st.write("### 학습 제안")
                for suggestion in msg.feedback['suggestions']:
                    st.write(f"- {suggestion}")

def render_position_selection():
    """포지션 선택 UI 렌더링"""
    st.write("### 지원하시는 포지션을 선택해주세요:")
    cols = st.columns(3)
    
    positions = {
        "frontend": "프론트엔드",
        "backend": "백엔드",
        "fullstack": "풀스택"
    }
    
    selection = None
    for i, (key, label) in enumerate(positions.items()):
        with cols[i]:
            if st.button(label, key=key, use_container_width=True):
                selection = label
                
    return selection

def render_status_bar(position: str, current_topic: str, completed: int, total: int):
    """상태 표시바 렌더링"""
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"#### 선택하신 포지션: {position}")
        if current_topic:
            st.write(f"현재 주제: {current_topic}")
    with col2:
        st.write(f"진행률: {completed}/{total} 주제 완료")

def render_control_buttons(session, interviewer):
    """컨트롤 버튼 렌더링"""
    cols = st.columns(3)
    
    with cols[0]:
        if st.button("⏩ 다른 주제로 넘어가기", 
                    type="secondary", 
                    help="현재 주제를 건너뛰고 새로운 주제로 이동"):
            return "skip_topic"
            
    with cols[1]:
        if st.button("🔄 다른 질문 받기", 
                    type="secondary", 
                    help="현재 주제에서 다른 질문으로 변경"):
            return "refresh_question"
            
    with cols[2]:
        if st.button("🚫 면접 종료", 
                    type="secondary", 
                    help="면접을 종료하고 최종 평가 보기"):
            return "end_interview"
            
    return None

def render_answer_input():
    """답변 입력 UI 렌더링"""
    st.write("### 답변 입력")
    answer = st.text_area(
        label="답변을 입력하세요:",
        key="answer_input",
        height=150,
        placeholder="이 곳에 답변을 입력해주세요..."
    )
    
    submit = st.button("답변 제출", 
                      key="submit_answer", 
                      type="primary", 
                      use_container_width=True)
                      
    return answer if submit else None

def render_final_evaluation(feedback: str):
    """최종 평가 표시"""
    st.write("## 📋 최종 면접 평가")
    st.markdown(feedback)