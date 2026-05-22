# 🚀 LLM Optimization Hub - Complete Setup Summary

## 📋 What You're Getting

A **production-ready metrics tracking system** for your LLM Cost & Resource Optimization project.

### Features Included:
✅ Real-time cost tracking  
✅ Latency monitoring (P50, P95, P99)  
✅ Cache hit/miss rates  
✅ Batch efficiency metrics  
✅ Per-model analytics  
✅ Team-based reporting  
✅ Dashboard with 6 KPI cards + 6 charts  
✅ Recent requests table  
✅ Interactive filters  
✅ REST API for integration  

---

## 📁 All Files Created (12 files)

### Backend Application Files (4)
1. **main.py** - FastAPI server with API endpoints
2. **database.py** - SQLAlchemy models for PostgreSQL
3. **metrics_tracker.py** - Core tracking and aggregation logic
4. **metrics_client.py** - Python SDK to send metrics

### Configuration Files (5)
5. **requirements.txt** - Python dependencies
6. **.env** - Environment variables
7. **docker-compose.yml** - Full stack (PostgreSQL, Redis, Prometheus, Grafana)
8. **Dockerfile** - Container image definition
9. **prometheus.yml** - Monitoring configuration

### Utility Scripts (2)
10. **start.sh** - One-command startup (Mac/Linux)
11. **test_metrics.py** - Demo script to populate dashboard

### Documentation (1)
12. **.gitignore** - Git configuration

---

## 🎯 Quick Start (Choose One)

### Option 1: Docker (Recommended - 2 minutes)

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows (PowerShell as Admin):**
```bash
docker-compose up -d
```

### Option 2: Manual Setup (Local Development)

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
# OR
venv\Scripts\activate          # Windows

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Access Your Services

Once running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://localhost:8000/static/dashboard.html | Real-time metrics visualization |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Service status |
| **Grafana** | http://localhost:3000 | Advanced analytics (admin/admin) |
| **Prometheus** | http://localhost:9090 | Metrics storage |

---

## 🔗 Integration with Your Code

### In Your Model Selection Module:

```python
from metrics_client import SyncMetricsClient
import time

# Initialize once
metrics_client = SyncMetricsClient(base_url="http://localhost:8000")

# After model inference:
start = time.time()
response = model.invoke(user_query)
latency = (time.time() - start) * 1000

# Track metrics (this is all you need!)
metrics_client.track_request(
    model="models/gemini-2.5-flash",
    prompt_tokens=len(user_query.split()),
    output_tokens=len(response.split()),
    total_tokens=len(user_query.split()) + len(response.split()),
    latency_ms=latency,
    user_id="krrish@berri.ai",
    team_alias="internal-chatbot-team"
)
```

---

## 📊 API Reference

### Main Endpoints

**Track a Request:**
```bash
POST /api/v1/metrics/track
{
    "model": "models/gemini-2.5-flash",
    "prompt_tokens": 100,
    "output_tokens": 1746,
    "total_tokens": 1846,
    "latency_ms": 13596.617,
    "user_id": "user@example.com",
    "team_alias": "internal-chatbot-team"
}
```

**Get Dashboard Metrics:**
```bash
GET /api/v1/dashboard/metrics?time_range_hours=24&team_alias=internal-chatbot-team
```

**Get Recent Requests:**
```bash
GET /api/v1/requests/recent?limit=50
```

**Track Cache Metrics:**
```bash
POST /api/v1/metrics/cache
{
    "cache_hit": 150,
    "cache_miss": 50,
    "avg_lookup_time_ms": 2.5,
    "team_alias": "internal-chatbot-team"
}
```

**Track Batch Processing:**
```bash
POST /api/v1/metrics/batch
{
    "batch_id": "batch_123",
    "batch_size": 10,
    "total_tokens": 5000,
    "batch_cost": 0.125,
    "batch_latency_ms": 3500
}
```

---

## 📈 Dashboard Components

### KPI Cards (6 metrics)
- **Total Cost**: Cumulative API spend
- **Total Tokens**: Aggregate token usage  
- **Avg Latency**: Average response time
- **Cache Hit Rate**: Cache effectiveness
- **Total Requests**: Request volume
- **Error Rate**: Failed request percentage

### Charts (6 visualizations)
1. **Cost Trend** (24H) - Line chart of spending
2. **Model Distribution** - Pie chart of token usage
3. **Token Usage by Model** - Bar chart comparison
4. **Latency Distribution** - Bucketed analysis
5. **Cache Performance** - Hit vs miss comparison
6. **API Response Times** - P50, P95, P99

### Interactive Features
- Time range selector (24H, 7D, 30D, Custom)
- Model filter dropdown
- Team filter dropdown
- Minimum cost filter
- Auto-refresh (30 seconds)
- Sortable recent requests table

---

## 🗄️ Database Schema

### metrics table (Main)
Stores individual request tracking:
- request_id, timestamp, model, user_id
- prompt_tokens, output_tokens, total_tokens
- response_cost, prompt_cost, output_cost
- latency_ms, cache_hit, is_batched
- team_alias, organization_alias, status

