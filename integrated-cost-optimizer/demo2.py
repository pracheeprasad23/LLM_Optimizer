"""
Demo Script 2 - Different Query Set for the Integrated LLM Cost Optimizer

This script tests with a completely different set of queries than demo.py.
Use this after running demo.py to see cache hits on semantically similar but
differently worded queries.

Run with: python demo2.py
Requires backend running: uvicorn main:app --port 8000
"""

import asyncio
import time
import random
from datetime import datetime

# Test queries organized by category - DIFFERENT FROM demo.py
WEB_DEV_QUERIES = [
    "Build a responsive navbar using CSS flexbox",
    "Create a dark mode toggle in JavaScript",
    "How to implement lazy loading for images",
    "Write CSS for a card component with shadow",
    "Create an accordion menu using vanilla JS",
    "Implement infinite scroll in React",
    "Add form validation with error messages",
    "Create a modal popup component",
    "Build a responsive grid layout",
    "Implement drag and drop functionality",
    "CSS flexbox responsive navigation bar",  # variation
    "JavaScript dark theme switcher",  # variation
    "Image lazy loading implementation",  # variation
    "CSS card with box shadow",  # variation
]

BACKEND_QUERIES = [
    "Create a middleware for authentication in Express.js",
    "Implement rate limiting for API endpoints",
    "Write a database connection pool in Node.js",
    "Create a caching layer with Redis",
    "Implement file upload handling",
    "Build a webhook handler service",
    "Create database migrations with Knex.js",
    "Implement request validation middleware",
    "Build a job queue processor",
    "Create API versioning strategy",
    "Express.js auth middleware creation",  # variation
    "API rate limiting implementation",  # variation
    "Redis caching layer setup",  # variation
]

DEVOPS_QUERIES = [
    "Write a Dockerfile for a Node.js app",
    "Create a GitHub Actions workflow for CI",
    "Configure nginx as reverse proxy",
    "Set up Kubernetes deployment manifest",
    "Create Terraform configuration for AWS EC2",
    "Write a bash script for log rotation",
    "Configure Prometheus alerting rules",
    "Set up Grafana dashboard for monitoring",
    "Create Helm chart for microservice",
    "Write ansible playbook for server setup",
    "Node.js Dockerfile creation",  # variation
    "GitHub Actions CI pipeline",  # variation
    "Nginx reverse proxy config",  # variation
]

DATABASE_QUERIES = [
    "Design a schema for e-commerce products",
    "Write a query with multiple JOINs",
    "Create database indexes for performance",
    "Implement full-text search in PostgreSQL",
    "Write a stored procedure for order processing",
    "Design a time-series data schema",
    "Create a data archival strategy",
    "Implement database sharding logic",
    "Write query to find orphan records",
    "Design schema for multi-tenancy",
    "E-commerce product database schema",  # variation
    "SQL multiple JOIN query",  # variation
    "PostgreSQL full text search setup",  # variation
]

SECURITY_QUERIES = [
    "How to prevent SQL injection attacks",
    "Implement JWT token refresh mechanism",
    "Set up CORS policy correctly",
    "How to store passwords securely",
    "Implement two-factor authentication",
    "Create a content security policy",
    "How to prevent XSS attacks",
    "Implement API key rotation",
    "Set up SSL certificate automation",
    "Create audit logging for compliance",
    "SQL injection prevention methods",  # variation
    "JWT refresh token implementation",  # variation
    "Secure password hashing storage",  # variation
]

TESTING_QUERIES = [
    "Write unit tests for a REST API",
    "Create integration tests with Jest",
    "Set up end-to-end testing with Cypress",
    "Write mocks for external API calls",
    "Implement test coverage reporting",
    "Create snapshot tests for React components",
    "Write performance benchmark tests",
    "Set up contract testing for microservices",
    "Implement chaos engineering tests",
    "REST API unit testing guide",  # variation
    "Jest integration test setup",  # variation
    "Cypress e2e testing configuration",  # variation
]

