"""음성 관련 유틸리티"""

import base64
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st
from gtts import gTTS

from ..config.settings import Settings

class AudioProcessor:
    """음성 처리 기능"""
    
    @staticmethod
    def text_to_speech(text: str) -> Optional[str]:
        """텍스트를 음성으로 변환하고 base64 인코딩된 문자열을 반환"""
        if not text:
            return None
            
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts = gTTS(text=text, lang='ko', slow=False)
                tts.save(fp.name)
                with open(fp.name, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    return base64.b64encode(audio_bytes).decode()
        except Exception as e:
            st.error(f"음성 변환 중 오류가 발생했습니다: {str(e)}")
            return None
        finally:
            if 'fp' in locals():
                Path(fp.name).unlink(missing_ok=True)

    @staticmethod
    def speech_to_text() -> Optional[str]:
        """마이크로부터 음성을 입력받아 텍스트로 변환"""
        if not Settings.ENABLE_SPEECH:
            st.error("음성 인식 기능을 사용할 수 없습니다.")
            return None
            
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("말씀해주세요...")
                audio = recognizer.listen(source)
                return recognizer.recognize_google(audio, language='ko-KR')
        except Exception as e:
            st.error(f"음성 인식 중 오류가 발생했습니다: {str(e)}")
            return None