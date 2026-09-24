import streamlit as st
import pandas as pd
import plotly.express as px
from pytrends.request import TrendReq

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Piyasa & Perakende Yoğunluk Paneli",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Canlı Perakende & Beyaz Eşya Tüketici İlgisi")
st.caption("Otomatik Güncellenen Canlı Piyasa & Takip Paneli")

# --- CANLI VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=3600)
def get_live_market_data():
    pytrends = TrendReq(hl='tr-TR', tz=180)
    
    # 1. Elektronik Perakende Grubu
    kw_electronics = ['Vatan Bilgisayar', 'Teknosa', 'MediaMarkt']
    pytrends.build_payload(kw_electronics, cat=0, timeframe='today 3-m', geo='TR')
    df_elec = pytrends.interest_over_time()
    if 'isPartial' in df_elec.columns:
        df_elec = df_elec.drop(columns=['isPartial'])
        
    # 2. Beyaz Eşya Grubu
    kw_whitegoods = ['Arçelik', 'Beko', 'Bosch', 'Siemens']
    pytrends.build_payload(kw_whitegoods, cat=0, timeframe='today 3-m', geo='TR')
    df_wg = pytrends.interest_over_time()
    if 'isPartial' in df_wg.columns:
        df_wg = df_wg.drop(columns=['isPartial'])
        
    return df_elec, df_wg

# Veriyi Çek ve Göster
try:
    with st.spinner('Canlı piyasa verileri yükleniyor...'):
        df_elec, df_wg = get_live_market_data()
    
    # Üst Özet Kartları
    col1, col2, col3 = st.columns(3)
    latest_elec = df_elec.iloc[-1]
    latest_wg = df_wg.iloc[-1]
    
    col1.metric(label="Elektronik Perakende Lideri", value=latest_elec.idxmax())
    col2.metric(label="Beyaz Eşya İlgi Lideri", value=latest_wg.idxmax())
    col3.metric(label="Son Güncelleme", value=df_elec.index[-1].strftime('%d.%m.%Y'))

    st.divider()

    # Grafik Sekmeleri
    tab1, tab2 = st.tabs(["📱 Elektronik Perakende", "❄️ Beyaz Eşya"])

    with tab1:
        fig_elec = px.line(
            df_elec, 
            x=df_elec.index, 
            y=df_elec.columns,
            labels={'value': 'Yoğunluk Endeksi (0-100)', 'date': 'Tarih', 'variable': 'Marka'},
            title="Vatan Bilgisayar vs Teknosa vs MediaMarkt"
        )
        fig_elec.update_layout(template="plotly_white")
        st.plotly_chart(fig_elec, use_container_width=True)

    with tab2:
        fig_wg = px.line(
            df_wg, 
            x=df_wg.index, 
            y=df_wg.columns,
            labels={'value': 'Yoğunluk Endeksi (0-100)', 'date': 'Tarih', 'variable': 'Marka'},
            title="Arçelik vs Beko vs Bosch vs Siemens"
        )
        fig_wg.update_layout(template="plotly_white")
        st.plotly_chart(fig_wg, use_container_width=True)

except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {str(e)}")