"""
Test script for eviction criteria in Adaptive Semantic Cache System
With 100 UNIQUE queries to force eviction

This script creates 100 unique queries designed to test the eviction logic by:
1. Creating exactly 100 unique cache entries (forcing eviction at 50+ entries)
2. Each query is completely different to prevent similarity-based caching
3. Demonstrating which entries get evicted based on the value scoring system
"""
import httpx
import asyncio
import time
import random
import uuid
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta


BASE_URL = "http://localhost:8000"


class EvictionTest:
    """Test runner for eviction criteria"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.all_queries = []  # Store all 100 unique queries
        self.query_results = {}
        self.cache_stats_history = []
        
    async def clear_cache(self):
        """Clear cache to start fresh"""
        try:
            response = await self.client.post(f"{BASE_URL}/cache/clear")
            print("✅ Cache cleared")
            return True
        except Exception as e:
            print(f"⚠️ Could not clear cache: {e}")
            return False
    
    async def send_query(self, query: str, query_id: str = "", wait_ms: int = 50) -> Dict[str, Any]:
        """Send a query and track results"""
        try:
            if wait_ms > 0:
                await asyncio.sleep(wait_ms / 1000)
            
            response = await self.client.post(
                f"{BASE_URL}/query",
                json={"query": query, "max_tokens": 200, "temperature": 0.7}
            )
            response.raise_for_status()
            result = response.json()
            
            if query_id:
                self.query_results[query_id] = {
                    "query": query,
                    "cached": result.get("cached", False),
                    "similarity": result.get("similarity_score", 0),
                    "tokens_saved": result.get("tokens_saved", 0),
                    "latency": result.get("latency_ms", 0)
                }
            
            return result
            
        except Exception as e:
            print(f"❌ Error sending query: {e}")
            return None
    
    async def get_cache_stats(self):
        """Get detailed cache statistics"""
        try:
            response = await self.client.get(f"{BASE_URL}/cache/stats")
            stats = response.json()["stats"]
            self.cache_stats_history.append({
                "timestamp": time.time(),
                "stats": stats
            })
            return stats
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return None
    
    async def generate_unique_queries(self, count: int = 100):
        """Generate 100 completely unique queries"""
        print(f"\n🎯 Generating {count} UNIQUE queries...")
        
        base_topics = [
            "artificial intelligence", "machine learning", "quantum computing", 
            "blockchain technology", "neural networks", "computer vision",
            "natural language processing", "robotics", "cybersecurity",
            "data science", "big data", "cloud computing", "internet of things",
            "augmented reality", "virtual reality", "autonomous vehicles",
            "genetic engineering", "biotechnology", "renewable energy",
            "space exploration", "astrophysics", "climate change",
            "economics", "philosophy", "psychology", "sociology",
            "history", "literature", "mathematics", "physics"
        ]
        
        query_templates = [
            "What is {topic} and how does it work?",
            "Explain the concept of {topic} in simple terms.",
            "How does {topic} impact our daily lives?",
            "What are the main applications of {topic}?",
            "Describe the history and evolution of {topic}.",
            "What are the challenges facing {topic} today?",
            "How is {topic} different from similar fields?",
            "What skills are needed to work in {topic}?",
            "What are the ethical considerations of {topic}?",
            "How will {topic} change in the next 10 years?",
            "What are the key principles of {topic}?",
            "Can you provide examples of {topic} in practice?",
            "What are the limitations of current {topic} approaches?",
            "How does {topic} relate to other scientific fields?",
            "What research is currently being done in {topic}?"
        ]
        
        unique_queries = []
        used_combinations = set()
        
        for i in range(count):
            # Ensure uniqueness by combining topic + template + random UUID
            topic = random.choice(base_topics)
            template = random.choice(query_templates)
            unique_id = str(uuid.uuid4())[:8]  # Get first 8 chars of UUID string
            
            # Create query with slight variations
            query = template.format(topic=topic)
            query = f"{query} [UniqueID: {unique_id}]"
            
            # Add some random adjectives to ensure uniqueness
            adjectives = ["modern", "contemporary", "advanced", "emerging", 
                         "traditional", "novel", "innovative", "cutting-edge",
                         "revolutionary", "transformative", "disruptive"]
            
            if random.random() > 0.5:
                adj = random.choice(adjectives)
                query = query.replace(topic, f"{adj} {topic}")
            
            unique_queries.append(query)
        
        return unique_queries
    
    async def run_100_unique_queries_test(self):
        """Run test with 100 unique queries to force eviction"""
        print("\n" + "="*100)
        print("🧪 100 UNIQUE QUERIES EVICTION TEST")
        print("="*100)
        
        # Clear cache to start fresh
        print("\n🔄 Starting with clean cache...")
        await self.clear_cache()
        
        # Get initial stats
        initial_stats = await self.get_cache_stats()
        print(f"Initial cache size: {initial_stats.get('total_entries', 0) if initial_stats else 0}")
        
        # Generate 100 unique queries
        all_queries = await self.generate_unique_queries(100)
        self.all_queries = all_queries
        
        print(f"\n📝 Executing 100 unique queries...")
        print("="*100)
        
        # Execute queries in batches
        batch_size = 25
        for batch_num in range(4):
            start_idx = batch_num * batch_size
            end_idx = start_idx + batch_size
            batch = all_queries[start_idx:end_idx]
            
            print(f"\n📦 Batch {batch_num + 1}/{4} (Queries {start_idx + 1}-{end_idx})")
            print("-" * 50)
            
            for i, query in enumerate(batch, start=start_idx + 1):
                query_id = f"q{i:03d}"
                result = await self.send_query(query, query_id, wait_ms=30)
                
                # Print progress every 5 queries
                if i % 5 == 0:
                    cache_hits = sum(1 for r in self.query_results.values() if r["cached"])
                    cache_misses = len(self.query_results) - cache_hits
                    print(f"  Query {i}/100 - Cache: {cache_hits} hits, {cache_misses} misses")
            
            # Get cache stats after each batch
            batch_stats = await self.get_cache_stats()
            if batch_stats:
                current_size = batch_stats.get('total_entries', 0)
                print(f"  Cache size after batch: {current_size} entries")
                
                # Check if eviction has occurred
                if current_size >= 50 and len(self.cache_stats_history) > 1:
                    prev_size = self.cache_stats_history[-2]["stats"].get('total_entries', 0)
                    if current_size < prev_size:
                        print(f"  ⚠️ Eviction detected! Cache decreased from {prev_size} to {current_size}")
        
        # Final cache stats
        final_stats = await self.get_cache_stats()
        print(f"\n" + "="*100)
        print("📊 FINAL CACHE STATUS")
        print("="*100)
        
        if final_stats:
            print(f"\nCache Size: {final_stats.get('total_entries', 0)} entries")
            print(f"Total Queries Sent: {len(self.all_queries)}")
            
            # Calculate cache hits/misses
            total_cached = sum(1 for r in self.query_results.values() if r["cached"])
            total_not_cached = len(self.query_results) - total_cached
            
            print(f"Total Cached Responses: {total_cached}")
            print(f"Total Non-Cached Responses: {total_not_cached}")
            
            # Since all queries are unique, most should be non-cached
            # But some might have high similarity if our uniqueness failed
            print(f"\n📈 Expected vs Actual:")
            print(f"  Expected: Mostly non-cached (unique queries)")
            print(f"  Actual: {total_cached} cached, {total_not_cached} non-cached")
            
            # Get eviction count from stats
            evictions = final_stats.get('evictions', 0)
            print(f"\n🗑️ Evictions: {evictions}")
            
            # Show value distribution
            if 'value_distribution' in final_stats:
                dist = final_stats['value_distribution']
                print(f"\n📊 Value Score Distribution:")
                print(f"  Min: {dist.get('min', 0):.4f}")
                print(f"  Avg: {dist.get('avg', 0):.4f}")
                print(f"  Max: {dist.get('max', 0):.4f}")
            
            # Show top queries by hits (if any)
            if 'top_queries' in final_stats and final_stats['top_queries']:
                print(f"\n🏆 Top Surviving Queries:")
                for i, query_info in enumerate(final_stats['top_queries'][:3], 1):
                    query_preview = query_info['query'][:60] + "..." if len(query_info['query']) > 60 else query_info['query']
                    print(f"{i}. Hits: {query_info['hits']} | "
                          f"Value: {query_info.get('cache_value', 0):.3f}")
                    print(f"   \"{query_preview}\"")
            
            # Show when evictions likely occurred
            print(f"\n📅 Cache Growth Timeline:")
            for i, stat_entry in enumerate(self.cache_stats_history):
                stats = stat_entry["stats"]
                if i == 0:
                    print(f"  Initial: {stats.get('total_entries', 0)} entries")
                else:
                    prev_stats = self.cache_stats_history[i-1]["stats"]
                    prev_count = prev_stats.get('total_entries', 0)
                    curr_count = stats.get('total_entries', 0)
                    if curr_count < prev_count:
                        print(f"  Batch {i}: {prev_count} → {curr_count} entries (Eviction!)")
                    else:
                        print(f"  Batch {i}: {curr_count} entries")
        
        # Now test re-querying to see what survived
        print(f"\n" + "="*100)
        print("🔄 RE-QUERY TEST: Checking which entries survived")
        print("="*100)
        
        # Re-query a sample of 20 queries from different positions
        sample_indices = list(range(0, 100, 5))  # Every 5th query
        survivors = 0
        total_sampled = len(sample_indices)
        
        print(f"\nRe-querying {total_sampled} sample queries...")
        for idx in sample_indices:
            if idx < len(self.all_queries):
                original_query = self.all_queries[idx]
                query_id = f"re_q{idx+1:03d}"
                
                result = await self.send_query(original_query, query_id, wait_ms=50)
                
                if result and result.get("cached", False):
                    survivors += 1
                    status = "✅ HIT (survived)"
                else:
                    status = "❌ MISS (evicted or never cached)"
                
                # Show first and last few samples
                if idx in [0, 5, 95, 99]:
                    query_preview = original_query[:50] + "..." if len(original_query) > 50 else original_query
                    print(f"  Query {idx+1}: {status}")
                    print(f"    \"{query_preview}\"")
        
        print(f"\n📊 Survival Rate in Sample: {survivors}/{total_sampled} ({survivors/total_sampled:.1%})")
        
        # Based on eviction criteria, queries should survive based on:
        # 1. Hits (these are all 1 hit except re-queries)
        # 2. Age (older queries are more likely evicted)
        # 3. Token savings (longer responses might survive)
        print(f"\n🎯 Expected Eviction Pattern:")
        print(f"  1. Older queries (first 50) are more likely evicted")
        print(f"  2. Newer queries (last 50) are more likely to survive")
        print(f"  3. Queries with higher token savings might survive longer")
        
        return {
            "initial_stats": initial_stats,
            "final_stats": final_stats,
            "total_queries": len(self.all_queries),
            "survival_rate": survivors / total_sampled if total_sampled > 0 else 0
        }
    
    async def run_simple_eviction_test(self):
        """Run a simple test that just sends 100 queries and shows eviction"""
        print(f"\n" + "="*100)
        print("🧪 SIMPLE 100-QUERY EVICTION TEST")
        print("="*100)
        
        # Clear cache first
        # await self.clear_cache()
        
        # Create 100 simple unique queries without UUID complications
        simple_queries = []
        for i in range(100):
            topic_num = i + 1
            query = f"What is the main concept behind technology topic {topic_num}? Please explain in detail with examples relevant to modern applications in various industries across different sectors."
            simple_queries.append(query)
        
        print(f"\n📝 Sending 100 simple unique queries...")
        
        cache_sizes = []
        eviction_points = []
        
        for i, query in enumerate(simple_queries, 1):
            query_id = f"simple_q{i:03d}"
            await self.send_query(query, query_id, wait_ms=20)
            
            # Check cache size every 10 queries
            if i % 10 == 0:
                stats = await self.get_cache_stats()
                if stats:
                    size = stats.get('total_entries', 0)
                    cache_sizes.append((i, size))
                    print(f"  Query {i}/100: Cache size = {size}")
                    
                    # Check if eviction occurred
                    if len(cache_sizes) > 1:
                        prev_i, prev_size = cache_sizes[-2]
                        if size < prev_size:
                            print(f"    ⚠️ EVICTION DETECTED! Cache decreased from {prev_size} to {size}")
                            eviction_points.append((prev_i, i, prev_size, size))
        
        # Final analysis
        final_stats = await self.get_cache_stats()
        
        print(f"\n" + "="*100)
        print("📊 FINAL ANALYSIS")
        print("="*100)
        
        if final_stats:
            print(f"\nFinal Cache Size: {final_stats.get('total_entries', 0)} entries")
            print(f"Total Evictions: {final_stats.get('evictions', 0)}")
            print(f"Total Queries Sent: 100")
            
            # Show cache hit rate
            total_cached = sum(1 for r in self.query_results.values() if r["cached"])
            hit_rate = total_cached / 100 if self.query_results else 0
            print(f"Cache Hit Rate: {hit_rate:.1%} (expected to be low for unique queries)")
            
            # Show eviction points
            if eviction_points:
                print(f"\n📉 Eviction Points Detected:")
                for start_q, end_q, old_size, new_size in eviction_points:
                    print(f"  Between queries {start_q}-{end_q}: {old_size} → {new_size} entries")
            
            # Calculate expected vs actual
            expected_final_size = 50  # After many evictions
            actual_final_size = final_stats.get('total_entries', 0)
            
            print(f"\n🎯 Expected Final Cache Size: ~{expected_final_size}")
            print(f"📊 Actual Final Cache Size: {actual_final_size}")
            
            if actual_final_size > 60:
                print(f"❌ UNEXPECTED: Cache has more than 60 entries!")
            elif actual_final_size > 50:
                print(f"⚠️ Note: Cache slightly above 50, may need more queries to trigger eviction")
            else:
                print(f"✅ GOOD: Cache at or below 50 entries")
        
        return final_stats
    
    async def run_comprehensive_test(self):
        """Run all tests"""
        print("\n" + "="*100)
        print("🧪 COMPREHENSIVE EVICTION TEST SUITE")
        print("="*100)
        
        try:
            # Check if server is running
            response = await self.client.get(f"{BASE_URL}/")
            print(f"✅ Server is running: {response.json()}")
        except Exception as e:
            print(f"❌ Error: Cannot connect to server at {BASE_URL}")
            print(f"   Make sure the server is running: python main.py")
            return
        
        # Run simple test first (avoids UUID issues)
        print(f"\n1️⃣ MAIN TEST: 100 Simple Unique Queries")
        main_results = await self.run_simple_eviction_test()
        
        # Summary
        print(f"\n" + "="*100)
        print("📋 TEST SUMMARY")
        print("="*100)
        
        if main_results:
            print(f"\n✅ Test Completed:")
            print(f"   Final cache size: {main_results.get('total_entries', 'N/A')}")
            print(f"   Total evictions: {main_results.get('evictions', 'N/A')}")
            print(f"   Cache hit rate: {main_results.get('hit_rate', 'N/A')}")
        
        print(f"\n🎯 Key Observations:")
        print(f"   1. Cache should max out at 50 entries")
        print(f"   2. When limit reached, 10% (5 entries) should be evicted")
        print(f"   3. Eviction based on LOWEST value score:")
        print(f"      - Few hits (40% weight)")
        print(f"      - Old age (20% weight)")
        print(f"      - Low similarity (20% weight)")
        print(f"      - Low token savings (20% weight)")
        
        print(f"\n📊 To verify eviction criteria:")
        print(f"   1. Check cache stats endpoint")
        print(f"   2. Look for evictions count")
        print(f"   3. Examine value distribution")
        print(f"   4. Re-query old queries to see if evicted")
        
        return main_results
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()


async def main():
    """Main test function"""
    test = EvictionTest()
    
    try:
        # Run comprehensive test
        results = await test.run_comprehensive_test()
        
        print(f"\n" + "="*100)
        print("✅ TEST COMPLETE")
        print("="*100)
        
        # Export results if needed
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "cache_size": results.get('total_entries', 0) if results else 0,
            "evictions": results.get('evictions', 0) if results else 0,
            "total_queries": 100
        }
        
        with open("eviction_test_results.json", "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"\n📁 Results saved to eviction_test_results.json")
        
    finally:
        await test.close()


if __name__ == "__main__":
    asyncio.run(main())