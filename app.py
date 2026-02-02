import streamlit as st
import pandas as pd
import json
import yaml # Đảm bảo đã pip install pyyaml
import plotly.graph_objects as go
import plotly.express as px
import os
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(layout="wide", page_title="NASA AI-Ops Control Center", page_icon="🛡️")

# --- XỬ LÝ DỮ LIỆU ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'output')
CONFIG_PATH = os.path.join(BASE_DIR, 'autoscale_config.yaml') 

@st.cache_data
def load_dataset():
    store = {}
    try:
        # 1. ĐỌC CONFIG TỪ FILE YAML
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                store['config'] = yaml.safe_load(f)

        # 2. ĐỌC DỮ LIỆU TỪ CSV/JSON
        for tf in ['1m', '5m', '15m']:
            # Forecast
            f_path = os.path.join(DATA_DIR, f'forecast_{tf}.csv')
            if os.path.exists(f_path):
                df = pd.read_csv(f_path)
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
                store[f'forecast_{tf}'] = df
            # Metrics
            m_path = os.path.join(DATA_DIR, f'metrics_{tf}.json')
            if os.path.exists(m_path):
                with open(m_path, 'r') as f: store[f'metrics_{tf}'] = json.load(f)
            # Scaling Logs
            for m in ['req', 'bytes', 'hybrid']:
                s_path = os.path.join(DATA_DIR, f'scale_{m}_{tf}.csv')
                if os.path.exists(s_path):
                    df = pd.read_csv(s_path)
                    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)
                    store[f'scale_{m}_{tf}'] = df
        return store
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {e}")
        return None

DB = load_dataset()
if not DB:
    st.error("❌ Không tìm thấy dữ liệu. Hãy đảm bảo thư mục data/output/ chứa đầy đủ file.")
    st.stop()

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.title("🎛️ CONTROL CENTER")
    st.markdown("---")
    
    st.subheader("1. Cấu hình Demo")
    tf_selected = st.select_slider("Khung thời gian (Timeframe)", options=['1m', '5m', '15m'], value='5m')
    method_selected = st.selectbox("Chiến lược Scaling", ['req', 'bytes', 'hybrid'], index=2, format_func=lambda x: x.upper())

    st.markdown("---")
    st.success(f"Mode: **{method_selected.upper()}**")
    st.info(f"Resolution: **{tf_selected}**")

# --- CSS TÙY CHỈNH (Tab Full + Card Đều) ---
st.markdown("""
<style>
    /* 1. Tab trải đều */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab-list"] button {
        flex-grow: 1;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        white-space: nowrap;
    }

    /* 2. Ép chiều cao các Metric Card bằng nhau */
    div[data-testid="column"] > div { height: 100%; width: 100%; }
    div[data-testid="stMetric"] {
        background-color: #161B22 !important; 
        border: 1px solid #30363D !important; 
        border-radius: 8px !important;
        height: 140px !important; 
        min-height: 140px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }

    /* 3. Sửa lỗi lệch chữ 'Tốt' (Ẩn mũi tên) */
    div[data-testid="stMetricDelta"] svg { display: none !important; } 
    div[data-testid="stMetricDelta"] > div { text-align: center !important; font-weight: bold !important; }
    div[data-testid="stMetricDelta"] { width: 100% !important; justify-content: center !important; display: flex !important; margin-top: 5px !important; }
    div[data-testid="stMetricLabel"] { width: 100% !important; justify-content: center !important; display: flex !important; }
    div[data-testid="stMetricValue"] { width: 100% !important; justify-content: center !important; display: flex !important; }
</style>
""", unsafe_allow_html=True)

# --- MAIN TABS ---
t1, t2, t3, t4 = st.tabs([
    "VẤN ĐỀ (EDA)", 
    "MODEL", 
    "GIẢI PHÁP (LIVE)", 
    "HIỆU QUẢ (ROI)"
])

