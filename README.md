# 🤖 AI 면접 코치 - LLM 기반 개발자 면접 시뮬레이터

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-interview-service-uzyraeqymsdzsasxpa8ies.streamlit.app)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

AI 면접 코치는 개발자 취업 준비생을 위한 AI 기반 모의 면접 시스템입니다. Google의 Gemini Pro를 활용하여 실제 기술 면접과 유사한 환경을 제공하며, 답변에 대한 즉각적인 피드백과 개선점을 제시합니다.

## 📌 주요 기능

- **다양한 직무 지원**: 프론트엔드, 백엔드, 풀스택 개발자 포지션별 맞춤 면접
- **실시간 피드백**: 답변에 대한 즉각적인 평가 및 개선점 제시
- **주제별 심층 분석**: 각 기술 주제별 이해도와 실무 적용 능력 평가
- **맞춤형 학습 제안**: 부족한 부분에 대한 구체적인 학습 방향 제시
- **상세한 최종 평가**: 전체 면접 과정에 대한 종합적인 피드백 제공

## 🚀 시작하기

### 온라인 데모
- [AI 면접 코치 바로가기](https://ai-interview-coach.streamlit.app)

### 로컬 설치 및 실행

1. **저장소 클론**
```bash
git clone https://github.com/pg-Parunson/ai-interview-coach.git
cd ai-interview-coach
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **환경 설정**
- `.streamlit/secrets.toml` 파일 생성
```toml
GOOGLE_API_KEY = "your-api-key-here"
```

4. **애플리케이션 실행**
```bash
streamlit run interview_app.py
```

## 💡 사용 방법

1. **포지션 선택**
   - 프론트엔드, 백엔드, 풀스택 중 선택

2. **면접 진행**
   - 주어진 질문에 답변 입력
   - 실시간 피드백 확인
   - 필요시 다음 주제로 이동

3. **피드백 확인**
   - 답변별 상세 피드백
   - 주제별 종합 평가
   - 최종 면접 결과

## 🔧 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **AI Model**: Google Gemini Pro
- **Dependencies**:
  - streamlit==1.31.0
  - google-generativeai==0.3.2
  - gTTS==2.5.0
  - python-dotenv==1.0.1

## 📋 면접 주제

### 프론트엔드
- JavaScript/TypeScript 기초
- React/Vue/Angular 프레임워크
- HTML/CSS 및 웹 표준
- 상태관리 및 성능 최적화
- 웹 보안과 인증

### 백엔드
- 주로 사용하는 개발 언어
- 서버 아키텍처 설계
- 데이터베이스 설계 및 최적화
- API 설계 및 보안
- 캐싱 및 성능 최적화
- 마이크로서비스 아키텍처

### 풀스택
- 프론트엔드 프레임워크
- 백엔드 아키텍처
- 데이터베이스 및 캐싱
- DevOps 및 배포
- 시스템 설계

## 📝 추가 정보

### 피드백 구조
- **이해도 평가**: 개념 이해도 및 실무 적용 능력 분석
- **강점**: 2-3가지 구체적인 장점
- **개선 필요**: 2-3가지 보완점
- **학습 제안**: 구체적인 학습 방향

### 사용 제한
- 답변 최대 길이: 500자
- 세션당 최대 주제 수: 3개
- 주제당 최대 답변 횟수: 3회

## 🤝 기여하기

프로젝트 개선에 기여하고 싶으시다면:
1. 이슈 생성
2. 풀 리퀘스트 제출
3. 버그 리포트 작성

## 📜 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## ✨ 크레딧

개발: 정재호 (iwogh3176@gmail.com)

---

질문이나 제안사항이 있으시다면 언제든 연락 주세요! 😊