import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px

# Konfigurasi Tema & Layout
st.set_page_config(page_title="CK Monitoring Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS untuk gaya Dark Mode & Card
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .alert-card {
        background-color: #1f2937;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid #ef4444;
        transition: 0.3s;
    }
    .alert-card:hover { background-color: #374151; }
    .unit-tag { background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .type-tag { background-color: #9333ea; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Pastikan nama file sesuai dengan yang Anda upload
    df = pd.read_excel('AbuseDummy.xlsx')
    return df

try:
    data_all = load_data()
    
    # --- HEADER ---
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.title("🎛️ Truck Abuse Central Monitoring")
    with col_t2:
        st.write(f"**System Status:** 🟢 Online")
        st.write(f"**Server Time:** {datetime.now().strftime('%H:%M:%S')}")

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("Settings")
    sim_active = st.sidebar.toggle("Start Live Monitoring", value=False)
    interval = st.sidebar.select_slider("Refresh Rate (s)", options=[1, 2, 5], value=2)

    # --- TOP METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    total_event = len(data_all)
    critical_event = len(data_all[data_all['SVRTY'] == 2])
    unique_trucks = data_all['MACHINE'].nunique()
    
    m1.metric("Total Violations", total_event)
    m2.metric("Critical (Svrty 2)", critical_event, delta_color="inverse")
    m3.metric("Units Monitored", unique_trucks)
    m4.metric("Active Area", data_all['AREA'].iloc[0])

    # --- MAIN CONTENT ---
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📍 Live Position Log (UTM Map)")
        # Visualisasi koordinat menggunakan Plotly (karena UTM tidak bisa pakai st.map langsung)
        fig = px.scatter(data_all.tail(50), x="LOCX", y="LOCY", 
                         color="DESCRIPTION", hover_name="MACHINE",
                         template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🔔 Violation Feed")
        feed_placeholder = st.empty()

    # --- SIMULATION LOGIC ---
    if sim_active:
        # Simulasi berjalan mundur dari data terbaru
        for i in range(len(data_all)-1, 0, -1):
            row = data_all.iloc[i]
            
            with feed_placeholder.container():
                # Loop untuk menampilkan 5 alert terbaru saja di feed agar tidak penuh
                for j in range(i, max(i-5, 0), -1):
                    alert = data_all.iloc[j]
                    border_color = "#ef4444" if alert['SVRTY'] == 2 else "#f59e0b"
                    
                    st.markdown(f"""
                        <div class="alert-card" style="border-left-color: {border_color};">
                            <div style="display: flex; justify-content: space-between;">
                                <span class="type-tag">{alert['DESCRIPTION']}</span>
                                <small>{alert['SOURCETIMESTAMP']}</small>
                            </div>
                            <div style="margin-top: 10px;">
                                <span class="unit-tag">{alert['MACHINE']}</span> 
                                <b>{alert['OPRNAME']}</b>
                            </div>
                            <div style="font-size: 13px; margin-top: 5px; color: #9ca3af;">
                                📍 {alert['AREA']} ({alert['LOCX']}, {alert['LOCY']})
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            time.sleep(interval)
    else:
        with feed_placeholder:
            st.info("Toggle 'Start Live Monitoring' di sidebar untuk simulasi.")
            st.dataframe(data_all[['MACHINE', 'OPRNAME', 'DESCRIPTION', 'SOURCETIMESTAMP']].tail(10))

except Exception as e:
    st.error(f"Error: {e}")
