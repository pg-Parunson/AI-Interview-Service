import json
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional
import streamlit as st

class FileStatisticsManager:
    """파일 기반 통계 관리자"""
    
    def __init__(self):
        self.stats_dir = Path(".streamlit/statistics")
        self.daily_stats_file = self.stats_dir / f"stats_{date.today()}.json"
        self.initialize_storage()

    def initialize_storage(self):
        """저장소 초기화"""
        try:
            self.stats_dir.mkdir(parents=True, exist_ok=True)
            if not self.daily_stats_file.exists():
                self._save_stats(self._get_default_stats())
        except Exception as e:
            st.warning(f"통계 저장소 초기화 중 오류 발생: {str(e)}")

    @staticmethod
    def _get_default_stats() -> Dict:
        """기본 통계 데이터 구조"""
        return {
            "total_interviews": 0,
            "completed_interviews": 0,
            "position_distribution": {
                "프론트엔드": 0,
                "백엔드": 0,
                "풀스택": 0
            },
            "success_count": 0,
            "last_updated": datetime.now().isoformat()
        }

    def _load_stats(self) -> Dict:
        """통계 데이터 로드"""
        try:
            if self.daily_stats_file.exists():
                with open(self.daily_stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._get_default_stats()
        except Exception as e:
            st.warning(f"통계 데이터 로드 중 오류 발생: {str(e)}")
            return self._get_default_stats()

    def _save_stats(self, stats: Dict):
        """통계 데이터 저장"""
        try:
            stats["last_updated"] = datetime.now().isoformat()
            with open(self.daily_stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.warning(f"통계 데이터 저장 중 오류 발생: {str(e)}")

    # 캐시 데코레이터를 클래스 메서드에 맞게 수정
    @staticmethod
    @st.cache_data(ttl=300)  # 5분간 캐시
    def _get_cached_stats(file_path: str) -> Dict:
        """캐시된 통계 데이터 반환"""
        try:
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return FileStatisticsManager._get_default_stats()

    def update_statistics(self, session) -> None:
        """면접 세션 완료 시 통계 업데이트"""
        stats = self._load_stats()
        
        # 전체 면접 수 증가
        stats["total_interviews"] += 1
        
        # 포지션 분포 업데이트
        if session.position:
            stats["position_distribution"][session.position] += 1
        
        # 완료된 면접 통계
        if session.interview_complete:
            stats["completed_interviews"] += 1
            
            # 성공 여부 확인 및 업데이트
            if self._check_session_success(session):
                stats["success_count"] += 1
        
        self._save_stats(stats)

    def get_statistics_summary(self) -> Dict:
        """통계 데이터 요약"""
        # 캐시된 통계 데이터 가져오기
        stats = self._get_cached_stats(str(self.daily_stats_file))
        
        # 비율 계산
        completion_rate = (
            (stats["completed_interviews"] / stats["total_interviews"] * 100)
            if stats["total_interviews"] > 0 else 0
        )
        
        success_rate = (
            (stats["success_count"] / stats["completed_interviews"] * 100)
            if stats["completed_interviews"] > 0 else 0
        )
        
        return {
            "total_interviews": stats["total_interviews"],
            "completion_rate": round(completion_rate, 1),
            "position_distribution": stats["position_distribution"],
            "success_rate": round(success_rate, 1)
        }

    def _check_session_success(self, session) -> bool:
        """면접 세션의 성공 여부 판단"""
        if not session.completed_topics or not session.final_feedback:
            return False
        
        total_score = 0
        num_scores = 0
        
        for topic, conversations in session.conversations.items():
            for msg in conversations:
                if msg.feedback and 'completion_score' in msg.feedback:
                    total_score += msg.feedback['completion_score']
                    num_scores += 1
        
        average_score = total_score / num_scores if num_scores > 0 else 0
        return average_score >= 4.0

    def cleanup_old_stats(self, days_to_keep: int = 30):
        """오래된 통계 파일 정리"""
        try:
            for stats_file in self.stats_dir.glob("stats_*.json"):
                file_date = date.fromisoformat(stats_file.stem.split('_')[1])
                if (date.today() - file_date).days > days_to_keep:
                    stats_file.unlink()
        except Exception as e:
            st.warning(f"오래된 통계 파일 정리 중 오류 발생: {str(e)}")