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

    def __init__(self, ollama_service):
        """
        Args:
            ollama_service: Ollama 서비스 인스턴스
        """
        self.ollama_service = ollama_service
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

            # LLM 호출
            response = await self.ollama_service.chat(
                model="llama3.2:latest",
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

태그 생성 규칙:
1. 텍스트의 핵심 주제와 카테고리를 나타내는 태그 선택
2. 구체적이고 의미있는 단어 사용
3. 중복되거나 유사한 태그 제외
4. {language_instruction}
5. 태그는 단일 단어 또는 짧은 구문 (2-3 단어)
6. 소문자 사용 (영어의 경우)

반드시 다음 JSON 형식으로만 응답하세요:
{{"tags": ["태그1", "태그2", "태그3"]}}

JSON만 반환하고 다른 설명은 포함하지 마세요.
"""
        return prompt

    def _parse_tag_response(self, response: str) -> List[str]:
        """LLM 응답에서 태그 추출"""
        try:
            # JSON 형식 찾기
            json_match = re.search(r'\{[\s\S]*"tags"[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("tags", [])

            # JSON 배열만 있는 경우
            array_match = re.search(r'\[[\s\S]*\]', response)
            if array_match:
                return json.loads(array_match.group())

            # 쉼표로 구분된 텍스트
            tags = [tag.strip(' "\',') for tag in response.split(',')]
            return [tag for tag in tags if tag]

        except Exception as e:
            logger.warning(f"Failed to parse tags from response: {e}")
            return []

    def _clean_tags(
        self,
        tags: List[str],
        max_tags: int,
        language: str
    ) -> List[str]:
        """태그 정제 및 필터링"""
        cleaned = []

        for tag in tags:
            # 기본 정제
            tag = tag.strip().lower()

            # 빈 태그 제외
            if not tag:
                continue

            # 특수문자 제거 (한글, 영문, 숫자, 하이픈, 언더스코어만 허용)
            tag = re.sub(r'[^\w\sㄱ-ㅎㅏ-ㅣ가-힣-]', '', tag)

            # 너무 짧거나 긴 태그 제외
            if len(tag) < 2 or len(tag) > 20:
                continue

            # 중복 제외
            if tag not in cleaned:
                cleaned.append(tag)

            # 최대 개수 도달
            if len(cleaned) >= max_tags:
                break

        return cleaned

    def _calculate_confidence(self, tags: List[str], content: str) -> float:
        """태그 신뢰도 계산"""
        if not tags:
            return 0.0

        # 간단한 신뢰도: 태그가 텍스트에 나타나는 비율
        content_lower = content.lower()
        matches = sum(1 for tag in tags if tag.lower() in content_lower)

        confidence = matches / len(tags) if tags else 0.0

        # 태그 개수에 따른 가중치
        if len(tags) >= 3:
            confidence = min(confidence + 0.1, 1.0)

        return round(confidence, 2)

    def _fallback_tag_extraction(self, content: str, max_tags: int) -> List[str]:
        """폴백: 간단한 키워드 추출"""
        # 불용어 제거 및 키워드 추출 (매우 간단한 구현)
        stopwords = {
            'ko': {'은', '는', '이', '가', '을', '를', '에', '의', '와', '과', '도', '만', '까지', '입니다', '습니다'},
            'en': {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'}
        }

        words = re.findall(r'\b\w+\b', content.lower())

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

        tags_with_stats = [
            {
                "tag": tag,
                "count": count,
                "last_used": None  # DB에서 가져와야 함
            }
            for tag, count in sorted(
                user_tags.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
        ]

        return tags_with_stats

    async def autocomplete_tags(
        self,
        prefix: str,
        user_id: str,
        limit: int = 10
    ) -> List[str]:
        """
        태그 자동완성

        Args:
            prefix: 태그 접두사
            user_id: 사용자 ID
            limit: 결과 개수

        Returns:
            List[str]: 자동완성 제안
        """
        # TODO: 실제 DB에서 조회
        # 현재는 캐시에서 필터링 (예시)
        user_tags = self.tag_cache.get(user_id, {})

        prefix_lower = prefix.lower()
        matching_tags = [
            tag for tag in user_tags.keys()
            if tag.lower().startswith(prefix_lower)
        ]

        # 빈도순 정렬
        matching_tags.sort(key=lambda t: user_tags[t], reverse=True)

        return matching_tags[:limit]

    def record_tag_usage(self, user_id: str, tags: List[str]):
        """태그 사용 기록 (캐시 업데이트)"""
        if user_id not in self.tag_cache:
            self.tag_cache[user_id] = {}

        for tag in tags:
            self.tag_cache[user_id][tag] = self.tag_cache[user_id].get(tag, 0) + 1


# 싱글톤 인스턴스 생성을 위한 팩토리 함수
_tag_service_instance = None


def get_tag_service(ollama_service) -> TagService:
    """TagService 싱글톤 인스턴스 반환"""
    global _tag_service_instance
    if _tag_service_instance is None:
        _tag_service_instance = TagService(ollama_service)
    return _tag_service_instance
