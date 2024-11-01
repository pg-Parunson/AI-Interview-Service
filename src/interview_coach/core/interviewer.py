"""면접관 로직 구현"""

from typing import Dict, List, Optional
import google.generativeai as genai

from .models import Conversation, AnswerAnalysis
from .session import InterviewSession
from ..prompts.interview import InterviewPrompts
from ..prompts.evaluation import EvaluationPrompts
from ..config.constants import POSITION_TOPICS

class MockInterviewer:
    """AI 면접관 구현"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def get_next_topic(self, session: InterviewSession) -> Optional[str]:
        """다음 면접 주제 선택"""
        available_topics = [
            topic for topic in POSITION_TOPICS[session.position]
            if topic not in session.completed_topics
        ]
        
        if not available_topics:
            return None
            
        return available_topics[0]
    
    def get_model_response(self, prompt: str, retry_count: int = 3) -> Optional[str]:
        """Gemini API를 사용하여 응답을 생성"""
        for i in range(retry_count):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        candidate_count=1,
                    )
                )
                if response.text:
                    return response.text
            except Exception as e:
                if i == retry_count - 1:
                    raise e
        return None

    def _format_conversation_history(self, conversation: List[Conversation]) -> str:
        """대화 내역을 문자열로 포맷팅"""
        formatted = []
        for msg in conversation:
            role = "면접관" if msg.role == "interviewer" else "지원자"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

    def analyze_answer(self, answer: str, question_context: dict) -> AnswerAnalysis:
        """답변 분석 및 다음 액션 결정"""
        prompt = InterviewPrompts.analyze_answer(
            position=question_context['position'],
            topic=question_context['topic'],
            conversation_history=self._format_conversation_history(question_context['history']),
            answer=answer
        )
        
        response = self.get_model_response(prompt)
        return self._parse_analysis_response(response)

    def handle_answer(self, session: InterviewSession, answer: str) -> Dict:
        """답변 처리 및 다음 상호작용 결정"""
        current_context = {
            'position': session.position,
            'topic': session.current_topic,
            'history': session.get_current_conversation()
        }
        
        analysis = self.analyze_answer(answer, current_context)
        session.add_message('candidate', answer)
        
        if analysis.action == 'FOLLOW_UP' or analysis.action == 'HINT':
            session.add_message('interviewer', analysis.next_response)
            return {
                'type': analysis.action.lower(),
                'response': analysis.next_response
            }
        else:  # CONCLUDE
            feedback = self._generate_topic_feedback(session)
            session.add_message('interviewer', analysis.next_response, feedback=feedback)
            return {
                'type': 'conclude',
                'response': analysis.next_response,
                'feedback': feedback
            }

    def start_topic(self, session: InterviewSession, topic: str) -> str:
        """새로운 주제로 면접 시작"""
        prompt = InterviewPrompts.start_topic(
            position=session.position,
            topic=topic
        )
        
        first_question = self.get_model_response(prompt)
        if first_question:
            session.current_topic = topic
            session.add_message('interviewer', first_question)
            return first_question
        
        return f"{topic}에 대해 설명해주시겠습니까?"

    def refresh_current_topic(self, session: InterviewSession) -> str:
        """현재 주제에 대해 새로운 질문 생성"""
        prompt = InterviewPrompts.refresh_topic(
            position=session.position,
            topic=session.current_topic,
            conversation_history=self._format_conversation_history(session.get_current_conversation())
        )
        
        new_question = self.get_model_response(prompt)
        if new_question:
            session.conversations[session.current_topic] = []
            session.add_message('interviewer', new_question)
            return new_question
        
        return f"{session.current_topic}에 대해 다른 관점에서 이야기해보시겠어요?"

    def generate_final_evaluation(self, session: InterviewSession) -> str:
        """최종 평가 생성"""
        if not session.get_all_conversations():
            return EvaluationPrompts.get_empty_evaluation_message()
            
        prompt = EvaluationPrompts.final_evaluation(
            position=session.position,
            completed_topics=session.completed_topics,
            conversation_history=self._format_conversation_history(session.get_all_conversations())
        )
        
        return self.get_model_response(prompt) or "평가를 생성할 수 없습니다."

    def _generate_topic_feedback(self, session: InterviewSession) -> Dict:
        """주제별 상세 피드백 생성"""
        conversation = session.get_current_conversation()
        prompt = EvaluationPrompts.topic_feedback(
            position=session.position,
            topic=session.current_topic,
            conversation_history=self._format_conversation_history(conversation)
        )
        
        try:
            feedback = self.get_model_response(prompt)
            return self._parse_feedback_response(feedback)
        except:
            return {
                'understanding': '기본적인 이해도를 보여주었습니다.',
                'strengths': ['성실한 답변 태도를 보여주었습니다.'],
                'improvements': ['더 구체적인 예시가 필요합니다.'],
                'suggestions': ['관련 실무 경험을 쌓아보시기를 권장드립니다.']
            }

    @staticmethod
    def _parse_analysis_response(response: str) -> AnswerAnalysis:
        """분석 응답 파싱"""
        try:
            parts = response.strip().split('\n')
            return AnswerAnalysis(
                action=parts[0].split(':')[1].strip(),
                completion_score=int(parts[1].split(':')[1].strip()),
                next_response=':'.join(parts[2].split(':')[1:]).strip(),
                feedback=':'.join(parts[3].split(':')[1:]).strip() if len(parts) > 3 else None
            )
        except:
            return AnswerAnalysis(
                action='CONCLUDE',
                completion_score=3,
                next_response='네, 이해했습니다. 다음 주제로 넘어가도록 하겠습니다.',
                feedback='성실하게 답변해 주셨습니다.'
            )