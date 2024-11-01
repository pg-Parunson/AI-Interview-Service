"""InterviewSession 테스트"""

import pytest
from interview_coach.core.session import InterviewSession
from interview_coach.core.models import Conversation

@pytest.fixture
def session():
    session = InterviewSession()
    session.position = "프론트엔드"
    session.current_topic = "JavaScript/TypeScript 기초"
    return session

def test_add_message(session):
    session.add_message("interviewer", "테스트 질문")
    session.add_message("candidate", "테스트 답변")
    
    conversations = session.get_current_conversation()
    assert len(conversations) == 2
    assert conversations[0].role == "interviewer"
    assert conversations[0].content == "테스트 질문"
    assert conversations[1].role == "candidate"
    assert conversations[1].content == "테스트 답변"

def test_clear_current_conversation(session):
    session.add_message("interviewer", "테스트 질문")
    session.clear_current_conversation()
    
    assert session.current_topic is None
    assert session.current_topic in session.completed_topics
    assert len(session.get_current_conversation()) == 0

def test_get_remaining_topics(session):
    session.completed_topics = ["JavaScript/TypeScript 기초"]
    remaining = session.get_remaining_topics()
    
    assert "JavaScript/TypeScript 기초" not in remaining
    assert len(remaining) == len(session.position_topics["프론트엔드"]) - 1

def test_get_all_conversations(session):
    # 첫 번째 주제
    session.add_message("interviewer", "첫 번째 질문")
    session.add_message("candidate", "첫 번째 답변")
    session.clear_current_conversation()
    
    # 두 번째 주제
    session.current_topic = "React/Vue/Angular 프레임워크"
    session.add_message("interviewer", "두 번째 질문")
    session.add_message("candidate", "두 번째 답변")
    
    all_conversations = session.get_all_conversations()
    assert len(all_conversations) == 2  # 첫 번째 주제의 대화만 포함
    assert all_conversations[0].content == "첫 번째 질문"
    assert all_conversations[1].content == "첫 번째 답변"

def test_reset(session):
    session.add_message("interviewer", "테스트 질문")
    session.completed_topics.append("이전 주제")
    session.interview_complete = True
    session.final_feedback = "테스트 피드백"
    
    session.reset()
    
    assert session.position is None
    assert session.current_topic is None
    assert len(session.conversations) == 0
    assert len(session.completed_topics) == 0
    assert not session.interview_complete
    assert session.final_feedback is None