from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class InterviewStatistics:
    """면접 통계 데이터 모델"""
    total_interviews: int = 0
    completed_interviews: int = 0
    position_distribution: Dict[str, int] = None
    success_count: int = 0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.position_distribution is None:
            self.position_distribution = {
                "프론트엔드": 0,
                "백엔드": 0,
                "풀스택": 0
            }
        if self.last_updated is None:
            self.last_updated = datetime.now()