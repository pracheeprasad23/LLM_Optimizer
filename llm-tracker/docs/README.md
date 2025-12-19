# LLM Cost & Resource Optimization System - Metrics Backend Integration Guide

## 📋 Project Overview

This is the **Monitoring & Metrics Tracking System** for your Cost and Resource Optimization project. It tracks:
- 💰 API costs per request
- ⏱️ Latency metrics (P50, P95, P99)
- 📊 Cache hit/miss rates
- 📦 Batch processing efficiency
- 🎯 Model usage distribution
- 👥 Per-team/user analytics

## 📁 Project Structure

```
llm-optimization-metrics/
├── main.py                 # FastAPI backend server
├── database.py             # SQLAlchemy models & database setup
├── metrics_tracker.py      # Core metrics tracking logic
├── metrics_client.py       # Client SDK for sending metrics
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── docker-compose.yml      # Docker compose setup (PostgreSQL + Redis + Prometheus + Grafana)
├── Dockerfile              # Docker image definition
├── prometheus.yml          # Prometheus configuration
├── README.md              # This file
└── dashboard.html         # Frontend dashboard (place in /static folder)
```

## 🚀 Quick Start

### Option 1: Docker (Recommended - Single Command)

```bash
# Clone or setup your project
cd llm-optimization-metrics

# Install Docker Desktop from https://www.docker.com/products/docker-desktop

# Start all services
docker-compose up -d

# Wait 30 seconds for services to initialize
sleep 30

# Access the services:
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Dashboard: http://localhost:8000/static/dashboard.html
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
```

### Option 2: Local Development (Manual Setup)

#### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (for frontend development)

#### Step 1: Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Setup Database

```bash
# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql

# Or on Linux/Windows, ensure PostgreSQL is running

# Create database
createdb llm_optimization

# User: llm_user, Password: password123 (configured in .env)
```

#### Step 3: Setup Redis
```bash
# Start Redis (macOS with Homebrew)
brew services start redis

# Or on Linux:
# redis-server

# Or on Windows with WSL:
# wsl redis-server
```

#### Step 4: Run Backend
```bash
# In the project directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Visit http://localhost:8000/docs for API documentation
```

#### Step 5: Run Frontend
```bash
# Copy dashboard.html to a static folder or open in browser
# http://localhost:8000/static/dashboard.html
```

## 📊 API Endpoints

### 1. Track Request Metrics
**POST** `/api/v1/metrics/track`

Send this from your **model selection module** after each inference:

```python
from metrics_client import SyncMetricsClient

client = SyncMetricsClient(base_url="http://localhost:8000")

# Track after model inference
result = client.track_request(
    model="models/gemini-2.5-flash",
    prompt_tokens=100,
    output_tokens=1746,
    total_tokens=1846,
    latency_ms=13596.617,
    user_id="krrish@berri.ai",
    team_alias="internal-chatbot-team",
    cache_hit=False,
    query_type="reasoning"
)
```

**Expected Response:**
```json
{
    "status": "success",
    "message": "Metrics tracked successfully",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "cost": 0.000567,
    "tokens": 1846
}
```

### 2. Get Dashboard Metrics
**GET** `/api/v1/dashboard/metrics`

```bash
# Get metrics for last 24 hours
curl http://localhost:8000/api/v1/dashboard/metrics?time_range_hours=24

# Filter by team
curl "http://localhost:8000/api/v1/dashboard/metrics?team_alias=internal-chatbot-team"

# Filter by model
curl "http://localhost:8000/api/v1/dashboard/metrics?model_filter=gpt-4"
```

**Response:**
```json
{
    "total_cost": 12.456,
    "total_tokens": 125000,
    "total_requests": 1240,
    "avg_latency_ms": 2500.5,
    "cache_hit_rate": 32.5,
    "error_rate": 0.5,
    "model_usage": {
        "gemini-2.5-flash": {
            "count": 620,
            "tokens": 75000,
            "cost": 8.125
        },
        "gpt-4": {
            "count": 380,
            "tokens": 42000,
            "cost": 3.780
        }
    },
    "hourly_trend": {
        "2025-12-18 12:00": {"cost": 0.52, "count": 52},
        "2025-12-18 13:00": {"cost": 0.48, "count": 48}
    }
}
```

### 3. Get Recent Requests
**GET** `/api/v1/requests/recent`

```bash
curl "http://localhost:8000/api/v1/requests/recent?limit=20"
```

### 4. Track Cache Metrics
**POST** `/api/v1/metrics/cache`

```python
client.track_cache_metrics(
    cache_hit=150,
    cache_miss=50,
    avg_lookup_time_ms=2.5,
    team_alias="internal-chatbot-team"
)
```

### 5. Track Batch Processing
**POST** `/api/v1/metrics/batch`

```python
client.track_batch(
    batch_id="batch_123",
    batch_size=10,
    total_tokens=5000,
    batch_cost=0.125,
    batch_latency_ms=3500,
    team_alias="internal-chatbot-team"
)
```

## 🔗 Integration with Your Model Selection Module

Your **model selection module** receives metrics like:
```python
{
    'model': 'models/gemini-2.5-flash',
    'prompt_tokens': 10,
    'output_tokens': 1746,
    'total_tokens': 1756,
    'latency_ms': 13596.617,
    'timestamp': '2025-12-14 19:37:14'
}
```

### How to Integrate:

1. **Import the client** in your model selection module:
```python
from metrics_client import SyncMetricsClient

# Initialize once at startup
metrics_client = SyncMetricsClient(base_url="http://localhost:8000")
```

