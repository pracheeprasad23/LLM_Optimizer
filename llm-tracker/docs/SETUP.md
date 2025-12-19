# 📦 SETUP INSTRUCTIONS FOR VS CODE

This guide will help you set up the entire LLM Optimization Metrics Backend in VS Code.

## 📋 What You Have

The following files are included:

```
Backend Files:
├── main.py                  # FastAPI server (API endpoints)
├── database.py              # SQLAlchemy database models
├── metrics_tracker.py       # Core metrics tracking logic
├── metrics_client.py        # Python client SDK to send metrics
│
Configuration Files:
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── docker-compose.yml       # Docker setup (PostgreSQL, Redis, Prometheus, Grafana)
├── Dockerfile               # Container image definition
├── prometheus.yml           # Prometheus configuration
│
Scripts:
├── start.sh                # One-command startup script (Mac/Linux)
├── test_metrics.py         # Test script to send sample metrics
│
Documentation:
├── README.md               # Full documentation
└── SETUP.md               # This file
```

## 🎯 Step-by-Step Setup

### Step 1: Install Prerequisites (5 minutes)

**Option A: Using Docker (Recommended - Easiest)**

1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and launch Docker Desktop
3. Open VS Code terminal

**Option B: Manual Installation (For Local Development)**

- Python 3.9+: https://www.python.org/downloads/
- PostgreSQL: https://www.postgresql.org/download/
- Redis: https://redis.io/download (or `brew install redis` on Mac)

### Step 2: Open Project in VS Code

```bash
# Open VS Code and create a new folder
mkdir llm-optimization-metrics
cd llm-optimization-metrics

# Create all the files from the list above in this folder
# You can copy-paste the content from each file provided
```

### Step 3A: Quick Start with Docker (2 minutes)

**On Mac/Linux:**
```bash
# Make script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

**On Windows (using PowerShell as Admin):**
```bash
# Start Docker services
docker-compose up -d

# Wait 30 seconds
timeout /t 30

# Check status
docker-compose ps
```

**Expected Output:**
```
NAME            STATUS
llm_postgres    Up (healthy)
llm_redis       Up (healthy)
llm_backend     Up
llm_prometheus  Up
llm_grafana     Up
```

### Step 3B: Manual Local Setup (10 minutes)

```bash
# Step 1: Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Start PostgreSQL
# Mac with Homebrew:
brew services start postgresql

# Linux (if not already running):
sudo systemctl start postgresql

# Windows:
# Start PostgreSQL from Services or installation folder

# Step 4: Create database
createdb -U postgres llm_optimization

# Step 5: Start Redis
# Mac with Homebrew:
brew services start redis

# Linux:
sudo systemctl start redis-server

# Windows with WSL:
wsl redis-server

# Step 6: Run the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test the Backend

In a new VS Code terminal:

```bash
# Test if backend is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2025-12-18T..."}

# View API documentation
# Open browser: http://localhost:8000/docs
```

### Step 5: Send Test Metrics

```bash
# In VS Code terminal
python test_metrics.py

# Expected output:
# 🧪 Testing LLM Optimization Hub Metrics Backend
# ✓ Request 1/20
# ✓ Request 2/20
# ... and so on
```

### Step 6: View Dashboard

Open in browser: **http://localhost:8000/static/dashboard.html**

You should see:
- ✓ Real-time cost metrics
- ✓ Recent requests table
- ✓ Charts and graphs
- ✓ Live filters

## 🔗 Integration Guide (For Your Model Selection Module)

### How to Send Metrics from Your Code

**Step 1: Import the client**
```python
from metrics_client import SyncMetricsClient

# Initialize once
metrics_client = SyncMetricsClient(base_url="http://localhost:8000")
```

**Step 2: Track metrics after model inference**
```python
import time
import uuid

# In your model selection module
def inference(query, user_id):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Your model inference
    response = model.generate(query)  # Your actual code
    
    latency_ms = (time.time() - start_time) * 1000
    
    # Track metrics
    metrics_client.track_request(
        model="models/gemini-2.5-flash",
        prompt_tokens=len(query.split()),
        output_tokens=len(response.split()),
        total_tokens=len(query.split()) + len(response.split()),
        latency_ms=latency_ms,
        user_id=user_id,
        request_id=request_id,
        team_alias="your-team"
    )
    
    return response
```

That's it! Your metrics will appear in the dashboard in real-time.

