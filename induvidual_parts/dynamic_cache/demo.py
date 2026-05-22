"""
Demo script for Adaptive Semantic Cache System

Configurable Guarantees:
- N forced unique (new) queries → CACHE MISS
- M semantically similar queries → CACHE HIT
- K random unrelated queries
- Similar queries never appear before their base
- Random + similar queries are randomly interleaved
"""

import httpx
import asyncio
import time
import random
from typing import Dict, Any

# ==========================================================
# 🔧 CONFIGURATION (EDIT HERE)
# ==========================================================
BASE_QUERY_COUNT = 60        # Forced cache misses
CACHE_HIT_QUERY_COUNT = 40  # Semantic cache hits
RANDOM_QUERY_COUNT = 60     # Random noise queries
REQUEST_DELAY_SEC = 0.25
BASE_URL = "http://localhost:8000"
# ==========================================================


class CacheDemo:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = []

    async def send_query(self, query: str) -> Dict[str, Any]:
        print(f"\n{'=' * 80}")
        print(f"Query: {query}")
        print(f"{'=' * 80}")

        start = time.time()

        response = await self.client.post(
            f"{BASE_URL}/query",
            json={"query": query, "max_tokens": 500, "temperature": 0.7},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("cached"):
            print("✅ CACHE HIT")
            print(f"   Similarity: {result.get('similarity_score', 0):.4f}")
            print(f"   Threshold: {result.get('threshold_used', 0):.4f}")
            print(f"   Tokens Saved: {result.get('tokens_saved', 0)}")
            print(f"   Cost Saved: ${result.get('cost_saved', 0):.6f}")
        else:
            print("❌ CACHE MISS")
            print(f"   Tokens Used: {result.get('tokens_used', 0)}")
            print(f"   Cost: ${result.get('cost', 0):.6f}")

        latency = result.get("latency_ms", (time.time() - start) * 1000)
        print(f"   Latency: {latency:.2f}ms")

        self.results.append({
            "cached": bool(result.get("cached", False)),
            "latency_ms": float(latency),
            "tokens_saved": result.get("tokens_saved", 0),
            "cost_saved": result.get("cost_saved", 0.0),
        })

        return result

    async def print_metrics(self):
        metrics = (await self.client.get(f"{BASE_URL}/metrics")).json().get("metrics", {})

        print(f"\n{'=' * 80}")
        print("📊 METRICS")
        print(f"{'=' * 80}")
        print(f"Requests: {metrics.get('total_requests', 0)}")
        print(f"Hits: {metrics.get('cache_hits', 0)} ({metrics.get('hit_rate', 0):.2%})")
        print(f"Misses: {metrics.get('cache_misses', 0)}")
        print(f"Cache Size: {metrics.get('cache_size', 0)}")
        print(f"Tokens Saved: {metrics.get('llm_tokens_saved', 0):,}")
        print(f"Cost Saved: ${metrics.get('total_cost_saved', 0):.6f}")
        print(f"Evictions: {metrics.get('evictions', 0)}")

    async def print_summary(self):
        hits = [r for r in self.results if r["cached"]]
        misses = [r for r in self.results if not r["cached"]]

        print(f"\n{'=' * 80}")
        print("📈 SUMMARY")
        print(f"{'=' * 80}")
        print(f"Total Queries: {len(self.results)}")
        print(f"Hits: {len(hits)} | Misses: {len(misses)}")

        if hits and misses:
            avg_hit = sum(r["latency_ms"] for r in hits) / len(hits)
            avg_miss = sum(r["latency_ms"] for r in misses) / len(misses)
            print(f"Avg Hit Latency: {avg_hit:.2f}ms")
            print(f"Avg Miss Latency: {avg_miss:.2f}ms")
            print(f"Speedup: {avg_miss / avg_hit:.1f}x")

    async def run_demo(self):
        print("\n" + "=" * 80)
        print("🚀 ADAPTIVE SEMANTIC CACHE DEMO")
        print("=" * 80)

        # --------------------------------------------------
        # BASE QUERIES (truncate by config)
        # --------------------------------------------------
        base_queries = [
            "What is the capital of France?",
            "What is the capital of Germany?",
            "What is the capital of Japan?",
            "Which country has the city of Cairo?",
            "What is the longest river in the world?",
            "Which is the largest desert on Earth?",
            "What is photosynthesis?",
            "Explain Newton's first law of motion",
            "What is quantum computing?",
            "What is dark matter?",
            "Explain the theory of relativity",
            "What is nuclear fusion?",
            "What is machine learning?",
            "Explain artificial intelligence",
            "What is blockchain technology?",
            "What is cloud computing?",
            "What is edge computing?",
            "Explain what APIs are",
            "What is Python programming language?",
            "Explain object oriented programming",
            "What is a REST API?",
            "Difference between list and tuple in Python",
            "What is a database index?",
            "Explain multithreading",
            "What is calculus?",
            "Explain linear algebra",
            "What is the Pythagorean theorem?",
            "What is probability theory?",
            "Explain standard deviation",
            "What is matrix multiplication?",
            "Who was Napoleon Bonaparte?",
            "What caused World War 1?",
            "What was the Industrial Revolution?",
            "Who discovered America?",
            "What was the French Revolution?",
            "Explain the Cold War",
            "What is inflation?",
            "Explain supply and demand",
            "What is a startup?",
            "What is venture capital?",
            "Explain market capitalization",
            "What is GDP?",
            "What is climate change?",
            "Explain renewable energy",
            "What is space exploration?",
            "What causes earthquakes?",
            "What is human DNA?",
            "Explain the solar system",
            "What is cybersecurity?",
            "Explain neural networks",
            "What is data science?",
            "Explain big data",
            "What is DevOps?",
            "Explain containerization",
            "What is Kubernetes?",
            "Explain microservices",
            "What is Internet of Things?"
        ][:BASE_QUERY_COUNT]

        # --------------------------------------------------
        # SEMANTIC VARIANTS (truncate by config)
        # --------------------------------------------------
        semantic_variants = [
            (0, "Which city serves as France’s capital?"),
            (1, "Capital city of Germany?"),
            (2, "Which city is Japan governed from?"),
            (6, "How does photosynthesis work in plants?"),
            (7, "State Newton’s first law simply"),
            (8, "How does quantum computing differ from classical computing?"),
            (9, "What exactly is meant by dark matter?"),
            (12, "Explain machine learning in simple words"),
            (13, "What does AI actually mean?"),
            (14, "How does blockchain ensure trust?"),
            (15, "Explain cloud computing with an example"),
            (18, "Tell me about Python language"),
            (19, "What are OOP concepts?"),
            (20, "Explain RESTful APIs"),
            (21, "How are Python lists and tuples different?"),
            (24, "Explain the basics of calculus"),
            (25, "What does linear algebra study?"),
            (26, "Explain the Pythagorean theorem simply"),
            (28, "Why is standard deviation important?"),
            (30, "Who was Napoleon and why is he important?"),
            (31, "What triggered World War 1?"),
            (32, "Why was the Industrial Revolution important?"),
            (35, "What was the Cold War about?"),
            (36, "Why does inflation occur?"),
            (37, "Explain the law of supply and demand"),
            (38, "How does a startup company work?"),
            (39, "What role does venture capital play?"),
            (41, "What does GDP measure?"),
            (42, "How does climate change affect Earth?"),
            (43, "What are renewable energy sources?")
        ][:CACHE_HIT_QUERY_COUNT]

        # --------------------------------------------------
        # RANDOM QUERIES
        # --------------------------------------------------
        random_queries = [
            "How to tie a tie?",
            "What are black holes?",
            "How does GPS work?",
            "How to improve time management?",
            "What are ETFs?",
            "How do wind turbines generate power?",
            "What is augmented reality?",
            "How to prepare for interviews?",
            "What causes coral bleaching?",
            "How to optimize images for web?"
        ]
        random_queries = random_queries * ((RANDOM_QUERY_COUNT // len(random_queries)) + 1)
        random_queries = random_queries[:RANDOM_QUERY_COUNT]

        # --------------------------------------------------
        # BUILD EXECUTION STREAM
        # --------------------------------------------------
        execution_stream = [("base", i, q) for i, q in enumerate(base_queries)]

        for base_idx, text in semantic_variants:
            if base_idx < len(base_queries):
                base_pos = next(i for i, x in enumerate(execution_stream) if x[1] == base_idx)
                insert_pos = random.randint(base_pos + 1, len(execution_stream))
                execution_stream.insert(insert_pos, ("similar", base_idx, text))

        for q in random_queries:
            execution_stream.insert(random.randint(0, len(execution_stream)), ("random", None, q))

        # --------------------------------------------------
        # EXECUTE
        # --------------------------------------------------
        for i, (kind, _, query) in enumerate(execution_stream, 1):
            print(f"\n[{i}/{len(execution_stream)}] [{kind.upper()}]")
            await self.send_query(query)
            await asyncio.sleep(REQUEST_DELAY_SEC)

        await self.print_metrics()
        await self.print_summary()

        print(f"\n{'=' * 80}")
        print("✅ DEMO COMPLETE")
        print(f"{'=' * 80}")

    async def close(self):
        await self.client.aclose()


async def main():
    demo = CacheDemo()
    try:
        await demo.client.get(f"{BASE_URL}/")
        await demo.run_demo()
    finally:
        await demo.close()


if __name__ == "__main__":
    asyncio.run(main())
