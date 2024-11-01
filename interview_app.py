# 표준 라이브러리
import os
import json
import time
import base64
import tempfile
import csv
from pathlib import Path
from io import StringIO
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

# 서드파티 라이브러리
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from gtts import gTTS

# 음성 인식 기능 조건부 임포트
ENABLE_SPEECH = False  # 음성 기능 비활성화
try:
    import speech_recognition as sr
    ENABLE_SPEECH = True
except ImportError:
    pass

# 음성 관련 유틸리티 함수들
def text_to_speech(text: str) -> str:
    """텍스트를 음성으로 변환하고 base64 인코딩된 문자열을 반환"""
    if not text:
        return ""
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(fp.name)
            with open(fp.name, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                return base64.b64encode(audio_bytes).decode()
    except Exception as e:
        st.error(f"음성 변환 중 오류가 발생했습니다: {str(e)}")
        return ""
    finally:
        if 'fp' in locals():
            Path(fp.name).unlink(missing_ok=True)

def speech_to_text() -> str:
    """마이크로부터 음성을 입력받아 텍스트로 변환"""
    if not ENABLE_SPEECH:
        st.error("음성 인식 기능을 사용할 수 없습니다.")
        return ""

@dataclass
class Conversation:
    role: str  # 'interviewer' 또는 'candidate'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    feedback: Dict = None

@dataclass
class InterviewSession:
    position: str = None
    current_topic: str = None
    conversations: Dict[str, List[Conversation]] = field(default_factory=dict)
    completed_topics: List[str] = field(default_factory=list)
    waiting_for_next: bool = False
    interview_complete: bool = False
    final_feedback: str = None

    def add_message(self, role: str, content: str, feedback: Dict = None):
        """대화 내용을 현재 주제에 저장"""
        if self.current_topic not in self.conversations:
            self.conversations[self.current_topic] = []
            
        new_message = Conversation(role=role, content=content, feedback=feedback)
        self.conversations[self.current_topic].append(new_message)

    def get_current_conversation(self) -> List[Conversation]:
        """현재 주제의 대화 내용 반환"""
        return self.conversations.get(self.current_topic, [])

    def clear_current_conversation(self):
        """주제 완료 처리"""
        if self.current_topic:
            self.completed_topics.append(self.current_topic)
        self.current_topic = None

    def validate_completion(self) -> Tuple[bool, str]:
        """면접 종료 가능 여부 검증"""
        # 최소 1개 이상의 주제가 완료되어야 함
        if not self.completed_topics:
            return False, "최소 1개 이상의 주제에 대해 답변해야 합니다."
        
        # 각 주제별로 최소 1개 이상의 답변이 있어야 함
        for topic in self.completed_topics:
            conversation = self.conversations.get(topic, [])
            candidate_responses = [msg for msg in conversation if msg.role == 'candidate']
            if not candidate_responses:
                return False, f"'{topic}' 주제에 대한 답변이 없습니다."
                
            # 답변의 유효성 검사 (빈 답변 체크)
            for response in candidate_responses:
                if not response.content.strip():
                    return False, f"'{topic}' 주제에 빈 답변이 있습니다."
        
        return True, ""

def render_conversation(messages: List[Conversation]) -> None:
    """대화형 UI 렌더링"""
    if not messages:  # messages가 None이거나 비어있을 경우 처리
        return
        
    for msg in messages:
        if msg.role == 'interviewer':
            st.write(f"👤 면접관: {msg.content}")
        else:
            st.write(f"🧑‍💻 지원자: {msg.content}")
        
        # 피드백이 있는 경우 표시
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
                    
def initialize_session():
    if 'session' not in st.session_state:
        st.session_state.session = InterviewSession()
        st.session_state.submitted = False

class UsageLimits:
    MAX_ANSWER_LENGTH = 3000  # 답변 최대 글자수 확장
    MAX_TOPICS_PER_SESSION = 5  # 세션당 최대 주제 수
    MAX_RESPONSES_PER_TOPIC = 10  # 주제당 최대 답변 횟수
    
def enforce_limits(session: InterviewSession, answer: str) -> Tuple[bool, str]:
    """사용량 제한 검사"""
    # 답변 길이 체크 - 경고와 제한을 분리
    if len(answer) > UsageLimits.MAX_ANSWER_LENGTH:
        return False, f"""
        답변이 너무 깁니다. {UsageLimits.MAX_ANSWER_LENGTH}자 이내로 작성해주세요.
        
        현재 답변 길이: {len(answer)}자
        제한 길이: {UsageLimits.MAX_ANSWER_LENGTH}자
        
        💡 Tip: 답변이 길어진다면 핵심 내용을 중심으로 구조화하여 설명하는 것이 효과적입니다.
        """
    elif len(answer) > UsageLimits.MAX_ANSWER_LENGTH * 0.8:  # 80% 이상일 때 경고
        st.warning(f"""
        답변이 제한 길이에 근접하고 있습니다.
        현재 답변 길이: {len(answer)}자 / {UsageLimits.MAX_ANSWER_LENGTH}자
        """)
    
    # 현재 주제에서의 답변 횟수 체크
    current_responses = len([msg for msg in session.get_current_conversation() 
                           if msg.role == 'candidate'])
                           
    if current_responses >= UsageLimits.MAX_RESPONSES_PER_TOPIC:
        return False, "이 주제에 대한 연습을 충분히 하셨네요. 다음 주제로 넘어가시겠습니까?"
    
    # 총 주제 수 체크 (단, 마지막 주제인 경우 특별 처리)
    if len(session.completed_topics) >= UsageLimits.MAX_TOPICS_PER_SESSION:
        remaining_topics = [topic for topic in session.interviewer.position_topics[session.position]
                          if topic not in session.completed_topics]
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

def export_to_txt(session: InterviewSession) -> str:
    """면접 내용을 읽기 쉬운 텍스트 형식으로 변환"""
    lines = []
    
    # 헤더 정보
    lines.extend([
        "=" * 50,
        "📝 면접 기록",
        "=" * 50,
        f"직무: {session.position}",
        f"일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}",
        f"진행된 주제: {', '.join(session.completed_topics)}",
        "\n" + "=" * 50 + "\n"
    ])
    
    # 주제별 대화 내용 출력
    for topic in session.completed_topics:
        lines.extend([
            f"[주제] {topic}",
            "-" * 50,
            ""  # 빈 줄 추가
        ])
        
        # 해당 주제의 대화 내용이 있는 경우
        if topic in session.conversations:
            for msg in session.conversations[topic]:
                timestamp = msg.timestamp.strftime('%H:%M:%S')
                role = '👤 면접관' if msg.role == 'interviewer' else '🧑‍💻 지원자'
                lines.extend([
                    f"[{timestamp}] {role}:",
                    msg.content,
                    ""  # 메시지 사이 빈 줄
                ])
                
                # 피드백이 있는 경우
                if msg.feedback:
                    lines.extend([
                        "🔍 피드백:",
                        "* 이해도 평가:",
                        f"  {msg.feedback['understanding']}",
                        "",
                        "* 강점:",
                        *[f"  - {strength}" for strength in msg.feedback['strengths']],
                        "",
                        "* 개선 필요:",
                        *[f"  - {improvement}" for improvement in msg.feedback['improvements']],
                        "",
                        "* 학습 제안:",
                        *[f"  - {suggestion}" for suggestion in msg.feedback['suggestions']],
                        ""
                    ])
        
        lines.extend([
            "=" * 50,
            ""  # 주제 사이 빈 줄
        ])
    
    # 최종 평가 추가
    if session.final_feedback:
        lines.extend([
            "📋 최종 평가",
            "=" * 50,
            session.final_feedback,
            "=" * 50
        ])
    
    return '\n'.join(lines)
    
class MockInterviewer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        self.position_topics = {
            "프론트엔드": [
                "JavaScript/TypeScript 기초",
                "React/Vue/Angular 프레임워크",
                "HTML/CSS 및 웹 표준",
                "상태관리 및 성능 최적화",
                "웹 보안과 인증"
            ],
            "백엔드": [
                "주로 사용하는 개발 언어"
                "서버 아키텍처 설계",
                "데이터베이스 설계 및 최적화",
                "API 설계 및 보안",
                "캐싱 및 성능 최적화",
                "마이크로서비스 아키텍처"
            ],
            "풀스택": [
                "프론트엔드 프레임워크",
                "백엔드 아키텍처",
                "데이터베이스 및 캐싱",
                "DevOps 및 배포",
                "시스템 설계"
            ]
        }

    def get_model_response(self, prompt: str, retry_count: int = 3) -> str:
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
                time.sleep(1)
            except Exception as e:
                if i == retry_count - 1:
                    st.error(f"Gemini API 오류: {str(e)}")
                time.sleep(1)
        return None

    def _format_conversation_history(self, conversation: List[Conversation]) -> str:
        """대화 내역을 문자열로 포맷팅"""
        formatted = []
        for msg in conversation:
            role = "면접관" if msg.role == "interviewer" else "지원자"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

    def analyze_answer(self, answer: str, question_context: dict) -> dict:
        """답변 분석 및 다음 액션 결정"""
        history = question_context['history']
        current_depth = len([msg for msg in history if msg.role == 'interviewer'])

        prompt = f"""
        당신은 {question_context['position']} 개발자 면접관입니다.
        현재 주제: {question_context['topic']}
        현재까지의 대화:
        {self._format_conversation_history(history)}
        
        지원자의 답변: {answer}
        
        지원자의 답변을 분석하여 다음 행동을 결정해주세요.
        
        고려사항:
        1. 답변이 명확하고 좋은 경우:
           - 좀 더 깊이 있는 후속 질문
           - 실제 경험이나 예시를 물어보는 질문
           
        2. 답변이 애매하거나 부족한 경우:
           - 한번 정도는 힌트나 가이드를 주며 기회 제공
           - 그래도 어려워한다면 다른 방향의 질문으로 전환
           
        3. 답변이 잘 못하거나 모른다고 할 경우:
           - 더 이상 깊이 파고들지 않고 부드럽게 마무리
           - 긍정적인 피드백과 함께 다음 주제로 전환

        현재 대화 깊이: {current_depth}회차
        
        다음 형식으로 답변해주세요:
        액션: (FOLLOW_UP/HINT/CONCLUDE)
        답변_완성도: (1-5)
        다음_응답: (면접관의 자연스러운 답변)
        피드백: (현재 답변에 대한 간단한 피드백)
        """
        
        response = self.get_model_response(prompt)
        try:
            parts = response.strip().split('\n')
            action = parts[0].split(':')[1].strip()
            score = int(parts[1].split(':')[1].strip())
            response_text = ':'.join(parts[2].split(':')[1:]).strip()
            feedback = ':'.join(parts[3].split(':')[1:]).strip() if len(parts) > 3 else ""
            
            # 대화가 3회 이상 오갔거나 답변이 부족한 경우 자연스럽게 마무리
            if current_depth >= 3 or (score <= 2 and current_depth >= 1):
                action = 'CONCLUDE'
                response_text = f"네, 알겠습니다. {feedback} 다음 주제로 넘어가도록 하겠습니다."
            
            return {
                'action': action,
                'completion_score': score,
                'next_response': response_text,
                'feedback': feedback
            }
        except:
            return {
                'action': 'CONCLUDE',
                'completion_score': 3,
                'next_response': '네, 이해했습니다. 다음 주제로 넘어가도록 하겠습니다.',
                'feedback': '성실하게 답변해 주셨습니다.'
            }
            
    def generate_topic_feedback(self, conversation: List[Conversation], topic: str, position: str) -> Dict:
        """주제별 상세 피드백 생성"""
        conversation_history = self._format_conversation_history(conversation)
        
        prompt = f"""
        {position} 개발자 면접관으로서 다음 대화에 대한 상세한 피드백을 작성해주세요.
        
        주제: {topic}
        
        대화 내역:
        {conversation_history}
        
        다음 형식으로 피드백을 작성해주세요:
        
        이해도 평가:
        - 전반적인 개념 이해도 (상/중/하)
        - 실무 적용 능력 분석
        
        강점:
        - (2-3가지 구체적인 장점과 예시)
        
        개선 필요:
        - (2-3가지 구체적인 보완점과 예시)
        
        학습 제안:
        - (부족한 부분을 보완하기 위한 구체적인 학습 방향)
        
        피드백 작성 시 주의사항:
        1. 긍정적이고 건설적인 톤 유지
        2. 부족한 부분에 대해서는 개선 방향 제시에 중점
        3. 지원자의 현재 수준을 고려한 현실적인 학습 제안
        4. 과도한 비판이나 부정적 평가 지양
        """
        
        feedback = self.get_model_response(prompt)
        try:
            parts = feedback.split('\n\n')
            return {
                'understanding': parts[1].split(':\n')[1].strip(),
                'strengths': parts[2].split(':\n')[1].strip().split('\n'),
                'improvements': parts[3].split(':\n')[1].strip().split('\n'),
                'suggestions': parts[4].split(':\n')[1].strip().split('\n')
            }
        except:
            return {
                'understanding': '기본적인 이해도를 보여주었습니다.',
                'strengths': ['성실한 답변 태도를 보여주었습니다.'],
                'improvements': ['더 구체적인 예시가 필요합니다.'],
                'suggestions': ['관련 실무 경험을 쌓아보시기를 권장드립니다.']
            }

    def handle_answer(self, session: InterviewSession, answer: str) -> Dict:
      """답변 처리 및 다음 상호작용 결정"""
      current_context = {
          'position': session.position,
          'topic': session.current_topic,
          'history': session.get_current_conversation()  # 변경된 부분
      }
      
      # 답변 분석
      analysis = self.analyze_answer(answer, current_context)
      
      # 답변 저장
      session.add_message('candidate', answer)
      
      if analysis['action'] == 'FOLLOW_UP':
          # 추가 질문
          session.add_message('interviewer', analysis['next_response'])
          return {
              'type': 'follow_up',
              'response': analysis['next_response']
          }
      elif analysis['action'] == 'HINT':
          # 힌트 제공
          session.add_message('interviewer', analysis['next_response'])
          return {
              'type': 'hint',
              'response': analysis['next_response']
          }
      else:  # CONCLUDE
          # 주제 마무리 및 피드백 생성
          feedback = self.generate_topic_feedback(
              session.get_current_conversation(),  # 변경된 부분
              session.current_topic,
              session.position
          )
          
          session.add_message(
              'interviewer',
              analysis['next_response'],
              feedback=feedback
          )
          
          return {
              'type': 'conclude',
              'response': analysis['next_response'],
              'feedback': feedback
          }

    def get_next_topic(self, session: InterviewSession) -> str:
        """다음 면접 주제 선택"""
        available_topics = [
            topic for topic in self.position_topics[session.position]
            if topic not in session.completed_topics
        ]
        
        if not available_topics:
            return None
            
        return available_topics[0]

    def start_topic(self, session: InterviewSession, topic: str) -> str:
        """새로운 주제로 면접 시작"""
        prompt = f"""
        당신은 {session.position} 개발자 면접관입니다.
        이제 '{topic}' 주제에 대해 질문을 시작하려고 합니다.
        
        다음 조건을 만족하는 첫 질문을 생성해주세요:
        1. 주니어 개발자 수준에 적합한 난이도
        2. 기본 개념을 확인하면서도 실무 경험을 파악할 수 있는 질문
        3. 추가 질문으로 발전시킬 수 있는 개방형 질문
        4. 자연스러운 한국어로 된 질문
        
        면접관의 입장에서 자연스럽게 질문을 시작하는 형식으로 작성해주세요.
        """
        
        first_question = self.get_model_response(prompt)
        if first_question:
            session.current_topic = topic
            session.add_message('interviewer', first_question)
            return first_question
        
        return f"{topic}에 대해 설명해주시겠습니까?"
    
    def generate_final_evaluation(self, completed_topics: List[str], conversation_history: List[Conversation], position: str) -> str:
      """최종 평가 생성"""
      # 주제별 대화 품질 분석
      topic_analysis = {}
      current_topic = None
      good_topics = []
      weak_topics = []
      
      # 전체 대화 내용을 순회하면서 주제별로 분류
      for msg in conversation_history:
          if msg.role == 'interviewer' and not msg.feedback:
              # 새로운 주제의 시작으로 간주
              for topic in completed_topics:
                  if topic in msg.content:
                      current_topic = topic
                      if current_topic not in topic_analysis:
                          topic_analysis[current_topic] = {
                              'messages': [],
                              'quality_score': 0
                          }
                      break
          
          if current_topic:
              topic_analysis[current_topic]['messages'].append(msg)
      
      # 각 주제별 품질 점수 계산
      for topic, analysis in topic_analysis.items():
          messages = analysis['messages']
          
          # 실제 대화가 있는 경우에만 평가
          if messages:
              # 주제별 대화 수
              conversation_count = len([m for m in messages if m.role == 'candidate'])
              
              # 피드백이 있는 메시지 확인
              feedback_msgs = [m for m in messages if m.feedback]
              
              if feedback_msgs:
                  last_feedback = feedback_msgs[-1].feedback
                  # 마지막 피드백의 이해도에 따른 점수 할당
                  understanding_score = 0
                  if "충분한" in last_feedback['understanding'] or "좋은" in last_feedback['understanding']:
                      understanding_score = 3
                  elif "기본적인" in last_feedback['understanding']:
                      understanding_score = 2
                  
                  # 강점 수에 따른 추가 점수
                  strength_score = min(len(last_feedback['strengths']), 3)
                  
                  # 총점 계산 (대화수 * 0.5 + 이해도 + 강점)
                  quality_score = (min(conversation_count, 4) * 0.5) + understanding_score + strength_score
                  
                  if quality_score >= 4:
                      good_topics.append(topic)
                  elif quality_score <= 2:
                      weak_topics.append(topic)
                      
                  topic_analysis[topic]['quality_score'] = quality_score
      
      # 전체 평가 생성
      good_topics_count = len(good_topics)
      total_topics = len(completed_topics)
      
      if good_topics_count >= total_topics * 0.6:  # 60% 이상의 주제에서 좋은 평가
          prompt = f"""
          당신은 {position} 개발자 면접관입니다.
          전반적으로 우수한 면접 수행을 보여준 지원자에 대한 종합 평가를 진행해주세요.
          
          다음 정보를 참고해 주세요:
          - 잘 수행한 주제: {', '.join(good_topics)}
          - 보완이 필요한 주제: {', '.join(weak_topics)}
          
          평가 작성 시 다음 사항을 포함해주세요:
          1. 전반적인 기술 이해도
          2. 의사소통 능력
          3. 실무 적용 가능성
          4. 향후 발전 가능성
          5. 개선이 필요한 부분에 대한 구체적인 제안
          
          긍정적인 측면에 중점을 두되, 개선점도 건설적으로 제시해주세요.
          """
      else:
          # 기존 prompt 사용
          prompt = f"""
          당신은 {position} 개발자 면접관입니다.
          지금까지의 모든 면접 내용을 바탕으로 균형잡힌 평가를 진행해주세요.
          
          면접 진행 주제: {', '.join(completed_topics)}
          잘 수행한 주제: {', '.join(good_topics)}
          보완이 필요한 주제: {', '.join(weak_topics)}
          
          대화 내역을 분석한 결과:
          {', '.join([f"{topic}: {analysis['quality_score']:.1f}점" for topic, analysis in topic_analysis.items()])}
          
          다음 형식으로 평가를 작성해주세요:
          
          [종합 평가]
          
          1. 전반적인 역량
          - 기술적 이해도
          - 실무 적용 능력
          - 의사소통 능력
          
          2. 주요 강점
          - 잘 수행한 주제들에서 보여준 역량
          - 의사소통 방식의 장점
          
          3. 개선 제안사항
          - 보완이 필요한 영역
          - 구체적인 학습 방향
          
          4. 종합 의견
          - 현재 수준 평가
          - 성장 가능성
          
          작성 시 주의사항:
          1. 실제 대화 내용을 기반으로 구체적인 피드백 제공
          2. 개선점은 건설적인 제안 형태로 제시
          3. 지원자의 잠재력과 강점도 반드시 포함
          """
      
      return self.get_model_response(prompt)
    
    def refresh_current_topic(self, session: InterviewSession) -> str:
        """현재 주제에 대해 새로운 질문 생성"""
        prompt = f"""
        당신은 {session.position} 개발자 면접관입니다.
        '{session.current_topic}' 주제에 대해 이전과 다른 새로운 질문을 생성해주세요.
        
        조건:
        1. 주니어 개발자 수준에 적합한 난이도
        2. 이전 질문과 중복되지 않는 새로운 관점
        3. 실무 경험을 파악할 수 있는 질문
        4. 자연스러운 한국어로 된 질문
        
        이전 질문들:
        {self._format_conversation_history(session.get_current_conversation())}
        """
        
        new_question = self.get_model_response(prompt)
        if new_question:
            # 이전 대화 초기화
            session.conversations[session.current_topic] = []
            # 새 질문 추가
            session.add_message('interviewer', new_question)
            return new_question
        
        return f"{session.current_topic}에 대해 다른 관점에서 설명해주시겠습니까?"
    
# React 컴포넌트 정의
EVALUATION_COMPONENT = """
// SVG Icons
const Check = ({ className = "h-4 w-4" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const AlertCircle = ({ className = "h-4 w-4" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

// Card Components
const Card = ({ children, className = "" }) => (
  <div className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = "" }) => (
  <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>
    {children}
  </div>
);

const CardTitle = ({ children, className = "" }) => (
  <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`}>
    {children}
  </h3>
);

const CardContent = ({ children, className = "" }) => (
  <div className={`p-6 pt-0 ${className}`}>
    {children}
  </div>
);

const AudioButton = ({ audioData, buttonText = "🔊 듣기" }) => {
  const playAudio = React.useCallback(() => {
    const audio = new Audio(`data:audio/mp3;base64,${audioData}`);
    audio.play().catch(error => console.error('Audio playback error:', error));
  }, [audioData]);

  return (
    <button
      onClick={playAudio}
      className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors inline-flex items-center gap-2"
    >
      <span>🔊</span>
      <span>{buttonText}</span>
    </button>
  );
};

const FeedbackSection = ({ feedback }) => {
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Card className="bg-white shadow-md">
        <CardHeader className="bg-blue-50/50 border-b">
          <CardTitle className="text-lg text-blue-800">답변 피드백</CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">이해도 평가</h4>
              <p className="text-gray-600">{feedback.understanding}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <div className="font-medium text-green-700 flex items-center gap-2">
                  <Check className="h-4 w-4" />
                  강점
                </div>
                <ul className="space-y-2">
                  {feedback.strengths.map((strength, idx) => (
                    strength && (
                      <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                        <span className="text-green-600 mt-1">•</span>
                        <span>{strength}</span>
                      </li>
                    )
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <div className="font-medium text-red-700 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  개선 필요
                </div>
                <ul className="space-y-2">
                  {feedback.improvements.map((improvement, idx) => (
                    improvement && (
                      <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                        <span className="text-red-600 mt-1">•</span>
                        <span>{improvement}</span>
                      </li>
                    )
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-700 mb-2">학습 제안</h4>
              <ul className="space-y-2">
                {feedback.suggestions.map((suggestion, idx) => (
                  suggestion && (
                    <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                      <span className="text-blue-600 mt-1">•</span>
                      <span>{suggestion}</span>
                    </li>
                  )
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const MessageBubble = ({ role, content, isLast = false }) => {
  const isInterviewer = role === 'interviewer';
  
  return (
    <div className={`flex ${isInterviewer ? 'justify-start' : 'justify-end'} mb-4`}>
      <div className={`
        max-w-[80%] px-4 py-2 rounded-lg
        ${isInterviewer ? 'bg-gray-100 text-gray-800' : 'bg-blue-500 text-white'}
      `}>
        {content}
      </div>
    </div>
  );
};

const ConversationView = ({ messages, feedback }) => {
  return (
    <div className="space-y-4">
      {messages.map((msg, idx) => (
        <MessageBubble 
          key={idx}
          role={msg.role}
          content={msg.content}
          isLast={idx === messages.length - 1}
        />
      ))}
      {feedback && <FeedbackSection feedback={feedback} />}
    </div>
  );
};

export { AudioButton, FeedbackSection, ConversationView };
"""

def get_api_key():
    """환경에 따라 적절한 방법으로 API 키를 가져옴"""
    try:
        # Streamlit Cloud의 secrets에서 가져오기 시도
        return st.secrets["GOOGLE_API_KEY"]
    except KeyError:
        # 로컬 환경에서는 직접 입력받기
        return st.text_input(
            "Google API 키를 입력하세요:",
            type="password",
            help="https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다"
        )
    
# 상단에 버전 정보 상수 추가
VERSION = "1.0.0"  # Semantic Versioning 사용
LAST_UPDATED = "2024-11-01"
VERSION_INFO = {
    "현재 버전": VERSION,
    "마지막 업데이트": LAST_UPDATED,
    "주요 기능": [
        "프론트엔드/백엔드/풀스택 직무 면접 지원",
        "Gemini Pro 기반 지능형 면접관",
        "실시간 피드백 및 개선점 제공",
        "주제별 심층 분석"
    ],
    "변경 이력": {
        "1.0.0": "최초 공개 버전",
        # 향후 업데이트 기록 추가
    }
}

def main():
    st.set_page_config(
        page_title="AI 면접 코치 - 개발자 기술면접 연습",
        page_icon="🤖",
        layout="wide",
        menu_items={
            'Get Help': "https://github.com/pg-Parunson/ai-interview-coach",
            'Report a bug': "https://github.com/pg-Parunson/ai-interview-coach/issues",
            'About': """
            ### AI 면접 코치 - LLM 기반 개발자 면접 시뮬레이터
            
            이 서비스는 개발자 취업 준비생을 위한 AI 기반 모의 면접 시스템입니다.
            
            - 💻 프론트엔드/백엔드/풀스택 직무 지원
            - 🤖 Gemini Pro 기반의 지능형 면접관
            - 📊 상세한 피드백과 개선점 제공
            
            **개발자:** 정재호 (a.k.a Jeff)
            **이메일:** iwogh3176@gmail.com
            **GitHub:** [pg-Parunson/ai-interview-coach](https://github.com/pg-Parunson/ai-interview-coach)
            
            *Last Updated: {LAST_UPDATED}*

            © 2024 AI Interview Coach. All rights reserved.
            """
        },
        initial_sidebar_state="auto"
    )
    
    st.title("🤖 AI 면접 코치 - 개발자 기술면접 연습")
    st.caption("🌱 면접 연습을 통해 더 나은 개발자로 성장하세요. 여러분의 도전을 응원합니다!")
    
    # 버전 정보를 사이드바에 표시
    with st.sidebar:
        st.write(f"### 📌 v{VERSION}")
        if st.button("릴리즈 노트 보기", key="release_notes"):
            with st.expander("상세 정보", expanded=True):
                st.write(f"**현재 버전:** v{VERSION}")
                st.write(f"**마지막 업데이트:** {LAST_UPDATED}")
                
                st.write("**주요 기능:**")
                for feature in VERSION_INFO["주요 기능"]:
                    st.write(f"- {feature}")
                
                st.write("**변경 이력:**")
                for version, changes in VERSION_INFO["변경 이력"].items():
                    st.write(f"- v{version}: {changes}")

    initialize_session()
    
    # Google API 키 설정
    api_key = get_api_key()
    if not api_key:
        st.warning("""
        Google API 키가 필요합니다.
        1. https://makersuite.google.com/app/apikey 에서 발급
        2. 발급받은 키를 입력해주세요
        """)
        return
            
    if 'interviewer' not in st.session_state:
        st.session_state.interviewer = MockInterviewer(api_key)
    
    session = st.session_state.session
    interviewer = st.session_state.interviewer

    # 포지션 선택
    if not session.position:
        st.write("### 지원하시는 포지션을 선택해주세요:")
        cols = st.columns(3)
        with cols[0]:
            if st.button("프론트엔드", key="frontend", use_container_width=True):
                session.position = "프론트엔드"
                st.rerun()
        with cols[1]:
            if st.button("백엔드", key="backend", use_container_width=True):
                session.position = "백엔드"
                st.rerun()
        with cols[2]:
            if st.button("풀스택", key="fullstack", use_container_width=True):
                session.position = "풀스택"
                st.rerun()
        return

    # 면접 진행 상태 표시
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"#### 선택하신 포지션: {session.position}")
        if session.current_topic:
            st.write(f"현재 주제: {session.current_topic}")
    with col2:
        completed = len(session.completed_topics)
        total = len(interviewer.position_topics[session.position])
        st.write(f"진행률: {completed}/{total} 주제 완료")

    # 면접 진행
    if not session.interview_complete:
        # 현재 주제가 없으면 새 주제 시작
        if not session.current_topic:
            next_topic = interviewer.get_next_topic(session)
            if next_topic:
                with st.spinner('다음 주제를 준비중입니다...'):
                    first_question = interviewer.start_topic(session, next_topic)
            else:
                session.interview_complete = True
                st.rerun()
                return
        
        # 현재 대화 표시
        st.write("---")
        if session.current_topic:
            render_conversation(session.get_current_conversation())  # current_conversation 대신 get_current_conversation() 사용

        # 컨트롤 버튼들 (주제 스킵, 면접 종료 등)
        cols = st.columns(3)
        with cols[0]:
            if st.button("⏩ 다른 주제로 넘어가기", type="secondary", help="현재 주제를 건너뛰고 새로운 주제로 이동"):
                session.clear_current_conversation()
                st.rerun()
        with cols[1]:
            if st.button("🔄 다른 질문 받기", type="secondary", help="현재 주제에서 다른 질문으로 변경"):
              if session.current_topic:
                  with st.spinner('새로운 질문을 준비중입니다...'):
                      new_question = interviewer.refresh_current_topic(session)
                  st.rerun()
              else:
                  st.warning("현재 진행 중인 주제가 없습니다.")
        with cols[2]:
            if st.button("🚫 면접 종료", type="secondary", help="면접을 종료하고 최종 평가 보기"):
              is_valid, message = session.validate_completion()
              if is_valid:
                  session.interview_complete = True
                  st.rerun()
              else:
                  st.error(f"면접을 종료할 수 없습니다: {message}")

        # 답변 입력 UI
        st.write("### 답변 입력")
        answer = st.text_area(
            label="답변을 입력하세요:",
            key="answer_input",
            height=150,
            placeholder="이 곳에 답변을 입력해주세요..."
        )

        # 답변 제출 버튼
        submit_button = st.button("답변 제출", key="submit_answer", type="primary", use_container_width=True)
        if submit_button:
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
                    st.session_state.current_answer = ''
                    
                    if response['type'] in ['follow_up', 'hint']:
                        st.rerun()
                    else:  # conclude
                        st.success("해당 주제에 대한 평가가 완료되었습니다.")
                        session.clear_current_conversation()
                        st.rerun()

    # 면접 완료 처리
    if session.interview_complete and not session.final_feedback:
        st.write("## 🎉 면접이 모두 완료되었습니다!")
        
        # 전체 대화 내역 수집
        with st.spinner('최종 평가를 작성중입니다...'):
            # 모든 주제의 대화 내용을 하나로 합치기
            all_conversations = []
            for topic in session.completed_topics:
                all_conversations.extend(session.conversations.get(topic, []))
                
            session.final_feedback = interviewer.generate_final_evaluation(
                session.completed_topics,
                all_conversations,  # 변경된 부분
                session.position
            )
            st.rerun()
            
    # 최종 평가 표시
    if session.final_feedback:
        st.write("## 📋 최종 면접 평가")
        st.markdown(session.final_feedback)
        
        # 면접 기록 다운로드 버튼
        st.write("### 💾 면접 기록 다운로드")
        
        txt_data = export_to_txt(session)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        position = session.position.replace('/', '_')
        filename = f"면접기록_{position}_{timestamp}.txt"
        
        st.download_button(
            label="📝 면접 기록 다운로드 (TXT)",
            data=txt_data.encode('utf-8'),
            file_name=filename,
            mime="text/plain",
            help="면접 내용을 텍스트 파일로 다운로드합니다. 대화 내용과 피드백을 쉽게 확인할 수 있습니다."
        )
        
        if st.button("새로운 면접 시작", key="new_interview", type="primary"):
            st.session_state.session = InterviewSession()
            st.session_state.submitted = False
            st.rerun()

if __name__ == "__main__":
    main()