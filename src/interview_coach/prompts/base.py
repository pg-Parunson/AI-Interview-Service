"""프롬프트 기본 클래스 정의"""

from abc import ABC, abstractmethod
from typing import Any

class PromptTemplate(ABC):
    """프롬프트 템플릿 기본 클래스"""
    
    @abstractmethod
    def format(self, **kwargs: Any) -> str:
        """프롬프트 템플릿 포맷팅"""
        pass

    @classmethod
    def _clean_text(cls, text: str) -> str:
        """템플릿 텍스트 정리"""
        return '\n'.join(line.strip() for line in text.strip().split('\n'))