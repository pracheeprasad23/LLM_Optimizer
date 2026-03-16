"""
Demo Script - 150 Queries to Test the Integrated LLM Cost Optimizer

This script tests:
1. Cache hits with similar/duplicate queries
2. Different intent types (coding, summarization, reasoning, etc.)
3. Different complexity levels (low, medium, high)
4. Model selection across different providers
5. Batching behavior with rapid requests

Run with: python demo.py
Requires backend running: uvicorn main:app --port 8000
"""

import asyncio
import time
import random
from datetime import datetime

# Test queries organized by category
CODING_QUERIES = [
    "Write a Python function to calculate factorial",
    "Create a JavaScript function to reverse a string",
    "Write Python code to sort a list of dictionaries by key",
    "Implement a binary search algorithm in Python",
    "Create a REST API endpoint using FastAPI",
    "Write a SQL query to find duplicate records",
    "Implement a linked list in Python",
    "Create a React component for a login form",
    "Write a Python decorator for logging function calls",
    "Implement merge sort algorithm",
    "Write Python code for factorial calculation",  # variation
    "JavaScript reverse string function",  # variation
    "Python sort list of dicts by key value",  # variation
    "Binary search implementation Python",  # variation
    "FastAPI REST endpoint example",  # variation
]

SUMMARIZATION_QUERIES = [
    "Summarize the key concepts of machine learning",
    "Give me a brief overview of blockchain technology",
    "Summarize the principles of agile development",
    "Briefly explain cloud computing",
    "TLDR: What is DevOps?",
    "Summarize the benefits of microservices architecture",
    "Brief explanation of neural networks",
    "Summarize REST API best practices",
    "Quick overview of containerization with Docker",
    "Summarize database normalization concepts",
    "Machine learning key concepts summary",  # variation
    "Blockchain technology overview briefly",  # variation
    "Agile development principles summarized",  # variation
    "Cloud computing brief explanation",  # variation
    "DevOps summary in short",  # variation
]

REASONING_QUERIES = [
    "Explain why microservices are better than monolithic architecture",
    "Analyze the trade-offs between SQL and NoSQL databases",
    "Why is functional programming becoming popular?",
    "Explain the reasoning behind using TypeScript over JavaScript",
    "Analyze the benefits and drawbacks of serverless computing",
    "Why are design patterns important in software development?",
    "Explain the reasoning for using message queues",
    "Analyze when to use GraphQL vs REST",
    "Why is test-driven development considered a best practice?",
    "Explain the trade-offs of different caching strategies",
    "Microservices vs monolithic - why microservices are better",  # variation
    "SQL vs NoSQL trade-off analysis",  # variation
    "Why is functional programming popular now?",  # variation
    "TypeScript over JavaScript - explain reasoning",  # variation
    "Serverless computing benefits and drawbacks analysis",  # variation
]

DATA_ANALYSIS_QUERIES = [
    "How do I analyze a CSV dataset in Python?",
    "Create a visualization for sales data using matplotlib",
    "Explain how to perform exploratory data analysis",
    "How to clean and preprocess data for machine learning",
    "Create a dashboard for KPI tracking",
    "How to perform sentiment analysis on text data",
    "Explain statistical testing for A/B experiments",
    "How to detect anomalies in time series data",
    "Create a chart showing customer segmentation",
    "How to calculate correlation between variables",
    "Python CSV dataset analysis",  # variation
    "Matplotlib sales data visualization",  # variation
    "Exploratory data analysis explanation",  # variation
    "Data preprocessing for ML",  # variation
    "KPI tracking dashboard creation",  # variation
]

FACTUAL_QUERIES = [
    "What is the difference between RAM and ROM?",
    "Define API in software development",
    "What is HTTP status code 404?",
    "What does SOLID stand for in programming?",
    "Define recursion in computer science",
    "What is an IP address?",
    "What is the OSI model?",
    "Define machine learning algorithm",
    "What is version control?",
    "What is a database index?",
    "RAM vs ROM difference",  # variation
    "API definition in software",  # variation
    "HTTP 404 meaning",  # variation
    "SOLID principles meaning",  # variation
    "Recursion definition computer science",  # variation
]

CREATIVE_QUERIES = [
    "Write a creative tagline for a tech startup",
    "Generate a story about a programmer solving a bug",
    "Create a poem about coding",
    "Write a creative description for a mobile app",
    "Generate marketing copy for a SaaS product",
    "Tech startup creative tagline",  # variation
    "Story about programmer fixing bugs",  # variation
    "Poem about programming",  # variation
]

