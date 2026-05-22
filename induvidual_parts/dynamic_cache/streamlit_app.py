"""
Streamlit Dashboard for Adaptive Semantic Cache System
Real-time monitoring and analytics
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import json

# Page config
st.set_page_config(
    page_title="Cache Monitor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = st.sidebar.text_input("Backend URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .cache-hit {
        color: #28a745;
        font-weight: bold;
    }
    .cache-miss {
        color: #dc3545;
        font-weight: bold;
    }
    .evicted {
        color: #ffc107;
        font-weight: bold;
    }
    
    /* Style metric containers */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetric"] label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: bold;
    }
    
    /* Different gradient colors for variety */
    [data-testid="column"]:nth-child(1) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="column"]:nth-child(2) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    [data-testid="column"]:nth-child(3) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    [data-testid="column"]:nth-child(4) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    [data-testid="column"]:nth-child(5) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    /* Style section headers */
    h1, h2, h3 {
        color: #1f1f1f;
        font-weight: 700;
    }
    
    /* Style dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Style expander */
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-radius: 8px;
        border: 2px solid #f39c12;
        padding: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    [data-testid="stExpander"] [data-testid="StyledLinkIconContainer"] {
        color: #2c3e50 !important;
    }
    
    [data-testid="stExpander"] p, [data-testid="stExpander"] div {
        color: #2c3e50 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for history
if 'request_history' not in st.session_state:
    st.session_state.request_history = []
if 'eviction_history' not in st.session_state:
    st.session_state.eviction_history = []
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = []

# Helper functions
def fetch_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {str(e)}")
        return None

def send_query(query_text, max_tokens=500, temperature=0.7):
    """Send query to backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={
                "query": query_text,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error sending query: {str(e)}")
        return None

def clear_cache():
    """Clear all cache entries"""
    try:
        response = requests.post(f"{API_BASE_URL}/cache/clear", timeout=5)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error clearing cache: {str(e)}")
        return False

# Sidebar
st.sidebar.title("🚀 Cache Control Panel")
st.sidebar.markdown("---")

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=False)
if auto_refresh:
    time.sleep(5)
    st.rerun()

# Manual refresh button
if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
    st.rerun()

# Clear cache button
if st.sidebar.button("🗑️ Clear Cache", use_container_width=True):
    if clear_cache():
        st.sidebar.success("Cache cleared!")
        time.sleep(1)
        st.rerun()

st.sidebar.markdown("---")

# Fetch all data
metrics_data = fetch_data("/metrics")
stats_data = fetch_data("/cache/stats")
entries_data = fetch_data("/cache/entries")

# Main title
st.title("🎯 Adaptive Semantic Cache System - Real-Time Monitor")
st.markdown("---")

# Check if backend is accessible
if metrics_data is None:
    st.error("❌ Cannot connect to backend. Make sure the server is running!")
    st.stop()

# Extract metrics
metrics = metrics_data.get('metrics', {})
optimizer_data = metrics_data.get('optimizer', {})
config_data = metrics_data.get('config', {})

# Store metrics history
st.session_state.metrics_history.append({
    'timestamp': datetime.now(),
    'total_requests': metrics.get('total_requests', 0),
    'cache_hits': metrics.get('cache_hits', 0),
    'cache_misses': metrics.get('cache_misses', 0)
})

# Keep only last 100 records
if len(st.session_state.metrics_history) > 100:
    st.session_state.metrics_history = st.session_state.metrics_history[-100:]

# ============================================================================
# SECTION 1: KEY METRICS OVERVIEW
# ============================================================================
st.header("📊 Real-Time Metrics Overview")

col1, col2, col3, col4, col5 = st.columns(5)

total_requests = metrics.get('total_requests', 0)
cache_hits = metrics.get('cache_hits', 0)
cache_misses = metrics.get('cache_misses', 0)
hit_rate = metrics.get('hit_rate', 0.0) * 100
cache_size = metrics.get('cache_size', 0)

with col1:
    st.metric(
        "Total Requests",
        f"{total_requests:,}",
        delta=None
    )

with col2:
    st.metric(
        "Cache Hits",
        f"{cache_hits:,}",
        delta=None,
        delta_color="normal"
    )

with col3:
    st.metric(
        "Cache Misses",
        f"{cache_misses:,}",
        delta=None,
        delta_color="inverse"
    )

