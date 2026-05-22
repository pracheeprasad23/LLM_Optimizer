from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MetricsEntry(Base):
    """Main metrics tracking table"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Model Information
    model = Column(String, index=True)
    model_tier = Column(String)  # "budget", "standard", "premium"
    
    # Token Metrics
    prompt_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    
    # Cost Metrics
    response_cost = Column(Float)
    prompt_cost = Column(Float)
    output_cost = Column(Float)
    
    # Performance Metrics
    latency_ms = Column(Float)
    time_to_first_token_ms = Column(Float)
    
    # Cache Metrics
    cache_hit = Column(Boolean, default=False)
    cache_similarity_score = Column(Float, nullable=True)
    
    # Batch Information
    is_batched = Column(Boolean, default=False)
    batch_id = Column(String, nullable=True, index=True)
    batch_size = Column(Integer, nullable=True)
    
    # Request Context
    request_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    end_user = Column(String, index=True, nullable=True)
    team_alias = Column(String, index=True, nullable=True)
    organization_alias = Column(String, index=True, nullable=True)
    key_alias = Column(String, index=True, nullable=True)
    
    # Query Metadata
    query_type = Column(String)  # "faq", "reasoning", "creative", "code", "general"
    query_complexity = Column(String)  # "simple", "moderate", "complex"
    batchable = Column(Boolean)
    
    # Response Status
    status = Column(String)  # "success", "error", "timeout"
    error_message = Column(String, nullable=True)
    
    # Additional Metadata
    additional_usage_values = Column(JSON, nullable=True)
    extra_metadata = Column("metadata", JSON, nullable=True)

class CacheMetrics(Base):
    """Cache performance tracking"""
    __tablename__ = "cache_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    cache_hit = Column(Integer, default=0)
    cache_miss = Column(Integer, default=0)
    cache_evictions = Column(Integer, default=0)
    
    avg_cache_lookup_time_ms = Column(Float)
    total_cached_queries = Column(Integer)
    cache_size_bytes = Column(Integer)
    
    team_alias = Column(String, index=True, nullable=True)

class BatchMetrics(Base):
    """Batch processing metrics"""
    __tablename__ = "batch_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    batch_id = Column(String, unique=True, index=True)
    batch_size = Column(Integer)
    total_tokens_in_batch = Column(Integer)
    batch_cost = Column(Float)
    batch_latency_ms = Column(Float)
    
    # Per-query cost when batched vs individual
    avg_cost_per_query_batched = Column(Float)
    estimated_cost_if_individual = Column(Float)
    
    status = Column(String)  # "pending", "processing", "completed", "failed"
    team_alias = Column(String, index=True, nullable=True)

class ModelMetrics(Base):
    """Model-level aggregated metrics"""
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    model = Column(String, index=True)
    
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0)
    avg_latency_ms = Column(Float, default=0)
    error_count = Column(Integer, default=0)
    
    avg_prompt_tokens = Column(Float, default=0)
    avg_output_tokens = Column(Float, default=0)
    
    team_alias = Column(String, index=True, nullable=True)

class DailyAggregates(Base):
    """Daily aggregated metrics for reporting"""
    __tablename__ = "daily_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)  # YYYY-MM-DD format
    
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0)
    
    avg_latency_ms = Column(Float, default=0)
    cache_hit_rate = Column(Float, default=0)
    error_rate = Column(Float, default=0)
    
    most_used_model = Column(String)
    cost_per_request = Column(Float, default=0)
    
    team_alias = Column(String, index=True, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
