"""
Test script for the integrated LLM Optimization Pipeline

Demonstrates the complete flow with checkpoints and output examples.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add integration directory to path so we can import orchestrator
integration_dir = Path(__file__).parent
if str(integration_dir) not in sys.path:
    sys.path.insert(0, str(integration_dir))

# Import orchestrator
from orchestrator import OptimizationOrchestrator


async def test_single_query():
    """Test a single query through the pipeline"""
    
    print("\n" + "="*70)
    print("LLM Optimization Pipeline - Integration Test")
    print("="*70)
    
    # Get API key from .env file (loaded automatically)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("\nWARNING: GEMINI_API_KEY not found in .env file")
        print("   Please add GEMINI_API_KEY=your-key to .env file")
        print("   Cache and optimization will work, but LLM execution will be skipped\n")
    else:
        print("OK: API key loaded from .env file\n")
    
    # Initialize orchestrator (will auto-load from .env if not provided)
    orchestrator = OptimizationOrchestrator(
        enable_cache=True,
        enable_batching=False,
        gemini_api_key=gemini_api_key
    )
    
    # Test query - designed to select Gemini Flash (simple, low complexity, low latency)
    # Flash models are favored for: low complexity, low latency tolerance, simple queries
    test_prompt = "What is Python?"
    
    print("Input Prompt:")
    print(f"   {test_prompt}")
    print("\n" + "-"*70)
    
    # Process query
    result = await orchestrator.process_query(
        user_prompt=test_prompt,
        user_id="test_user",
        request_id="test_001"
    )
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print("\nResponse Generated:")
    if result["response"]:
        response_preview = result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"]
        print(f"   {response_preview}")
    else:
        print("   (No response - execution skipped or failed)")
    
    print("\nOptimization Metrics:")
    opt = result["optimization"]
    print(f"   Original length: {opt['original_prompt_length']} chars")
    print(f"   Optimized length: {opt['optimized_prompt_length']} chars")
    print(f"   Intent: {opt['analysis'].get('intent_type')}")
    print(f"   Complexity: {opt['analysis'].get('complexity_level')}")
    
    print("\nModel Selection:")
    model = result["model"]
    selected_model = model['selected']
    print(f"   Selected: {selected_model}")
    print(f"   Reason: {model['rationale']}")
    
    # Check if Gemini model was selected
    if "gemini" in selected_model.lower():
        print(f"   ✓ GEMINI MODEL SELECTED - API key will be used!")
    else:
        print(f"   ⚠ Non-Gemini model selected - execution may be skipped")
    
    print("\nCache Status:")
    cache = result["cache"]
    cache_status = "HIT" if cache["hit"] else "MISS"
    print(f"   Status: {cache_status}")
    if cache["similarity_score"]:
        print(f"   Similarity: {cache['similarity_score']:.4f}")
    print(f"   Stored: {'Yes' if cache['stored'] else 'No'}")
    
    print("\nExecution Metrics:")
    metrics = result["metrics"]
    print(f"   Status: {metrics.get('status', 'unknown')}")
    if metrics.get("prompt_tokens"):
        print(f"   Tokens: {metrics['prompt_tokens']} in, {metrics.get('output_tokens', 0)} out")
        print(f"   Cost: ${metrics.get('cost_usd', 0):.6f}")
        print(f"   Latency: {metrics.get('latency_ms', 0):.2f}ms")
    
    print("\nStage Timings:")
    stages = result["stages"]
    for stage, time_ms in stages.items():
        if stage != "total_ms":
            print(f"   {stage}: {time_ms:.2f}ms")
    print(f"   Total: {stages.get('total_ms', 0):.2f}ms")
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
    
    return result


async def test_cache_hit():
    """Test cache hit scenario (same query twice)"""
    
    print("\n" + "="*70)
    print("Cache Hit Test")
    print("="*70)
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    orchestrator = OptimizationOrchestrator(
        enable_cache=True,
        gemini_api_key=gemini_api_key
    )
    
    # Simple prompt that should select Gemini Flash
    # Simple prompt that should select Gemini Flash (low complexity, low latency)
    test_prompt = "What is machine learning?"
    
    print("\nFirst Request (should be MISS):")
    result1 = await orchestrator.process_query(test_prompt, request_id="cache_test_1")
    print(f"   Cache: {'HIT' if result1['cache']['hit'] else 'MISS'}")
    
    print("\nSecond Request (should be HIT):")
    result2 = await orchestrator.process_query(test_prompt, request_id="cache_test_2")
    print(f"   Cache: {'HIT' if result2['cache']['hit'] else 'MISS'}")
    
    if result2['cache']['hit']:
        print("   OK: Cache working correctly!")
    else:
        print("   WARNING: Expected cache hit but got miss")
        if result2['cache'].get('similarity_score'):
            print(f"   Best similarity: {result2['cache']['similarity_score']:.4f}")


async def main():
    """Run all tests"""
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        print("\n" + "="*70)
        print("WARNING: GEMINI_API_KEY not found in .env file")
        print("="*70)
        print("Please add GEMINI_API_KEY=your-key to .env file")
        print("Tests will run but LLM execution will be skipped\n")
    
    # Test 1: Single query with Gemini model
    print("\n" + "🔵 TEST 1: Gemini Model Test")
    print("="*70)
    await test_single_query()
    
    # Test 2: Cache hit (only if API key available)
    if gemini_api_key:
        print("\n" + "🔵 TEST 2: Cache Hit Test")
        await test_cache_hit()
    else:
        print("\n" + "="*70)
        print("Skipping Cache Hit test (GEMINI_API_KEY required)")
        print("="*70)
    
    # Dashboard instructions
    print("\n" + "="*70)
    print("📊 DASHBOARD ACCESS")
    print("="*70)
    print("\nTo view the metrics dashboard:")
    print("1. Start the metrics backend (if not running):")
    print("   cd llm-tracker/backend")
    print("   uvicorn main:app --reload --port 8000")
    print("\n2. Open dashboard in browser:")
    print("   http://localhost:8000/static/dashboard.html")
    print("\n3. The dashboard shows:")
    print("   - Total cost, tokens, requests")
    print("   - Cache hit rates")
    print("   - Model usage distribution")
    print("   - Latency metrics")
    print("   - Recent requests table")
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(main())