ARCHITECTURE_QUERIES = [
    "Design event-driven architecture pattern",
    "Implement CQRS with event sourcing",
    "Create clean architecture folder structure",
    "Design API gateway pattern",
    "Implement circuit breaker pattern",
    "Design pub/sub messaging system",
    "Create domain-driven design boundaries",
    "Implement saga pattern for transactions",
    "Design multi-region deployment strategy",
    "Event-driven architecture design",  # variation
    "CQRS event sourcing implementation",  # variation
]

DEBUGGING_QUERIES = [
    "How to debug memory leaks in Node.js",
    "Profile Python application performance",
    "Debug async/await issues in JavaScript",
    "Find and fix N+1 query problems",
    "Debug network latency issues",
    "Trace distributed system requests",
    "Debug race conditions in concurrent code",
    "Profile database query performance",
    "Node.js memory leak debugging",  # variation
    "Python performance profiling",  # variation
]

QUICK_QUERIES = [
    "What is REST?",
    "Define GraphQL",
    "What is gRPC?",
    "Explain WebSocket",
    "What is OAuth?",
    "Define CORS",
    "What is CDN?",
    "Explain SSL/TLS",
    "What is DNS?",
    "Define load balancer",
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
    """Run demo with alternative query set"""
    
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
    print("🚀 DEMO 2 - ALTERNATIVE QUERY SET")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Collect all queries
    all_queries = []
    
    all_queries.extend([(q, "web_dev") for q in WEB_DEV_QUERIES])
    all_queries.extend([(q, "backend") for q in BACKEND_QUERIES])
    all_queries.extend([(q, "devops") for q in DEVOPS_QUERIES])
    all_queries.extend([(q, "database") for q in DATABASE_QUERIES])
    all_queries.extend([(q, "security") for q in SECURITY_QUERIES])
    all_queries.extend([(q, "testing") for q in TESTING_QUERIES])
    all_queries.extend([(q, "architecture") for q in ARCHITECTURE_QUERIES])
    all_queries.extend([(q, "debugging") for q in DEBUGGING_QUERIES])
    all_queries.extend([(q, "quick") for q in QUICK_QUERIES])
    
    # Add some duplicates to test exact cache hits
    duplicates = random.sample(all_queries, 15)
    all_queries.extend(duplicates)
    
    # Shuffle to simulate realistic usage
    random.shuffle(all_queries)
    
    # Limit to 120 queries
    queries = all_queries[:120]
    
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
                    else:
                        stats["cache_misses"] += 1
                    
                    cost = result.get("cost", 0)
                    cost_saved = result.get("cost_saved", 0)
                    stats["total_cost"] += cost
                    stats["total_cost_saved"] += cost_saved
                    
                    if category not in stats["by_category"]:
                        stats["by_category"][category] = {"hits": 0, "misses": 0}
                    if result.get("cached"):
                        stats["by_category"][category]["hits"] += 1
                    else:
                        stats["by_category"][category]["misses"] += 1
                    
                    model = result.get("selected_model", "cached")
                    if model not in stats["by_model"]:
                        stats["by_model"][model] = 0
                    stats["by_model"][model] += 1
                    
                    print_query_details(i, len(queries), query, category, result, elapsed)
                    
                else:
                    stats["errors"] += 1
                    print(f"\n❌ ERROR {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                stats["errors"] += 1
                print(f"[{i:3d}/120] ⚠️ ERROR: {e}")
            
            await asyncio.sleep(0.05)
    
    # Print summary
    print()
    print("="*70)
    print("📊 DEMO 2 RESULTS SUMMARY")
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
    print(f"✅ Demo 2 completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print()
    print("👉 Open http://localhost:8501 to see results in the Streamlit dashboard!")


if __name__ == "__main__":
    asyncio.run(run_demo())
