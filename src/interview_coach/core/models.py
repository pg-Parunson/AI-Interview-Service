"""핵심 데이터 모델 정의"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

@dataclass
class Conversation:
    """대화 내용을 저장하는 모델"""
    role: str  # 'interviewer' 또는 'candidate'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    feedback: Optional[Dict] = None

@dataclass
class InterviewFeedback:
    """면접 답변에 대한 피드백 모델"""
    understanding: str
    strengths: list[str]
    improvements: list[str]
    suggestions: list[str]

@dataclass
class AnswerAnalysis:
    """답변 분석 결과 모델"""
    action: str  # 'FOLLOW_UP', 'HINT', 'CONCLUDE' 중 하나
    completion_score: int  # 1-5 사이의 점수
    next_response: str
    feedback: Optional[str] = None