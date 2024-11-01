"""입력 검증 유틸리티"""

from typing import Tuple

import streamlit as st

from ..core.session import InterviewSession
from ..config.constants import UsageLimits
from ..config.constants import POSITION_TOPICS

def enforce_limits(session: InterviewSession, answer: str) -> Tuple[bool, str]:
    """사용량 제한 검사"""
    # 답변 길이 체크
    if len(answer) > UsageLimits.MAX_ANSWER_LENGTH:
        return False, f"""
        답변이 너무 깁니다. {UsageLimits.MAX_ANSWER_LENGTH}자 이내로 작성해주세요.
        
        현재 답변 길이: {len(answer)}자
        제한 길이: {UsageLimits.MAX_ANSWER_LENGTH}자
        
        💡 Tip: 답변이 길어진다면 핵심 내용을 중심으로 구조화하여 설명하는 것이 효과적입니다.
        """
    
    # 답변 길이 경고
    if len(answer) > UsageLimits.MAX_ANSWER_LENGTH * 0.8:
        st.warning(f"""
        답변이 제한 길이에 근접하고 있습니다.
        현재 답변 길이: {len(answer)}자 / {UsageLimits.MAX_ANSWER_LENGTH}자
        """)
    
    # 현재 주제에서의 답변 횟수 체크
    current_responses = len([msg for msg in session.get_current_conversation() 
                           if msg.role == 'candidate'])
                           
    if current_responses >= UsageLimits.MAX_RESPONSES_PER_TOPIC:
        return False, "이 주제에 대한 연습을 충분히 하셨네요. 다음 주제로 넘어가시겠습니까?"
    
    # 총 주제 수 체크
    if len(session.completed_topics) >= UsageLimits.MAX_TOPICS_PER_SESSION:
        remaining_topics = [
            topic for topic in POSITION_TOPICS[session.position]
            if topic not in session.completed_topics
        ]
        if not remaining_topics:
            return False, """
            면접 연습이 완료되었습니다! 
            새로운 세션에서는 다른 주제들로 연습해보시는 것을 추천드립니다.
            지금까지의 연습 결과를 확인하시겠습니까?
            """
        # 마지막 주제는 완료할 수 있도록 허용
        if len(remaining_topics) > 1:
            return False, "이번 세션의 연습량이 충분합니다. 잠시 휴식 후 새로운 세션을 시작해주세요."
        
    return True, ""