# Adaptive Semantic Cache System for LLM Cost Optimization

A production-ready, dynamic semantic caching system that reduces LLM costs through intelligent query matching, adaptive thresholds, and value-based cache management.

## 🎯 Overview

This system demonstrates **real cost reduction** (not a toy cache) by:
- **Reducing redundant LLM calls** using FAISS-powered semantic similarity
- **Tracking token usage and cost savings** with detailed metrics
- **Real-time monitoring** via interactive Streamlit dashboard
- **Dynamically deciding what to cache** based on value scoring
- **Maintaining cache freshness** via intelligent eviction
- **Adapting thresholds and policies** based on observed usage patterns

## 🏗️ Architecture

```
User Query
   ↓
Normalize + Embed Query (models/embedding-001)
   ↓
FAISS Semantic Search (cosine similarity, 768-dim)
   ↓
Adaptive Similarity Threshold
   ↓
CACHE HIT ──→ Return Cached Response + Update Metrics
CACHE MISS ─→ Call LLM (gemini-2.0-flash)
                ↓
            Cost Tracking
                ↓
        Adaptive Cache Decision
                ↓
        Store (if high-value)
                ↓
        Eviction (if cache full)
```