### cache_metrics table
Cache performance tracking:
- cache_hit, cache_miss, avg_lookup_time_ms
- total_cached_queries, team_alias

### batch_metrics table
Batch processing details:
- batch_id, batch_size, total_tokens
- batch_cost, batch_latency_ms, status

### model_metrics table
Model-level aggregations:
- model, total_requests, total_tokens
- total_cost, avg_latency_ms, error_count

### daily_aggregates table
Daily rollups for trends:
- date, total_cost, total_tokens
- cache_hit_rate, error_rate

---

## 🔧 Configuration

### Update Model Pricing

Edit `metrics_tracker.py`, method `_calculate_cost()`:

```python
pricing = {
    "models/gemini-2.5-flash": {"prompt": 0.000075, "output": 0.0003},
    "gpt-4": {"prompt": 0.00003, "output": 0.0006},
    "gpt-4-turbo": {"prompt": 0.00001, "output": 0.00003},
    "gpt-3.5-turbo": {"prompt": 0.0000005, "output": 0.0000015},
    "claude-3-opus": {"prompt": 0.000015, "output": 0.000075},
    "claude-3-sonnet": {"prompt": 0.000003, "output": 0.000015},
}
```

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

# Logging
LOG_LEVEL=INFO
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 already in use | Change `API_PORT` in `.env` or kill process: `lsof -i :8000` |
| Database connection failed | Ensure PostgreSQL is running and URL is correct |
| Docker containers won't start | Run `docker-compose down -v` then `docker-compose up -d` |
| No data in dashboard | Run `python test_metrics.py` to send test data |
| Backend logs | `docker-compose logs -f backend` |
| Permission denied on start.sh | Run `chmod +x start.sh` first |

---

## ✅ Verification Checklist

After setup, verify everything:

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Send test data
python test_metrics.py

# 3. Check API docs
# Open: http://localhost:8000/docs

# 4. View dashboard
# Open: http://localhost:8000/static/dashboard.html

# 5. Verify database
# Run: python -c "from database import engine; print(engine)"
```

Expected outputs:
- ✅ Health check returns `{"status":"healthy"}`
- ✅ Test script shows 20 "✓ Request" messages
- ✅ API docs load with Swagger UI
- ✅ Dashboard shows charts and data
- ✅ Database connection successful

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Full technical documentation |
| **SETUP.md** | Step-by-step installation guide |
| **FILES.md** | Complete file listing and purposes |
| **This file** | Quick reference summary |

---

## 🎓 Example: Complete Integration

```python
# your_model_selection_module.py

from metrics_client import SyncMetricsClient
import time
import uuid

class ModelSelector:
    def __init__(self):
        self.metrics_client = SyncMetricsClient(
            base_url="http://localhost:8000"
        )
    
    def process_query(self, query, user_id, team_id):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Your model selection logic
        selected_model = self.select_model(query)
        response = self.invoke_model(selected_model, query)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Track metrics (automatic cost calculation!)
        self.metrics_client.track_request(
            model=selected_model,
            prompt_tokens=len(query.split()),
            output_tokens=len(response.split()),
            total_tokens=len(query.split()) + len(response.split()),
            latency_ms=latency_ms,
            user_id=user_id,
            request_id=request_id,
            team_alias=team_id,
            query_type="reasoning",
            status="success"
        )
        
        return response
```

---

## 🚀 Next Steps

1. ✅ **Run startup:** `./start.sh` or `docker-compose up -d`
2. ✅ **Verify:** `curl http://localhost:8000/health`
3. ✅ **Send test data:** `python test_metrics.py`
4. ✅ **View dashboard:** http://localhost:8000/static/dashboard.html
5. ✅ **Integrate client:** Import `metrics_client.py` in your module
6. ✅ **Start tracking:** Call `client.track_request()` after inference
7. ✅ **Monitor:** Watch metrics update in real-time on dashboard
8. ✅ **Optimize:** Use data to improve model routing and reduce costs

---

## 📞 Support Resources

- **API Documentation:** http://localhost:8000/docs
- **Full README:** See README.md file
- **Setup Guide:** See SETUP.md file
- **File Reference:** See FILES.md file
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy Docs:** https://www.sqlalchemy.org/

---

## 💡 Pro Tips

1. **Use Docker** - Simplest setup, includes everything
2. **Test First** - Run `python test_metrics.py` to verify setup
3. **Monitor Costs** - Set up cost alerts in Grafana
4. **Use Teams** - Tag requests by team for better analytics
5. **Batch Wisely** - Track batch metrics to measure batch efficiency
6. **Cache Aggressively** - Monitor cache hit rates for optimization

---

**You're ready to go! 🎉**

Your LLM Cost Optimization system is now tracking metrics in real-time. Start by sending metrics from your model selection module and watch your dashboard light up with data!

Questions? Check the documentation files or API docs at http://localhost:8000/docs

---

*Created for IIT Madras Cost & Resource Optimization in LLM Agents*