with col4:
    st.metric(
        "Hit Rate",
        f"{hit_rate:.1f}%",
        delta=None
    )

with col5:
    st.metric(
        "Cache Size",
        f"{cache_size}/{config_data.get('MAX_CACHE_SIZE', 50)}",
        delta=None
    )

# ============================================================================
# SECTION 2: COST & TOKEN METRICS
# ============================================================================
st.markdown("---")
st.header("💰 Cost & Token Analytics")

col1, col2, col3 = st.columns(3)

llm_tokens_used = metrics.get('llm_tokens_used', 0)
llm_tokens_saved = metrics.get('llm_tokens_saved', 0)
total_cost = metrics.get('total_cost', 0.0)
total_cost_saved = metrics.get('total_cost_saved', 0.0)
total_tokens = llm_tokens_used + llm_tokens_saved
savings_rate = (llm_tokens_saved / total_tokens * 100) if total_tokens > 0 else 0

with col1:
    st.metric("LLM Tokens Used", f"{llm_tokens_used:,}")
    st.metric("LLM Tokens Saved", f"{llm_tokens_saved:,}")
    st.metric("Total Tokens", f"{total_tokens:,}")

with col2:
    st.metric("Total Cost", f"${total_cost:.6f}")
    st.metric("Total Saved", f"${total_cost_saved:.6f}")
    st.metric("Total Budget", f"${(total_cost + total_cost_saved):.6f}")

with col3:
    st.metric("Token Savings Rate", f"{savings_rate:.1f}%")
    cost_efficiency = (total_cost_saved / (total_cost + total_cost_saved) * 100) if (total_cost + total_cost_saved) > 0 else 0
    st.metric("Cost Efficiency", f"{cost_efficiency:.1f}%")
    evictions = metrics.get('evictions', 0)
    st.metric("Total Evictions", f"{evictions}")

# ============================================================================
# SECTION 3: REAL-TIME CHARTS
# ============================================================================
st.markdown("---")
st.header("📈 Performance Trends")