## 🚨 Common Issues & Solutions

### Issue 1: "Connection refused" on localhost:8000

**Solution:**
```bash
# Make sure backend is running
docker-compose ps

# Or if using manual setup:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 2: Database connection error

```bash
# Reset database
dropdb llm_optimization
createdb llm_optimization

# Restart backend
docker-compose restart backend
```

### Issue 3: Port already in use

```bash
# Change port in .env:
API_PORT=8001

# Or kill process:
# Mac/Linux:
lsof -i :8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 4: Dashboard shows no data

```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Send test data
python test_metrics.py

# 3. Refresh dashboard
# Press Ctrl+Shift+R (hard refresh)
```

## 📊 Understanding the System Architecture

```
Your Model Selection Module
            ↓
        (sends metrics with)
        model, tokens, latency
            ↓
    metrics_client.py
    (Python HTTP client)
            ↓
    FastAPI Backend (main.py)
    POST /api/v1/metrics/track
            ↓
    Database (PostgreSQL)
    Storage in "metrics" table
            ↓
    MetricsAggregator
    Aggregates & processes
            ↓
    Dashboard (HTML/JavaScript)
    Real-time visualization
```

## 🎮 API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/metrics/track` | Track a single request |
| POST | `/api/v1/metrics/cache` | Track cache metrics |
| POST | `/api/v1/metrics/batch` | Track batch metrics |
| GET | `/api/v1/dashboard/metrics` | Get aggregated metrics |
| GET | `/api/v1/requests/recent` | Get recent requests |
| GET | `/health` | Health check |
| GET | `/docs` | API documentation |

## 📂 File Organization in VS Code

Organize your files like this:

```
llm-optimization-metrics/
├── Backend Scripts
│   ├── main.py
│   ├── database.py
│   ├── metrics_tracker.py
│   └── metrics_client.py
│
├── Configuration
│   ├── .env
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── prometheus.yml
│
├── Scripts
│   ├── start.sh
│   └── test_metrics.py
│
└── Documentation
    ├── README.md
    └── SETUP.md
```

## 🔄 Development Workflow

### When Developing:

```bash
# 1. Open terminal in VS Code
# Ctrl + ` (backtick)

# 2. Start backend with auto-reload
uvicorn main:app --reload

# 3. In another terminal, run tests
python test_metrics.py

# 4. View dashboard
# http://localhost:8000/static/dashboard.html

# 5. Make changes to code - auto-reloads
# Refresh dashboard to see new data
```

### When Deploying to Production:

1. Use docker-compose for easy deployment
2. Update `.env` with production database URL
3. Set `API_ENV=production`
4. Use docker-compose up -d (runs in background)

## 📞 Quick Commands Reference

```bash
# View all running services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Stop all services
docker-compose down

# Stop one service
docker-compose stop backend

# Restart all services
docker-compose restart

# Remove all containers and volumes
docker-compose down -v

# Access PostgreSQL directly
docker-compose exec postgres psql -U llm_user -d llm_optimization

# Access Redis directly
docker-compose exec redis redis-cli
```

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend running: `curl http://localhost:8000/health` → returns `{"status":"healthy"}`
- [ ] API docs accessible: Open `http://localhost:8000/docs`
- [ ] Test data sent: `python test_metrics.py` → shows "✓" checkmarks
- [ ] Dashboard loads: Open `http://localhost:8000/static/dashboard.html`
- [ ] Data visible in dashboard: Charts and tables show data
- [ ] Filters work: Try model/team filters on dashboard

## 🎓 Next Steps

1. ✅ Backend is set up and running
2. ✅ Metrics can be sent via Python client
3. ✅ Dashboard shows real-time data
4. **Next:** Integrate client into your model selection module
5. **Next:** Configure custom pricing in `metrics_tracker.py`
6. **Next:** Set up Grafana dashboards for deeper analytics
7. **Next:** Configure alerts for high costs

## 📖 Useful Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Docker: https://docs.docker.com/
- PostgreSQL: https://www.postgresql.org/docs/
- Prometheus: https://prometheus.io/docs/

## 🚀 You're Ready!

You now have a production-ready LLM metrics tracking system. Start using it to:
- 💰 Monitor API costs
- ⚡ Track performance
- 📊 Analyze usage patterns
- 🎯 Optimize routing

---

**Need help?** Check README.md for detailed documentation or API docs at http://localhost:8000/docs