COMPLEX_QUERIES = [
    "Provide a comprehensive step-by-step guide to implementing a distributed system with microservices, including service discovery, load balancing, circuit breakers, and observability.",
    "Explain in detail how to design a scalable real-time analytics pipeline using Apache Kafka, Apache Spark, and a time-series database.",
    "Create a comprehensive tutorial on implementing OAuth 2.0 with OpenID Connect for a multi-tenant SaaS application.",
    "Design a complete CI/CD pipeline for a containerized application with blue-green deployments, automated testing, and security scanning.",
    "Explain the complete architecture of a machine learning platform including data versioning, experiment tracking, and model registry.",
]

COMPLIANCE_QUERIES = [
    "How do I handle personal data in compliance with GDPR?",
    "Explain PII handling best practices for healthcare applications",
    "What are the privacy requirements for storing user data?",
    "How to implement data encryption for sensitive information?",
    "Explain confidential data handling policies",
]

SHORT_QUERIES = [
    "What is Python?",
    "Define API",
    "HTTP methods?",
    "What is JSON?",
    "Git basics?",
    "SQL vs NoSQL?",
    "What is REST?",
    "Define OOP",
    "Cloud types?",
    "What is Docker?",
]


def print_query_details(i: int, total: int, query: str, category: str, result: dict, elapsed: float):
    """Print detailed info about each query"""
    cached = result.get("cached", False)
    
    print()
    print("=" * 80)
    print(f"QUERY [{i}/{total}]")
    print("=" * 80)
    print(f"📝 Prompt:      {query[:70]}{'...' if len(query) > 70 else ''}")
    print(f"📁 Category:    {category}")
    print("-" * 80)
    
    if cached:
        print(f"✅ CACHE HIT!")
        print(f"   Similarity:  {result.get('similarity_score', 0):.4f}")
        print(f"   Threshold:   {result.get('threshold_used', 0):.2f}")
    else:
        print(f"❌ CACHE MISS")
        print(f"   Model:       {result.get('selected_model', 'N/A')}")
        if result.get('batch_id'):
            print(f"   Batch ID:    {result.get('batch_id')}")
    
    print("-" * 80)
    print(f"📊 Tokens Used:   {result.get('tokens_used', 0)}")
    print(f"📊 Tokens Saved:  {result.get('tokens_saved', 0)}")
    print(f"💰 Cost:          ${result.get('cost', 0):.6f}")
    print(f"💰 Cost Saved:    ${result.get('cost_saved', 0):.6f}")
    print(f"⏱️  Latency:       {result.get('latency_ms', 0):.0f}ms (total: {elapsed:.0f}ms)")
    print(f"🔖 Tracking ID:   {result.get('tracking_id', 'N/A')}")
    print("-" * 80)
    print(f"💬 Response:    {result.get('response', '')[:100]}...")
    print("=" * 80)


