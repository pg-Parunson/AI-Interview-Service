"""MockInterviewer 테스트"""

import pytest
from unittest.mock import Mock, patch

from interview_coach.core.interviewer import MockInterviewer
from interview_coach.core.session import InterviewSession
from interview_coach.core.models import Conversation

@pytest.fixture
def interviewer():
    return MockInterviewer("mock-api-key")

@pytest.fixture
def session():
    session = InterviewSession()
    session.position = "프론트엔드"
    session.current_topic = "JavaScript/TypeScript 기초"
    return session

def test_get_model_response(interviewer):
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
        mock_generate.return_value.text = "테스트 응답"
        response = interviewer.get_model_response("테스트 프롬프트")
        assert response == "테스트 응답"
        mock_generate.assert_called_once()

def test_analyze_answer(interviewer, session):
    mock_response = """
    액션: FOLLOW_UP
    답변_완성도: 4
    다음_응답: 좋은 답변입니다. 추가 질문이 있습니다.
    피드백: 구체적인 예시를 잘 들어주셨네요.
    """
    
    with patch.object(interviewer, 'get_model_response', return_value=mock_response):
        context = {
            'position': session.position,
            'topic': session.current_topic,
            'history': []
        }
        
        result = interviewer.analyze_answer("테스트 답변", context)
        
        assert result['action'] == 'FOLLOW_UP'
        assert result['completion_score'] == 4
        assert "좋은 답변입니다" in result['next_response']
        assert "구체적인 예시" in result['feedback']

def test_handle_answer(interviewer, session):
    mock_analysis = {
        'action': 'FOLLOW_UP',
        'completion_score': 4,
        'next_response': '추가 질문입니다.',
        'feedback': '좋은 답변입니다.'
    }
    
    with patch.object(interviewer, 'analyze_answer', return_value=mock_analysis):
        result = interviewer.handle_answer(session, "테스트 답변")
        
        assert result['type'] == 'follow_up'
        assert result['response'] == '추가 질문입니다.'
        assert len(session.get_current_conversation()) == 2  # 답변과 추가 질문

def test_generate_final_evaluation(interviewer, session):
    conversations = [
        Conversation(role="interviewer", content="첫 질문"),
        Conversation(role="candidate", content="첫 답변")
    ]
    session.conversations[session.current_topic] = conversations
    session.completed_topics.append(session.current_topic)
    
    with patch.object(interviewer, 'get_model_response', return_value="최종 평가 내용"):
        result = interviewer.generate_final_evaluation(session)
        assert result == "최종 평가 내용"

def test_refresh_current_topic(interviewer, session):
    with patch.object(interviewer, 'get_model_response', return_value="새로운 질문"):
        result = interviewer.refresh_current_topic(session)
        assert result == "새로운 질문"
        assert len(session.get_current_conversation()) == 1  # 새 질문만 있어야 함