2. **Track metrics** after each model call:
```python
# After your model inference completes
def get_model_response(user_query):
    import time
    import uuid
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Your model inference code
    response = model.invoke(user_query)
    
    latency_ms = (time.time() - start_time) * 1000
    
    # Track to metrics backend
    try:
        metrics_client.track_request(
            model="models/gemini-2.5-flash",
            prompt_tokens=len(user_query.split()),
            output_tokens=len(response.split()),
            total_tokens=len(user_query.split()) + len(response.split()),
            latency_ms=latency_ms,
            user_id="user@example.com",
            request_id=request_id,
            team_alias="your-team",
            cache_hit=False
        )
    except Exception as e:
        print(f"Failed to track metrics: {e}")
    
    return response
```

## 📈 Dashboard Features

The dashboard (`dashboard.html`) provides:

### Real-time KPIs (6 metrics)
- **Total Cost**: Cumulative API spend
- **Total Tokens**: Aggregate token usage
- **Avg Latency**: Average response time
- **Cache Hit Rate**: Cache effectiveness
- **Total Requests**: Request volume
- **Error Rate**: Failed request percentage

### Charts & Visualizations
1. **Cost Trend** - 24-hour spending pattern
2. **Model Distribution** - Token usage per model
3. **Token Usage by Model** - Bar chart breakdown
4. **Latency Distribution** - Bucketed latency analysis
5. **Cache Performance** - Hit vs miss comparison
6. **API Response Times** - P50, P95, P99 percentiles

### Interactive Features
- ⏱️ Time range selector (24H, 7D, 30D, Custom)
- 🔍 Model filter
- 👥 Team filter
- 💰 Minimum cost filter
- 🔄 Auto-refresh (30 seconds)
- 📊 Sortable requests table

## 🗄️ Database Schema

### metrics
Main table storing individual request metrics
- `id`, `timestamp`, `model`, `prompt_tokens`, `output_tokens`, `total_tokens`
- `response_cost`, `prompt_cost`, `output_cost`
- `latency_ms`, `time_to_first_token_ms`
- `cache_hit`, `cache_similarity_score`
- `is_batched`, `batch_id`, `batch_size`
- `user_id`, `team_alias`, `end_user`, `status`, `error_message`

### cache_metrics
Cache performance aggregates
- `timestamp`, `cache_hit`, `cache_miss`, `avg_cache_lookup_time_ms`

### batch_metrics
Batch processing details
- `batch_id`, `batch_size`, `total_tokens`, `batch_cost`, `status`

### model_metrics
Model-level aggregations
- Per-model totals: requests, tokens, cost, latency

### daily_aggregates
Daily rollups for trend analysis
- Date-level summaries of all metrics

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://llm_user:password123@localhost:5432/llm_optimization

# API
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development

# Cache
REDIS_URL=redis://localhost:6379/0

# Monitoring
LOG_LEVEL=INFO
ENABLE_TELEMETRY=true
```

### Update Model Pricing

In `metrics_tracker.py`, update the `_calculate_cost()` method:

```python
pricing = {
    "models/gemini-2.5-flash": {"prompt": 0.000075, "output": 0.0003},
    "gpt-4": {"prompt": 0.00003, "output": 0.0006},
    # Add your actual pricing here
}
```

## 📚 Example: Complete Integration

```python
# In your model selection module (model_selector.py)

from metrics_client import SyncMetricsClient
import time
import uuid

class ModelSelector:
    def __init__(self):
        self.metrics_client = SyncMetricsClient(
            base_url="http://localhost:8000"
        )
    
    def select_and_invoke(self, query, user_id, team_alias):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Your logic to select model
        model = self.select_best_model(query)
        
        # Invoke model
        response = self.invoke_model(model, query)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Track metrics
        self.metrics_client.track_request(
            model=model,
            prompt_tokens=len(query.split()),
            output_tokens=len(response.split()),
            total_tokens=len(query.split()) + len(response.split()),
            latency_ms=latency_ms,
            user_id=user_id,
            request_id=request_id,
            team_alias=team_alias,
            status="success"
        )
        
        return response
```

## 🐛 Troubleshooting

### Backend not connecting to database
```bash
# Check PostgreSQL is running
psql -U llm_user -d llm_optimization -c "SELECT 1;"

# Reset database
dropdb llm_optimization
createdb llm_optimization
```

### Dashboard showing no data
1. Ensure backend is running: `http://localhost:8000/docs`
2. Send test metrics:
```bash
curl -X POST http://localhost:8000/api/v1/metrics/track \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-2.5-flash","prompt_tokens":10,"output_tokens":100,"total_tokens":110,"latency_ms":1000,"user_id":"test"}'
```

### CORS errors
Backend has CORS enabled for all origins. If issues persist:
```python
# In main.py, update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-domain"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📖 Next Steps

1. ✅ Start backend with Docker or locally
2. ✅ Integrate `metrics_client.py` into your model selection module
3. ✅ Send first test metrics
4. ✅ View dashboard at `http://localhost:8000/static/dashboard.html`
5. ✅ Setup Grafana dashboards for deeper analytics
6. ✅ Configure alerts based on cost thresholds

## 📞 Support

For issues or questions:
- Check FastAPI docs: `http://localhost:8000/docs`
- Review metrics_client.py for usage examples
- Check logs: `docker-compose logs backend`

---

**Created for IIT Madras MLOps & Cost Optimization Project**
