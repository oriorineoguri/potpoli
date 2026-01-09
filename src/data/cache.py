"""
데이터 캐싱 모듈

API 호출을 최소화하고 성능을 향상시키기 위한 캐시 시스템입니다.

Note:
    - API Rate Limit 준수를 위해 캐시 사용 필수
    - 재무제표는 분기별로 변경되므로 캐시 TTL 길게 설정 가능
    - 주가는 실시간성이 중요하므로 캐시 TTL 짧게 설정
"""

import logging
import json
import os
from typing import Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class DataCache:
    """
    파일 기반 데이터 캐시

    데이터를 JSON 파일로 저장하여 API 호출을 최소화합니다.

    **캐시 정책:**
    - 주가 데이터: TTL 1시간 (실시간성 중요)
    - 재무제표: TTL 24시간 (하루 1회 갱신)
    - 컨센서스: TTL 12시간 (반나절 1회 갱신)
    """

    def __init__(self, cache_dir: str = "./data/cache"):
        """
        Args:
            cache_dir: 캐시 파일 저장 디렉토리
        """
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"DataCache 초기화: {self._cache_dir}")

    def get(
        self,
        key: str,
        ttl_seconds: int = 3600
    ) -> Optional[Any]:
        """
        캐시에서 데이터 조회

        Args:
            key: 캐시 키 (예: "stock_price_005930_20240101")
            ttl_seconds: 캐시 유효시간 (초)

        Returns:
            캐시된 데이터 (만료 or 없으면 None)

        Examples:
            >>> cache = DataCache()
            >>> data = cache.get("test_key", ttl_seconds=60)
        """
        cache_file = self._get_cache_file_path(key)

        # 캐시 파일이 없으면 None
        if not cache_file.exists():
            logger.debug(f"캐시 미스: {key}")
            return None

        # 캐시 파일 읽기
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # TTL 체크
            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            elapsed = (datetime.now() - cached_time).total_seconds()

            if elapsed > ttl_seconds:
                logger.debug(f"캐시 만료: {key} (경과시간: {elapsed:.0f}초)")
                # 만료된 캐시 파일 삭제
                cache_file.unlink()
                return None

            logger.info(f"캐시 히트: {key} (남은시간: {ttl_seconds - elapsed:.0f}초)")
            return cache_data["data"]

        except Exception as e:
            logger.error(f"캐시 읽기 실패: {key} - {e}")
            return None

    def set(
        self,
        key: str,
        data: Any
    ) -> bool:
        """
        데이터를 캐시에 저장

        Args:
            key: 캐시 키
            data: 저장할 데이터 (JSON 직렬화 가능해야 함)

        Returns:
            성공 여부

        Examples:
            >>> cache = DataCache()
            >>> cache.set("test_key", {"value": 123})
            True
        """
        cache_file = self._get_cache_file_path(key)

        try:
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "key": key,
                "data": data
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"캐시 저장: {key}")
            return True

        except Exception as e:
            logger.error(f"캐시 저장 실패: {key} - {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        캐시 삭제

        Args:
            key: 캐시 키

        Returns:
            성공 여부
        """
        cache_file = self._get_cache_file_path(key)

        try:
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"캐시 삭제: {key}")
                return True
            else:
                logger.warning(f"캐시 없음: {key}")
                return False

        except Exception as e:
            logger.error(f"캐시 삭제 실패: {key} - {e}")
            return False

    def clear_all(self) -> int:
        """
        모든 캐시 삭제

        Returns:
            삭제된 캐시 파일 개수
        """
        try:
            cache_files = list(self._cache_dir.glob("*.json"))
            count = 0

            for cache_file in cache_files:
                cache_file.unlink()
                count += 1

            logger.info(f"전체 캐시 삭제: {count}개 파일")
            return count

        except Exception as e:
            logger.error(f"캐시 전체 삭제 실패: {e}")
            return 0

    def clear_expired(self, ttl_seconds: int = 86400) -> int:
        """
        만료된 캐시만 삭제

        Args:
            ttl_seconds: 유효시간 기준 (기본: 24시간)

        Returns:
            삭제된 캐시 파일 개수
        """
        try:
            cache_files = list(self._cache_dir.glob("*.json"))
            count = 0
            now = datetime.now()

            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)

                    cached_time = datetime.fromisoformat(cache_data["timestamp"])
                    elapsed = (now - cached_time).total_seconds()

                    if elapsed > ttl_seconds:
                        cache_file.unlink()
                        count += 1

                except Exception as e:
                    logger.warning(f"캐시 파일 처리 실패: {cache_file.name} - {e}")
                    continue

            logger.info(f"만료된 캐시 삭제: {count}개 파일")
            return count

        except Exception as e:
            logger.error(f"만료 캐시 삭제 실패: {e}")
            return 0

    def _get_cache_file_path(self, key: str) -> Path:
        """
        캐시 키로부터 파일 경로 생성

        Args:
            key: 캐시 키

        Returns:
            캐시 파일 경로
        """
        # 파일 시스템 안전한 파일명 생성
        safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self._cache_dir / f"{safe_key}.json"

    def get_cache_size(self) -> int:
        """
        캐시 디렉토리 크기 조회 (바이트)

        Returns:
            총 캐시 크기 (바이트)
        """
        try:
            total_size = sum(
                f.stat().st_size
                for f in self._cache_dir.glob("*.json")
            )
            logger.info(f"캐시 크기: {total_size / 1024:.2f} KB")
            return total_size

        except Exception as e:
            logger.error(f"캐시 크기 조회 실패: {e}")
            return 0

    def get_cache_count(self) -> int:
        """
        캐시 파일 개수 조회

        Returns:
            캐시 파일 개수
        """
        try:
            count = len(list(self._cache_dir.glob("*.json")))
            logger.info(f"캐시 파일 개수: {count}개")
            return count

        except Exception as e:
            logger.error(f"캐시 개수 조회 실패: {e}")
            return 0
