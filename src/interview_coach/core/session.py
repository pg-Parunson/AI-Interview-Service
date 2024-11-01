"""면접 세션 관리"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from .models import Conversation
from ..config.constants import POSITION_TOPICS

@dataclass
class InterviewSession:
    """면접 세션 상태 관리"""
    
    position: Optional[str] = None
    current_topic: Optional[str] = None
    conversations: Dict[str, List[Conversation]] = field(default_factory=dict)
    completed_topics: List[str] = field(default_factory=list)
    waiting_for_next: bool = False
    interview_complete: bool = False
    final_feedback: Optional[str] = None

    def add_message(self, role: str, content: str, feedback: Optional[Dict] = None) -> None:
        """대화 내용을 현재 주제에 저장"""
        if self.current_topic not in self.conversations:
            self.conversations[self.current_topic] = []
            
        new_message = Conversation(role=role, content=content, feedback=feedback)
        self.conversations[self.current_topic].append(new_message)

    def get_current_conversation(self) -> List[Conversation]:
        """현재 주제의 대화 내용 반환"""
        return self.conversations.get(self.current_topic, [])

    def clear_current_conversation(self) -> None:
        """주제 완료 처리"""
        if self.current_topic:
            self.completed_topics.append(self.current_topic)
        self.current_topic = None

    def get_all_conversations(self) -> List[Conversation]:
        """모든 대화 내용을 하나의 리스트로 반환"""
        all_conversations = []
        for topic in self.completed_topics:
            all_conversations.extend(self.conversations.get(topic, []))
        return all_conversations

    def get_remaining_topics(self) -> List[str]:
        """남은 주제 목록 반환"""
        if not self.position:
            return []
        return [
            topic for topic in POSITION_TOPICS[self.position]
            if topic not in self.completed_topics
        ]

    def reset(self) -> None:
        """세션 초기화"""
        self.position = None
        self.current_topic = None
        self.conversations.clear()
        self.completed_topics.clear()
        self.waiting_for_next = False
        self.interview_complete = False
        self.final_feedback = None