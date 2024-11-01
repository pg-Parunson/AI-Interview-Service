"""환경 설정 및 구성 관리"""

import os
from typing import Optional
import streamlit as st
from pathlib import Path

def is_streamlit_cloud() -> bool:
    """Streamlit Cloud 환경인지 확인"""
    return os.getenv('STREAMLIT_RUNTIME_ENV') == 'cloud'

def get_api_key() -> Optional[str]:
    """환경에 따른 API 키 반환"""
    # 1. Streamlit Cloud - Secrets 사용
    if is_streamlit_cloud():
        return st.secrets.get("GOOGLE_API_KEY")
    
    # 2. 로컬 개발 환경
    # 2.1 .streamlit/secrets.toml 체크
    secrets_path = Path('.streamlit/secrets.toml')
    if secrets_path.exists():
        try:
            return st.secrets["GOOGLE_API_KEY"]
        except KeyError:
            pass
    
    # 2.2 환경 변수 체크
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        return api_key
    
    # 2.3 사용자 입력 요청
    return st.text_input(
        "Google API 키를 입력하세요:",
        type="password",
        help="""
        로컬 개발 환경에서는 다음 방법 중 하나로 API 키를 설정할 수 있습니다:
        1. .streamlit/secrets.toml 파일에 GOOGLE_API_KEY="your-key" 추가
        2. 환경 변수 GOOGLE_API_KEY 설정
        3. 위 입력창에 직접 입력
        
        API 키 발급: https://makersuite.google.com/app/apikey
        """
    )

class Settings:
    """전역 설정 관리"""
    
    # 환경 설정
    ENV = 'production' if is_streamlit_cloud() else 'development'
    DEBUG = not is_streamlit_cloud()
    
    # 음성 기능 활성화 여부
    ENABLE_SPEECH = False
    try:
        import speech_recognition as sr
        ENABLE_SPEECH = True
    except ImportError:
        pass
    
    # Streamlit 페이지 설정
    PAGE_CONFIG = {
        "page_title": "AI 면접 코치 - 개발자 기술면접 연습",
        "page_icon": "🤖",
        "layout": "wide",
        "initial_sidebar_state": "auto",
    }
    
    # 메뉴 아이템 설정
    MENU_ITEMS = {
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
        """
    }