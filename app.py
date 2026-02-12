import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Prototype Truck Abuse CK", layout="wide")

# Judul Utama
st.title("🚜 Truck Abuse Alert System (Excel Prototype)")

# 1. Fungsi Load Data Excel
@st.cache_data
def load_excel_data():
    # Ganti 'AbuseDummy.xlsx' dengan nama file excel yang Anda upload ke GitHub
    file_path = 'AbuseDummy.xlsx' 
    df = pd.read_excel(file_path)
    
    # Memastikan kolom tanggal dan waktu terbaca dengan benar
    df['DATE'] = df['DATE'].astype(str)
    df['SOURCETIMESTAMP'] = df['SOURCETIMESTAMP'].astype(str)
    
    # Sorting berdasarkan waktu terbaru
    return df

try:
    all_data = load_excel_data()
    
    # Sidebar Control
    st.sidebar.header("🕹️ Simulation Control")
    sim_speed = st.sidebar.select_slider("Interval Update (Detik)", options=[1, 3, 5, 10], value=3)
    start_sim = st.sidebar.button("Mulai Monitoring Simulasi")

    # Placeholder untuk Alert agar bisa diupdate secara dinamis
    alert_placeholder = st.empty()

    if start_sim:
        # Simulasi menampilkan data dari baris paling bawah (asumsi data terbaru) ke atas
        displayed_alerts = []
        
        # Mengambil 30 data sampel untuk simulasi
        sample_data = all_data.tail(30).iloc[::-1] 

        for index, row in sample_data.iterrows():
            displayed_alerts.insert(0, row)
            
            with alert_placeholder.container():
                st.markdown(f"### 🚨 Live Feed: {len(displayed_alerts)} Kejadian Terdeteksi")
                
                for alert in displayed_alerts:
                    # Warna indikator Severity
                    severity_color = "#FF4B4B" if alert['SVRTY'] == 2 else "#FFA500"
                    
                    st.markdown(f"""
                    <div style="border-left: 10px solid {severity_color}; background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 12px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); color: black;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: bold; font-size: 1.2em; color: {severity_color};">⚠️ {alert['DESCRIPTION']}</span>
                            <span style="color: gray; font-size: 0.8em;">{alert['DATE']} | {alert['SOURCETIMESTAMP']}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; margin-top: 10px; font-size: 0.95em;">
                            <div>
                                <b>Nomor Unit:</b> {alert['MACHINE']}<br>
                                <b>Operator:</b> {alert['OPRNAME']}
                            </div>
                            <div>
                                <b>Lokasi:</b> {alert['AREA']}<br>
                                <b>Koordinat:</b> {alert['LOCX']}, {alert['LOCY']}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            time.sleep(sim_speed)
    else:
        st.info("Silakan klik 'Mulai Monitoring Simulasi' untuk melihat bagaimana alert bekerja.")
        st.write("Preview Data Excel:")
        st.dataframe(all_data.head(10))

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.warning("Pastikan file 'AbuseDummy.xlsx' sudah diupload ke folder yang sama di GitHub.")
