"""상수 및 설정값 정의"""

from typing import Dict, List

VERSION = "1.2.0"
LAST_UPDATED = "2024-11-02"

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
        "1.1.0": "내부 구조 리팩토링 및 모듈화 (기능 변화 없음)",
        "1.2.0": "면접자 통계 데이터 대시보드 추가"
    }
}

POSITION_TOPICS: Dict[str, List[str]] = {
    "프론트엔드": [
        "JavaScript/TypeScript 기초",
        "React/Vue/Angular 프레임워크",
        "HTML/CSS 및 웹 표준",
        "상태관리 및 성능 최적화",
        "웹 보안과 인증"
    ],
    "백엔드": [
        "주로 사용하는 개발 언어",
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

class UsageLimits:
    MAX_ANSWER_LENGTH = 3000  # 답변 최대 글자수
    MAX_TOPICS_PER_SESSION = 5  # 세션당 최대 주제 수
    MAX_RESPONSES_PER_TOPIC = 10  # 주제당 최대 답변 횟수