# Integrated LLM Cost Optimizer

A unified system that combines **Prompt Optimization**, **Semantic Caching**, and **Request Batching** to reduce LLM costs while maintaining quality.

## 🎯 Overview

This system processes queries through a multi-stage pipeline:

```
User Prompt
    ↓
┌─────────────────────────┐
│   Prompt Optimizer      │  Clean, shorten, analyze
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   Semantic Cache        │  FAISS similarity search
│   HIT → Return cached   │
└─────────────────────────┘
    ↓ (MISS)
┌─────────────────────────┐
│   Model Selection       │  Cost-optimal model
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   Batching System       │  Group by model
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   LLM Service           │  Generate response
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   Cache Store           │  Save for future hits
└─────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup

```bash
cd integrated-cost-optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your GEMINI_API_KEY (optional - simulation mode works without it)
```

### 2. Run the Backend

```bash
uvicorn main:app --reload --port 8000
```

### 3. Run the Dashboard

```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501 for the dashboard.

## 📊 Features

### Query Tracking (Recent 20 Queries)
Each query is tracked with:
- Original & optimized prompt
- Cache hit/miss status
- Similarity score
- Selected model
- Token usage & cost
- Response time breakdown

### Semantic Cache
- **FAISS-powered** similarity search
- **Adaptive thresholds** based on query length
- **Value-based eviction** (not simple LRU)
- Real-time metrics

### Model Selection
- **11 models** across 5 providers (OpenAI, Anthropic, Google, DeepSeek, xAI)
- **Cost-first selection** - cheapest model that meets requirements
- Intent and complexity-aware routing

### Request Batching
- Model-wise grouping
- Adaptive wait times
- Token budget management

## 🔧 Configuration

Key settings in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key for Gemini | (required for real mode) |
| `SIMULATE_LLM` | Simulate LLM responses | `true` |
| `SIMULATE_EMBEDDINGS` | Use local embeddings | `false` |
| `MAX_CACHE_SIZE` | Max cache entries | `50` |

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Process query through pipeline |
| `/metrics` | GET | System-wide metrics |
| `/recent-queries` | GET | Last 20 queries with tracking |
| `/cache/stats` | GET | Cache statistics |
| `/cache/entries` | GET | View cache entries |
| `/batching/stats` | GET | Batching statistics |
| `/cache/clear` | POST | Clear cache |

## 📁 Project Structure

```
integrated-cost-optimizer/
├── main.py                 # FastAPI application
├── streamlit_app.py        # Dashboard
├── config.py               # Configuration
├── models.py               # Data models
├── prompt_optimizer/       # Prompt cleaning & analysis
├── cache/                  # Semantic cache with FAISS
├── batching/               # Model selection & batching
├── llm/                    # LLM service
└── pipeline/               # Orchestrator & tracker
```

## ⚠️ API Call Points

The system can operate in **simulation mode** (default) or **real API mode**:

| Component | API Used | Simulation Alternative |
|-----------|----------|----------------------|
| Prompt Shortening | Gemini | Rule-based patterns |
| Embeddings | Gemini embedding-001 | sentence-transformers (local) |
| LLM Response | Multi-provider | Realistic random responses |

To enable real APIs, set in `.env`:
```
SIMULATE_LLM=false
SIMULATE_EMBEDDINGS=false
GEMINI_API_KEY=your_key_here
```

## 📈 Metrics & Monitoring

The dashboard shows:
- **Real-time metrics**: Hit rate, cost, tokens
- **Recent 20 queries**: Complete tracking table
- **Cache details**: Entries, thresholds, evictions
- **Batching stats**: Batches by model
- **Cost analytics**: Savings visualization