async def run_demo():
    """Run the 150 query demo test"""
    
    # Import here to avoid issues if not installed
    try:
        import httpx
    except ImportError:
        print("Installing httpx...")
        import subprocess
        subprocess.run(["pip", "install", "httpx"], check=True)
        import httpx
    
    BASE_URL = "http://localhost:8000"
    
    # Check if server is running
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code != 200:
                print("❌ Backend not responding. Start with: uvicorn main:app --port 8000")
                return
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            print("   Start with: uvicorn main:app --port 8000")
            return
    
    print("="*70)
    print("🚀 INTEGRATED LLM COST OPTIMIZER - 150 QUERY DEMO TEST")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Collect all queries
    all_queries = []
    
    # Add queries from each category
    all_queries.extend([(q, "coding") for q in CODING_QUERIES])
    all_queries.extend([(q, "summarization") for q in SUMMARIZATION_QUERIES])
    all_queries.extend([(q, "reasoning") for q in REASONING_QUERIES])
    all_queries.extend([(q, "data_analysis") for q in DATA_ANALYSIS_QUERIES])
    all_queries.extend([(q, "factual") for q in FACTUAL_QUERIES])
    all_queries.extend([(q, "creative") for q in CREATIVE_QUERIES])
    all_queries.extend([(q, "complex") for q in COMPLEX_QUERIES])
    all_queries.extend([(q, "compliance") for q in COMPLIANCE_QUERIES])
    all_queries.extend([(q, "short") for q in SHORT_QUERIES])
    
    # Add some duplicates to test exact cache hits
    duplicates = random.sample(all_queries, 20)
    all_queries.extend(duplicates)
    
    # Shuffle to simulate realistic usage
    random.shuffle(all_queries)
    
    # Limit to 150 queries
    queries = all_queries[:150]
    
    print(f"Total queries to process: {len(queries)}")
    print()
    
    # Stats tracking
    stats = {
        "total": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "total_cost": 0.0,
        "total_cost_saved": 0.0,
        "total_time_ms": 0.0,
        "by_category": {},
        "by_model": {},
        "errors": 0,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, (query, category) in enumerate(queries, 1):
            try:
                start = time.time()
                
                response = await client.post(
                    f"{BASE_URL}/query",
                    json={
                        "query": query,
                        "max_tokens": 500,
                        "temperature": 0.7
                    }
                )
                
                elapsed = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    
                    stats["total"] += 1
                    stats["total_time_ms"] += elapsed
                    
                    if result.get("cached"):
                        stats["cache_hits"] += 1
                        status = "✅ HIT"
                    else:
                        stats["cache_misses"] += 1
                        status = "❌ MISS"
                    
                    cost = result.get("cost", 0)
                    cost_saved = result.get("cost_saved", 0)
                    stats["total_cost"] += cost
                    stats["total_cost_saved"] += cost_saved
                    
                    # Track by category
                    if category not in stats["by_category"]:
                        stats["by_category"][category] = {"hits": 0, "misses": 0}
                    if result.get("cached"):
                        stats["by_category"][category]["hits"] += 1
                    else:
                        stats["by_category"][category]["misses"] += 1
                    
                    # Track by model
                    model = result.get("selected_model", "cached")
                    if model not in stats["by_model"]:
                        stats["by_model"][model] = 0
                    stats["by_model"][model] += 1
                    
                    # Print detailed query info
                    print_query_details(i, len(queries), query, category, result, elapsed)
                    
                else:
                    stats["errors"] += 1
                    print(f"\n❌ ERROR {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                stats["errors"] += 1
                print(f"[{i:3d}/150] ⚠️ ERROR: {e}")
            
            # Small delay to avoid overwhelming
            await asyncio.sleep(0.05)
    
    # Print summary
    print()
    print("="*70)
    print("📊 DEMO RESULTS SUMMARY")
    print("="*70)
    print()
    
    hit_rate = (stats["cache_hits"] / stats["total"] * 100) if stats["total"] > 0 else 0
    avg_time = stats["total_time_ms"] / stats["total"] if stats["total"] > 0 else 0
    
    print(f"Total Queries:      {stats['total']}")
    print(f"Cache Hits:         {stats['cache_hits']} ({hit_rate:.1f}%)")
    print(f"Cache Misses:       {stats['cache_misses']}")
    print(f"Errors:             {stats['errors']}")
    print()
    print(f"Total Cost:         ${stats['total_cost']:.6f}")
    print(f"Cost Saved:         ${stats['total_cost_saved']:.6f}")
    print(f"Avg Response Time:  {avg_time:.0f}ms")
    print()
    
    print("📁 Results by Category:")
    print("-" * 40)
    for category, data in sorted(stats["by_category"].items()):
        cat_total = data["hits"] + data["misses"]
        cat_rate = (data["hits"] / cat_total * 100) if cat_total > 0 else 0
        print(f"  {category:15s}: {data['hits']:2d} hits, {data['misses']:2d} misses ({cat_rate:.0f}% hit rate)")
    print()
    
    print("🤖 Queries by Model:")
    print("-" * 40)
    for model, count in sorted(stats["by_model"].items(), key=lambda x: x[1], reverse=True):
        model_name = model if model else "cached"
        print(f"  {model_name:25s}: {count:3d} queries")
    print()
    
    # Fetch final system metrics
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/metrics")
            if response.status_code == 200:
                metrics = response.json()
                cache = metrics.get("cache", {})
                
                print("📈 Final System Metrics:")
                print("-" * 40)
                print(f"  Cache Size:       {cache.get('cache_size', 0)} entries")
                print(f"  Total Evictions:  {cache.get('evictions', 0)}")
                print(f"  Tokens Used:      {cache.get('llm_tokens_used', 0)}")
                print(f"  Tokens Saved:     {cache.get('llm_tokens_saved', 0)}")
        except:
            pass
    
    print()
    print("="*70)
    print(f"✅ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print()
    print("👉 Open http://localhost:8501 to see results in the Streamlit dashboard!")


if __name__ == "__main__":
    asyncio.run(run_demo())
