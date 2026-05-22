#!/usr/bin/env python3
"""
Test script to send sample metrics to the LLM Optimization Hub
Run this to populate the dashboard with test data
"""

from metrics_client import SyncMetricsClient
import time
import random
import uuid
from datetime import datetime, timedelta

def test_tracking():
    client = SyncMetricsClient(base_url="http://localhost:8000")
    
    models = ["models/gemini-2.5-flash", "gpt-4", "claude-3"]
    teams = ["internal-chatbot-team", "customer-support", "research"]
    users = ["krrish@berri.ai", "user1@example.com", "user2@example.com"]
    
    print("🧪 Testing LLM Optimization Hub Metrics Backend")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Send 20 test requests
    for i in range(20):
        try:
            model = random.choice(models)
            team = random.choice(teams)
            user = random.choice(users)
            
            # Generate realistic metrics
            prompt_tokens = random.randint(10, 500)
            output_tokens = random.randint(50, 2000)
            total_tokens = prompt_tokens + output_tokens
            latency_ms = random.uniform(500, 25000)
            cache_hit = random.random() > 0.7
            
            result = client.track_request(
                model=model,
                prompt_tokens=prompt_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                user_id=user,
                request_id=str(uuid.uuid4()),
                team_alias=team,
                cache_hit=cache_hit,
                query_type=random.choice(["faq", "reasoning", "creative", "code"]),
                status="success"
            )
            
            print(f"✓ Request {i+1}/20")
            print(f"  Model: {model}")
            print(f"  Tokens: {total_tokens} | Cost: ${result.get('cost', 0):.6f} | Latency: {latency_ms:.2f}ms")
            print(f"  Team: {team} | User: {user}")
            print()
            
            time.sleep(0.5)  # Small delay between requests
        
        except Exception as e:
            print(f"❌ Error on request {i+1}: {str(e)}")
            continue
    
    # Test cache metrics
    print("\n📊 Sending cache metrics...")
    try:
        result = client.track_cache_metrics(
            cache_hit=150,
            cache_miss=50,
            avg_lookup_time_ms=2.5,
            team_alias="internal-chatbot-team"
        )
        print("✓ Cache metrics tracked")
        print(f"  Hit rate: {(150 / (150 + 50)) * 100:.1f}%")
    except Exception as e:
        print(f"❌ Error tracking cache metrics: {e}")
    
    # Test batch metrics
    print("\n📦 Sending batch metrics...")
    try:
        result = client.track_batch(
            batch_id=str(uuid.uuid4()),
            batch_size=10,
            total_tokens=5000,
            batch_cost=0.125,
            batch_latency_ms=3500,
            team_alias="internal-chatbot-team"
        )
        print("✓ Batch metrics tracked")
        print(f"  Batch size: 10 | Cost per query: ${0.125/10:.6f}")
    except Exception as e:
        print(f"❌ Error tracking batch metrics: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("\n📍 View metrics at: http://localhost:8000/static/dashboard.html")
    print("📚 API Docs at:     http://localhost:8000/docs")

if __name__ == "__main__":
    print("Waiting 5 seconds for backend to initialize...\n")
    time.sleep(5)
    test_tracking()
