"""데이터 내보내기 유틸리티"""

from datetime import datetime
from typing import List

from ..core.session import InterviewSession
from ..core.models import Conversation

class InterviewExporter:
    """면접 데이터 내보내기"""
    
    @staticmethod
    def to_txt(session: InterviewSession) -> str:
        """면접 내용을 텍스트 형식으로 변환"""
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
        
        # 주제별 대화 내용
        for topic in session.completed_topics:
            lines.extend(InterviewExporter._format_topic_conversation(topic, session.conversations.get(topic, [])))
        
        # 최종 평가
        if session.final_feedback:
            lines.extend([
                "📋 최종 평가",
                "=" * 50,
                session.final_feedback,
                "=" * 50
            ])
        
        return '\n'.join(lines)

    @staticmethod
    def _format_topic_conversation(topic: str, conversations: List[Conversation]) -> List[str]:
        """주제별 대화 내용 포맷팅"""
        lines = [
            f"[주제] {topic}",
            "-" * 50,
            ""
        ]
        
        for msg in conversations:
            timestamp = msg.timestamp.strftime('%H:%M:%S')
            role = '👤 면접관' if msg.role == 'interviewer' else '🧑‍💻 지원자'
            
            lines.extend([
                f"[{timestamp}] {role}:",
                msg.content,
                ""
            ])
            
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
            ""
        ])
        
        return lines