# ==========================================
# TAB 1: EDA
# ==========================================
with t1:
    st.subheader(f"🚨 Phân tích rủi ro hạ tầng (Dựa trên khung {tf_selected})")
    
    df_vis = DB[f'scale_req_{tf_selected}'].copy()
    static_cap = df_vis['load'].quantile(0.95)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_vis['time'], y=df_vis['load'], name="Traffic Thực tế", fill='tozeroy', line=dict(color='#00CC96', width=2), fillcolor='rgba(0, 204, 150, 0.1)'))
    fig.add_trace(go.Scatter(x=df_vis['time'], y=[static_cap]*len(df_vis), name="Static Limit (Cố định)", line=dict(color='#EF553B', width=2, dash='dash')))
    spikes = df_vis[df_vis['load'] > static_cap]
    fig.add_trace(go.Scatter(x=spikes['time'], y=spikes['load'], mode='markers', name="Điểm Sập (Overload)", marker=dict(color='red', size=10, symbol='x')))
    fig.update_layout(height=450, template="plotly_dark", hovermode="x unified", title="Biến động tải & Rủi ro quá tải", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    n_spikes = len(spikes)
    risk_pct = (n_spikes / len(df_vis)) * 100
    waste_pct = (1 - df_vis['load'].mean() / static_cap) * 100
    
    c1.metric("Số lần Sập (Spikes)", f"{n_spikes}", delta="Nguy hiểm", delta_color="inverse")
    c2.metric("Tỉ lệ rủi ro", f"{risk_pct:.1f}%", "Downtime tiềm năng")
    c3.metric("Lãng phí (Off-peak)", f"{waste_pct:.1f}%", "Mất tiền vô ích")
    c4.metric("Đỉnh tải (Max Load)", f"{int(df_vis['load'].max()):,}", "Requests")

# ==========================================
# TAB 2: MODEL
# ==========================================
with t2:
    st.subheader(f"🧠 Hiệu năng Model LightGBM")
    
    curr_metrics = DB[f'metrics_{tf_selected}']['request_metrics']
    mape_val = curr_metrics['MAPE']
    
    # Logic: MAPE thấp là Tốt (Xanh - Inverse)
    if mape_val < 10:
        eval_text = "Xuất sắc"
        color_mode = "normal"
    elif mape_val < 20:
        eval_text = "Tốt (Good)"
        color_mode = "normal"
    else:
        eval_text = "Cần cải thiện"
        color_mode = "inverse"

    m1, m2, m3 = st.columns([1, 1, 1])
    with m1: st.metric("Khung thời gian", tf_selected)
    with m2: st.metric("MAPE (Sai số %)", f"{mape_val:.2f}%", delta=eval_text, delta_color=color_mode)
    with m3: st.metric("RMSE (Sai số đơn vị)", f"{curr_metrics['RMSE']:.2f}")
    
    st.divider()
    
    st.markdown("#### 🔎 Soi chi tiết: Dự báo vs Thực tế")
    df_f = DB[f'forecast_{tf_selected}']
    df_s = DB[f'scale_{method_selected}_{tf_selected}']
    
    fig_zoom = go.Figure()
    fig_zoom.add_trace(go.Scatter(x=df_s['time'], y=df_s['load'], name="Thực tế", line=dict(color='green', width=1)))
    fig_zoom.add_trace(go.Scatter(x=df_f['timestamp'], y=df_f['req_pred'], name="AI Dự báo", line=dict(color='#636EFA', width=2)))
    fig_zoom.update_layout(height=400, template="plotly_dark", hovermode="x unified", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_zoom, use_container_width=True)

# ==========================================
# TAB 3: SIMULATOR
# ==========================================
with t3:
    st.subheader(f"🎮 Auto-Scaling Simulator: {method_selected.upper()} ({tf_selected})")
    
    # --- ĐỌC CONFIG YAML AN TOÀN ---
    target_util = 60
    cooldown = 15    
    
    if 'config' in DB and DB['config']:
        g_params = DB['config'].get('global_parameters', {})
        target_util = g_params.get('TARGET_UTIL', 0.6) * 100
        cooldown = g_params.get('SCALE_IN_COOLDOWN', 15)
        
    st.info(f"⚙️ **Config Loaded:** Target Utilization = **{target_util:.0f}%** | Cooldown = **{cooldown} phút**")
    
    df_sim = DB[f'scale_{method_selected}_{tf_selected}']
    
    col_run, col_kpi = st.columns([1, 4])
    with col_run:
        run_anim = st.button("▶️ CHẠY DEMO", type="primary", use_container_width=True)
        speed = st.select_slider("Tốc độ", options=[0.05, 0.1, 0.5], value=0.05, label_visibility="collapsed")
    
    with col_kpi:
        k1, k2, k3 = st.columns(3)
        k1.metric("Max Servers", int(df_sim['instances'].max()))
        k2.metric("Scale Events", int(df_sim['scaled'].sum()))
        k3.metric("Avg Utilization", f"{df_sim['util'].mean()*100:.1f}%")

    chart_spot = st.empty()

    def plot_sim(data):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['time'], y=data['capacity'], fill='tozeroy', name='AI Capacity', line=dict(width=0), fillcolor='rgba(46, 204, 113, 0.3)'))
        fig.add_trace(go.Scatter(x=data['time'], y=data['load'], name='Load', line=dict(color='white', width=1.5)))
        scales = data[data['scaled'] == True]
        if not scales.empty:
            fig.add_trace(go.Scatter(x=scales['time'], y=scales['load'], mode='markers', name='Scale Action', marker=dict(color='yellow', size=10, symbol='triangle-up')))
        fig.update_layout(height=500, template="plotly_dark", hovermode="x unified", yaxis_title="Load / Capacity", margin=dict(l=0, r=0, t=30, b=0))
        return fig

    if run_anim:
        step = max(1, len(df_sim) // 50)
        for i in range(20, len(df_sim), step):
            chart_spot.plotly_chart(plot_sim(df_sim.iloc[:i]), use_container_width=True)
            time.sleep(speed)
        chart_spot.plotly_chart(plot_sim(df_sim), use_container_width=True)
    else:
        chart_spot.plotly_chart(plot_sim(df_sim), use_container_width=True)

# ==========================================
# TAB 4: ECONOMICS (ĐÃ SỬA LỖI NAME ERROR)
# ==========================================
with t4:
    st.subheader("💰 Hiệu quả Kinh tế (ROI Analysis)")
    
    # 1. KHAI BÁO MẶC ĐỊNH (Tránh NameError)
    unit_cost = 0.5 
    
    # 2. ĐỌC CONFIG (Tránh TypeError)
    if 'config' in DB and DB['config']:
        g_params = DB['config'].get('global_parameters', {})
        val = g_params.get('UNIT_COST_PER_HOUR')
        if val is not None:
            unit_cost = float(val)

    # Hiển thị mức giá đang dùng để kiểm tra
    st.caption(f"ℹ️ Đang tính toán với đơn giá: **${unit_cost}/giờ** (Lấy từ autoscale_config.yaml)")

    # 3. TÍNH TOÁN
    static_cost = df_sim['instances'].max() * len(df_sim) * unit_cost
    ai_cost = df_sim['instances'].sum() * unit_cost
    saved = static_cost - ai_cost
    pct = (saved / static_cost) * 100 if static_cost > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Chi phí Tĩnh (Cũ)", f"${static_cost:,.0f}", help="Chi phí nếu thuê server cố định theo mức đỉnh")
    c2.metric("Chi phí AI-Ops (Mới)", f"${ai_cost:,.0f}", help="Chi phí thực tế khi dùng Autoscaling")
    c3.metric("TIẾT KIỆM ĐƯỢC", f"{pct:.1f}%", delta=f"+${saved:,.0f}", help="Số tiền tiết kiệm được")
    
    st.markdown("---")
    
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Bar(x=['Static', 'AI-Ops'], y=[static_cost, ai_cost], marker_color=['#636EFA', '#00CC96'], text=[f"${static_cost:,.0f}", f"${ai_cost:,.0f}"], textposition='auto'))
    fig_roi.update_layout(title="So sánh chi phí trực quan", template="plotly_dark", height=350)
    st.plotly_chart(fig_roi, use_container_width=True)