if len(st.session_state.metrics_history) > 1:
    df_history = pd.DataFrame(st.session_state.metrics_history)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Requests over time
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_history['timestamp'],
            y=df_history['total_requests'],
            mode='lines+markers',
            name='Total Requests',
            line=dict(color='#1f77b4', width=2)
        ))
        fig1.update_layout(
            title="Total Requests Over Time",
            xaxis_title="Time",
            yaxis_title="Requests",
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Hit rate over time
        df_history['hit_rate'] = (df_history['cache_hits'] / df_history['total_requests'] * 100).fillna(0)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_history['timestamp'],
            y=df_history['hit_rate'],
            mode='lines+markers',
            name='Hit Rate',
            line=dict(color='#2ca02c', width=2),
            fill='tozeroy'
        ))
        fig2.update_layout(
            title="Cache Hit Rate Over Time",
            xaxis_title="Time",
            yaxis_title="Hit Rate (%)",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

# ============================================================================
# SECTION 4: FAISS INDEX INFORMATION
# ============================================================================
st.markdown("---")
st.header("🔍 FAISS Index Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Index Type", "IndexFlatIP (Cosine)")
    st.metric("Embedding Dimension", config_data.get('EMBEDDING_DIM', 768))

with col2:
    st.metric("Total Vectors", cache_size)
    st.metric("Embedding Model", config_data.get('EMBEDDING_MODEL', 'embedding-001'))

with col3:
    # avg_search_latency = stats_data.get('stats', {}).get('avg_latency_ms', 0) if stats_data else 0
    # st.metric("Avg Search Latency", f"{avg_search_latency:.2f}ms")
    st.metric("Max Cache Size", config_data.get('MAX_CACHE_SIZE', 24))

# Index details
st.subheader("📋 Index Configuration")
index_config = {
    "Similarity Metric": "Inner Product (Cosine)",
    "Short Query Threshold": f"{config_data.get('THRESHOLD_SHORT_QUERY', 0.92):.2f}",
    "Medium Query Threshold": f"{config_data.get('THRESHOLD_MEDIUM_QUERY', 0.88):.2f}",
    "Long Query Threshold": f"{config_data.get('THRESHOLD_LONG_QUERY', 0.84):.2f}",
    "Min Tokens to Cache": config_data.get('MIN_TOKENS_TO_CACHE', 10),
    "Min Cost to Cache": f"${config_data.get('MIN_COST_TO_CACHE', 0.000001):.8f}",
    "Eviction Percentage": f"{config_data.get('EVICTION_PERCENTAGE', 0.1) * 100:.0f}%"
}

df_config = pd.DataFrame([index_config]).T
df_config.columns = ['Value']
df_config['Value'] = df_config['Value'].astype(str)
st.dataframe(df_config, width='stretch')

# ============================================================================
# SECTION 5: CACHE ENTRIES DETAILS
# ============================================================================
st.markdown("---")
st.header("📚 Cache Entries (Detailed View)")

if entries_data and entries_data.get('entries'):
    entries = entries_data['entries']
    
    st.subheader(f"Showing {len(entries)} of {entries_data.get('total_entries', 0)} entries")
    
    # Create detailed table
    entries_df = pd.DataFrame(entries)
    
    # Format columns
    if not entries_df.empty:
        entries_df['created_at'] = pd.to_datetime(entries_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Color code by hits
        def color_hits(val):
            if val >= 10:
                return 'color: #155724; background-color: #d4edda'
            elif val >= 5:
                return 'color: #856404; background-color: #fff3cd'
            else:
                return 'color: #721c24; background-color: #f8d7da'
        
        styled_df = entries_df.style.map(color_hits, subset=['hits'])
        st.dataframe(styled_df, width='stretch', height=400)
        
        # Entry statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg Hits per Entry", f"{entries_df['hits'].mean():.1f}")
            st.metric("Max Hits", entries_df['hits'].max())
        
        with col2:
            st.metric("Avg Similarity", f"{entries_df['avg_similarity'].mean():.4f}")
            st.metric("Min Similarity", f"{entries_df['avg_similarity'].min():.4f}")
        
        with col3:
            st.metric("Total Tokens Saved", f"{entries_df['tokens_saved'].sum():,}")
            st.metric("Avg Tokens Saved", f"{entries_df['tokens_saved'].mean():.0f}")
        
        # Distribution charts
        st.subheader("📊 Entry Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Hits distribution
            fig = px.histogram(
                entries_df,
                x='hits',
                nbins=20,
                title='Distribution of Cache Hits',
                labels={'hits': 'Number of Hits', 'count': 'Number of Entries'},
                color_discrete_sequence=['#1f77b4']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Similarity distribution
            fig = px.histogram(
                entries_df,
                x='avg_similarity',
                nbins=20,
                title='Distribution of Similarity Scores',
                labels={'avg_similarity': 'Avg Similarity', 'count': 'Number of Entries'},
                color_discrete_sequence=['#2ca02c']
            )
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No cache entries yet. Send some queries to populate the cache!")

# ============================================================================
# SECTION 6: DETAILED STATS FROM CACHE MANAGER
# ============================================================================
st.markdown("---")
st.header("📈 Advanced Cache Statistics")

if stats_data and stats_data.get('stats'):
    stats = stats_data['stats']
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Cache Performance")
#         perf_metrics = {
#             "Total Entries": stats.get('total_entries', 0),
#             "Total Hits": stats.get('total_hits', 0),
#             "Avg Hits per Entry": f"{stats.get('avg_hits_per_entry', 0):.2f}",
#             "Avg Age (hours)": f"{stats.get('avg_age_hours', 0):.2f}",
#             "Avg Similarity": f"{stats.get('avg_similarity', 0):.4f}"
#         }
#         st.json(perf_metrics)
    
#     with col2:
#         st.subheader("Value Distribution")
#         value_dist = stats.get('value_distribution', {})
#         # st.json(value_dist)
    
# Top queries
st.subheader("🏆 Top Cached Queries (by hits)")
top_queries = stats.get('top_queries', [])
if top_queries:
    top_df = pd.DataFrame(top_queries)
    st.dataframe(top_df, width='stretch')

# ============================================================================
# SECTION 7: OPTIMIZER STATUS
# ============================================================================
st.markdown("---")
st.header("⚙️ Optimizer Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Optimization Cycles", optimizer_data.get('optimization_count', 0))
    st.metric("Requests Since Last", optimizer_data.get('requests_since_last_optimization', 0))

with col2:
    st.metric("Target Hit Rate", f"{config_data.get('TARGET_HIT_RATE', 0.4) * 100:.0f}%")
    st.metric("Optimization Interval", config_data.get('OPTIMIZATION_INTERVAL', 50))

with col3:
    last_opt = optimizer_data.get('last_optimization_time', 'Never')
    st.metric("Last Optimization", last_opt)

# Current thresholds
st.subheader("🎯 Current Adaptive Thresholds")
threshold_data = optimizer_data.get('current_thresholds', {})
if threshold_data:
    df_thresholds = pd.DataFrame([threshold_data]).T
    df_thresholds.columns = ['Threshold']
    st.dataframe(df_thresholds, width='stretch')

# ============================================================================
# SECTION 8: REQUEST HISTORY
# ============================================================================
st.markdown("---")
st.header("📜 Request History")

if st.session_state.request_history:
    history_df = pd.DataFrame(st.session_state.request_history[-50:])  # Last 50 requests
    st.dataframe(history_df, width='stretch', height=300)
else:
    st.info("No request history yet. Send queries using the test panel below.")

# ============================================================================
# SECTION 9: EVICTION LOGS
# ============================================================================
st.markdown("---")
st.header("🗑️ Eviction History & Logs")

# Fetch eviction history from server
eviction_data = fetch_data("/evictions/history?limit=100")

if eviction_data and eviction_data.get('evictions'):
    evictions = eviction_data['evictions']
    st.subheader(f"Recent Evictions ({len(evictions)} of {eviction_data.get('total_evictions', 0)} total)")
    
    for eviction in reversed(evictions[-20:]):  # Last 10 evictions
        with st.expander(f"🗑️ Eviction at {eviction['timestamp']} - {eviction['query'][:50]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Query:**", eviction['query'][:200] + "..." if len(eviction['query']) > 200 else eviction['query'])
                st.write("**Response:**", eviction.get('response', 'N/A'))
                st.write("**Reason:**", eviction.get('reason', 'Low value score'))
            
            with col2:
                st.write("**Metrics:**")
                st.json({
                    "Hits": eviction.get('hits', 0),
                    "Age (hours)": eviction.get('age_hours', 0),
                    "Value Score": eviction.get('value_score', 0),
                    "Avg Similarity": eviction.get('avg_similarity', 0),
                    "Tokens Saved": eviction.get('tokens_saved', 0)
                })
else:
    st.info("No evictions yet. Cache is not full or evictions haven't occurred since server started.")

# ============================================================================
# SECTION 10: QUERY TEST PANEL
# ============================================================================
st.markdown("---")
st.header("🧪 Test Query Panel")

with st.form("query_form"):
    query_input = st.text_area("Enter your query:", height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        max_tokens = st.slider("Max Tokens", 50, 1000, 500)
    with col2:
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    submit_button = st.form_submit_button("🚀 Send Query", use_container_width=True)

if submit_button and query_input:
    with st.spinner("Processing query..."):
        result = send_query(query_input, max_tokens, temperature)
        
        if result:
            # Display result
            st.success("✅ Query processed successfully!")
            
            # Add to history
            st.session_state.request_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'query': query_input[:100] + '...' if len(query_input) > 100 else query_input,
                'cached': result.get('cached', False),
                'similarity': result.get('similarity_score', 0),
                'tokens_used': result.get('tokens_used', 0),
                'cost': result.get('cost', 0),
                'latency_ms': result.get('latency_ms', 0)
            })
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Response")
                st.write(result.get('response', ''))
            
            with col2:
                st.subheader("Metrics")
                
                cached = result.get('cached', False)
                if cached:
                    st.markdown('<p class="cache-hit">✅ CACHE HIT</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="cache-miss">❌ CACHE MISS</p>', unsafe_allow_html=True)
                
                metrics_display = {
                    "Cached": "Yes" if cached else "No",
                    "Similarity Score": f"{result.get('similarity_score', 0):.4f}" if result.get('similarity_score') else "N/A",
                    "Tokens Used": result.get('tokens_used', 0),
                    "Tokens Saved": result.get('tokens_saved', 0),
                    "Cost": f"${result.get('cost', 0):.6f}",
                    "Cost Saved": f"${result.get('cost_saved', 0):.6f}",
                    "Latency": f"{result.get('latency_ms', 0):.2f}ms",
                    "Threshold Used": f"{result.get('threshold_used', 0):.2f}"
                }
                st.json(metrics_display)
            
            # Auto-refresh to show updated metrics
            time.sleep(1)
            st.rerun()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🚀 Adaptive Semantic Cache System v1.0.0</p>
    <p>Real-time monitoring dashboard powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)
