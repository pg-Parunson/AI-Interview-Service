"""평가 관련 프롬프트 템플릿"""

from typing import List

class EvaluationPrompts:
    """평가 생성 관련 프롬프트"""
    
    @staticmethod
    def topic_feedback(position: str, topic: str, conversation_history: str) -> str:
        """주제별 피드백 생성 프롬프트"""
        return f"""
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

    @staticmethod
    def final_evaluation(position: str, completed_topics: List[str], conversation_history: str) -> str:
        """최종 평가 생성 프롬프트"""
        topics_text = ', '.join(completed_topics) if completed_topics else '없음'
        
        return f"""
        당신은 {position} 개발자 면접관입니다.
        지원자와 나눈 실제 대화 내용만을 바탕으로 객관적인 평가를 진행해주세요.
        
        진행된 주제: {topics_text}
        
        평가 작성 시 주의사항:
        1. 실제 대화에서 나온 내용만 평가해주세요
        2. 답변이 부족한 부분은 명확히 지적해주세요
        3. 보여준 강점은 구체적으로 언급해주세요
        4. 실제 답변에 기반한 개선점을 제시해주세요
        5. 과대평가나 과소평가를 피해주세요
        
        대화 내역:
        {conversation_history}
        """

    @staticmethod
    def get_empty_evaluation_message() -> str:
        """답변이 없는 경우의 메시지"""
        return """
        면접이 진행되지 않았거나 답변이 기록되지 않았습니다.
        
        더 나은 피드백을 받기 위해서는:
        1. 면접관의 질문에 답변을 해주세요
        2. 구체적인 예시나 경험을 포함하여 답변해주세요
        3. 여러 주제에 대해 면접을 진행해보세요
        
        다시 면접에 도전해보시겠습니까?
        """