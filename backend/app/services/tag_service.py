"""
태그 자동 생성 및 관리 서비스
"""
from typing import List, Dict, Optional
import json
import re
import logging

logger = logging.getLogger(__name__)


class TagService:
    """태그 생성 및 관리 서비스"""

    def __init__(self, ollama_service, default_model: str = "llama3.2:latest"):
        """
        Args:
            ollama_service: Ollama 서비스 인스턴스
            default_model: 태그 생성에 사용할 기본 LLM 모델
        """
        self.ollama_service = ollama_service
        self.default_model = default_model
        self.tag_cache = {}  # 태그 빈도 캐시 (실제로는 DB 사용)

    async def suggest_tags(
        self,
        content: str,
        max_tags: int = 5,
        language: str = "auto"
    ) -> Dict[str, any]:
        """
        텍스트 내용을 분석하여 적절한 태그 제안

        Args:
            content: 분석할 텍스트
            max_tags: 최대 태그 개수
            language: 태그 언어 (auto, ko, en)

        Returns:
            Dict: {"tags": [...], "confidence": 0.0-1.0}
        """
        try:
            # 언어별 프롬프트 구성
            prompt = self._build_tag_generation_prompt(content, max_tags, language)

            # LLM 호출 (설정된 모델 사용)
            response = await self.ollama_service.chat(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates relevant tags for text content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # 응답 파싱
            tags = self._parse_tag_response(response["message"]["content"])

            # 태그 정제
            tags = self._clean_tags(tags, max_tags, language)

            logger.info(f"Generated {len(tags)} tags for content: {content[:50]}...")

            return {
                "tags": tags,
                "confidence": self._calculate_confidence(tags, content)
            }

        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            # 폴백: 간단한 키워드 추출
            return {
                "tags": self._fallback_tag_extraction(content, max_tags),
                "confidence": 0.5
            }

    def _build_tag_generation_prompt(
        self,
        content: str,
        max_tags: int,
        language: str
    ) -> str:
        """태그 생성 프롬프트 구성"""

        language_instruction = {
            "ko": "태그는 한글로 작성하세요.",
            "en": "Tags should be in English.",
            "auto": "태그는 텍스트의 주 언어로 작성하세요. (Use the main language of the text for tags)"
        }.get(language, "")

        prompt = f"""
다음 텍스트를 분석하여 가장 관련성 높은 태그 {max_tags}개를 생성하세요.

텍스트:
\"\"\"
{content}
\"\"\"

요구사항:
1. 태그는 단어나 짧은 구절로 작성
2. 가장 중요하고 관련성 높은 개념 추출
3. 중복 피하기
4. {language_instruction}

JSON 형식으로 답변:
{{"tags": ["태그1", "태그2", "태그3"]}}

JSON만 반환하고 다른 설명은 포함하지 마세요.
"""
        return prompt.strip()

    def _parse_tag_response(self, response: str) -> List[str]:
        """LLM 응답에서 태그 파싱"""
        try:
            # JSON 파싱 시도
            if "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return data.get("tags", [])

            # 배열 파싱 시도
            if "[" in response and "]" in response:
                array_start = response.find("[")
                array_end = response.rfind("]") + 1
                array_str = response[array_start:array_end]
                return json.loads(array_str)

            # 줄바꿈으로 구분된 태그
            lines = [line.strip() for line in response.split("\n")]
            tags = []
            for line in lines:
                # 번호 매겨진 항목 제거 (1. 태그, - 태그 등)
                cleaned = re.sub(r"^[\d\-\*\.]+\s*", "", line)
                cleaned = cleaned.strip("\"'[](){}")
                if cleaned and len(cleaned) > 1:
                    tags.append(cleaned)

            return tags[:10]  # 최대 10개까지만

        except Exception as e:
            logger.warning(f"Failed to parse tag response: {e}")
            return []

    def _clean_tags(
        self,
        tags: List[str],
        max_tags: int,
        language: str
    ) -> List[str]:
        """태그 정제 및 정규화"""
        cleaned = []

        for tag in tags:
            # 공백 제거 및 소문자 변환
            tag = tag.strip().lower()

            # 특수문자 제거 (한글, 영문, 숫자, 공백만 허용)
            tag = re.sub(r'[^\w\sㄱ-힣]', '', tag, flags=re.UNICODE)

            # 너무 길거나 짧은 태그 제외
            if 2 <= len(tag) <= 30 and tag not in cleaned:
                cleaned.append(tag)

            if len(cleaned) >= max_tags:
                break

        return cleaned

    def _calculate_confidence(self, tags: List[str], content: str) -> float:
        """태그 신뢰도 계산"""
        if not tags:
            return 0.0

        # 간단한 휴리스틱: 태그가 원문에 포함되어 있는지 확인
        content_lower = content.lower()
        matches = sum(1 for tag in tags if tag.lower() in content_lower)

        return min(0.5 + (matches / len(tags)) * 0.5, 1.0)

    def _fallback_tag_extraction(self, content: str, max_tags: int) -> List[str]:
        """LLM 실패 시 간단한 키워드 추출"""
        # 간단한 단어 분리
        words = re.findall(r'\b[\w가-힣]+\b', content.lower(), re.UNICODE)

        # 불용어 제거 (간단한 예시)
        stopwords = {
            'ko': {'이', '그', '저', '것', '수', '등', '및', '를', '을', '가', '이', '은', '는', '에', '의', '와', '과'},
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        }

        # 불용어 제거
        all_stopwords = stopwords['ko'] | stopwords['en']
        keywords = [w for w in words if w not in all_stopwords and len(w) > 2]

        # 빈도수 계산
        from collections import Counter
        word_freq = Counter(keywords)

        # 상위 키워드 반환
        return [word for word, _ in word_freq.most_common(max_tags)]

    async def get_popular_tags(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """
        사용자의 인기 태그 조회

        Args:
            user_id: 사용자 ID
            limit: 결과 개수

        Returns:
            List[Dict]: [{"tag": "...", "count": N, "last_used": "..."}]
        """
        # TODO: 실제 DB에서 조회
        # 현재는 캐시에서 반환 (예시)
        user_tags = self.tag_cache.get(user_id, {})

        sorted_tags = sorted(
            user_tags.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]

        return [
            {
                "tag": tag,
                "count": data["count"],
                "last_used": data.get("last_used", "")
            }
            for tag, data in sorted_tags
        ]

    async def autocomplete_tags(
        self,
        prefix: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[str]:
        """
        태그 자동완성

        Args:
            prefix: 검색할 접두어
            user_id: 사용자 ID (선택사항)
            limit: 결과 개수

        Returns:
            List[str]: 추천 태그 목록
        """
        # TODO: 실제 DB에서 조회
        # 현재는 캐시에서 검색 (예시)
        all_tags = set()

        if user_id and user_id in self.tag_cache:
            all_tags.update(self.tag_cache[user_id].keys())

        # 전체 캐시에서도 검색
        for tags_dict in self.tag_cache.values():
            all_tags.update(tags_dict.keys())

        # 접두어 매칭
        prefix_lower = prefix.lower()
        matching_tags = [
            tag for tag in all_tags
            if tag.lower().startswith(prefix_lower)
        ]

        return sorted(matching_tags)[:limit]


# 싱글톤 인스턴스 생성을 위한 팩토리 함수
_tag_service_instance = None


def get_tag_service(ollama_service, default_model: str = "llama3.2:latest") -> TagService:
    """TagService 싱글톤 인스턴스 반환"""
    global _tag_service_instance
    if _tag_service_instance is None:
        _tag_service_instance = TagService(
            ollama_service=ollama_service,
            default_model=default_model
        )
    return _tag_service_instance
