#!/usr/bin/env python3
"""
mem0 Fact Extraction 테스트

정리되지 않은 텍스트를 mem0에 넣으면 어떻게 자동으로
분류하고 저장하는지 확인하는 스크립트
"""

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.configs.llms.base import LlmConfig
from mem0.configs.embedders.base import EmbedderConfig
from mem0.configs.vector_stores.base import VectorStoreConfig
import json

def test_mem0_extraction():
    """mem0의 자동 fact extraction 테스트"""

    print("=" * 60)
    print("mem0 Fact Extraction 테스트")
    print("=" * 60)
    print()

    # mem0 초기화
    print("📦 mem0 초기화 중...")
    config = MemoryConfig(
        llm=LlmConfig(
            provider="ollama",
            config={
                "model": "llama3.2:latest",
                "base_url": "http://localhost:11434"
            }
        ),
        embedder=EmbedderConfig(
            provider="ollama",
            config={
                "model": "nomic-embed-text:latest",
                "base_url": "http://localhost:11434"
            }
        ),
        vector_store=VectorStoreConfig(
            provider="qdrant",
            config={
                "path": "./test_qdrant_data",
                "collection_name": "test_memories"
            }
        ),
        history_db_path="./test_history.db"
    )

    memory = Memory(config=config)
    print("✅ mem0 초기화 완료\n")

    # 테스트 1: 정리되지 않은 긴 텍스트
    print("=" * 60)
    print("테스트 1: 정리되지 않은 긴 텍스트")
    print("=" * 60)

    unstructured_text = """
    안녕하세요. 제 이름은 김철수이고 서울에 살고 있습니다.
    저는 파이썬 개발자로 5년째 일하고 있고요, FastAPI랑 Django를 주로 사용합니다.
    회사는 강남에 있어요. 취미는 등산이고 주말마다 북한산에 갑니다.
    최근에 머신러닝 공부를 시작했는데 흥미롭네요.
    아, 그리고 고양이 두 마리를 키우고 있습니다.
    좋아하는 음식은 피자이고, 주로 주말에 친구들과 같이 먹습니다.
    요즘 건강을 위해 운동도 시작했어요. 헬스장에 주 3회 다니고 있습니다.
    """

    print("\n📝 입력 텍스트:")
    print("-" * 60)
    print(unstructured_text.strip())
    print("-" * 60)
    print()

    print("🤖 mem0가 분석 중... (LLM이 fact를 추출하는 중)")
    result = memory.add(
        messages=[{"role": "user", "content": unstructured_text}],
        user_id="test_user_1"
    )

    print("\n✨ 추출된 Memories:")
    print("=" * 60)
    if result and 'results' in result:
        for i, mem in enumerate(result['results'], 1):
            print(f"{i}. ID: {mem.get('id', 'N/A')}")
            print(f"   Memory: {mem.get('memory', mem.get('content', 'N/A'))}")
            print(f"   Event: {mem.get('event', 'N/A')}")
            print()
    else:
        print("결과:", json.dumps(result, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("테스트 2: 다른 형식의 텍스트")
    print("=" * 60)

    meeting_notes = """
    2025년 11월 5일 회의록

    참석자: 김철수, 박영희, 이민수
    주제: Q4 프로젝트 계획

    - 새로운 AI 챗봇 프로젝트 시작 결정
    - 기술 스택: Python, FastAPI, mem0, Ollama
    - 예산: 5000만원
    - 기간: 3개월 (11월~1월)
    - 담당자: 김철수(백엔드), 박영희(프론트엔드), 이민수(DevOps)
    - 다음 회의: 11월 12일 오후 2시

    기타 사항:
    - 팀 워크샵 12월 예정
    - 신입 개발자 채용 진행 중
    """

    print("\n📝 입력 텍스트:")
    print("-" * 60)
    print(meeting_notes.strip())
    print("-" * 60)
    print()

    print("🤖 mem0가 분석 중...")
    result2 = memory.add(
        messages=[{"role": "user", "content": meeting_notes}],
        user_id="test_user_2",
        metadata={"type": "meeting_notes", "date": "2025-11-05"}
    )

    print("\n✨ 추출된 Memories:")
    print("=" * 60)
    if result2 and 'results' in result2:
        for i, mem in enumerate(result2['results'], 1):
            print(f"{i}. ID: {mem.get('id', 'N/A')}")
            print(f"   Memory: {mem.get('memory', mem.get('content', 'N/A'))}")
            print(f"   Event: {mem.get('event', 'N/A')}")
            print()
    else:
        print("결과:", json.dumps(result2, indent=2, ensure_ascii=False))

    # 검색 테스트
    print("\n" + "=" * 60)
    print("테스트 3: 메모리 검색")
    print("=" * 60)

    queries = [
        "김철수의 직업은?",
        "취미가 뭐지?",
        "프로젝트 예산은?"
    ]

    for query in queries:
        print(f"\n🔍 질문: {query}")
        results = memory.search(query=query, user_id="test_user_1", limit=3)
        print("   답변 가능한 메모리:")
        for mem in results[:3]:
            print(f"   - {mem.get('memory', mem.get('content', 'N/A'))} (score: {mem.get('score', 0):.2f})")

    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print("\n요약:")
    print("- mem0는 정리되지 않은 텍스트를 자동으로 분석합니다")
    print("- LLM이 중요한 사실(fact)들을 추출합니다")
    print("- 각 사실은 독립적인 메모리로 저장됩니다")
    print("- 나중에 의미론적 검색으로 관련 정보를 찾을 수 있습니다")
    print()

if __name__ == "__main__":
    try:
        test_mem0_extraction()
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        print("\n확인 사항:")
        print("1. Ollama 서버가 실행 중인가요? (ollama serve)")
        print("2. llama3.2 모델이 설치되어 있나요? (ollama pull llama3.2)")
        print("3. nomic-embed-text 모델이 설치되어 있나요? (ollama pull nomic-embed-text)")
        import traceback
        traceback.print_exc()
