import streamlit as st
import pandas as pd
import plotly.express as px
from pytrends.request import TrendReq
from gnews import GNews
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Canlı Perakende & Haber Portalı", layout="wide")

st.title("🌐 Canlı Perakende Arama Trendleri & Web Haber Taraması")
st.caption("Google Trends ve Web Haber Kaynaklarından Anlık Veri")

# Tab'lar (Sekmeler)
tab1, tab2 = st.tabs(["📊 Google Arama Trendleri", "📰 Canlı Web Haberleri & Kaynaklar"])

# ---------------------------------------------------------
# SEKME 1: GOOGLE TRENDS
# ---------------------------------------------------------
with tab1:
    st.subheader("Marka ve Perakende Arama Yoğunluğu")
    
    @st.cache_data(ttl=3600)
    def get_trends_data():
        pytrends = TrendReq(hl='tr-TR', tz=180)
        kw_list = ['Vatan Bilgisayar', 'Teknosa', 'MediaMarkt', 'Arçelik', 'Beko']
        pytrends.build_payload(kw_list, timeframe='today 3-m', geo='TR')
        df = pytrends.interest_over_time()
        if 'isPartial' in df.columns:
            df = df.drop(columns=['isPartial'])
        return df

    try:
        df_trends = get_trends_data()
        fig = px.line(df_trends, title="Son 3 Ay Arama Trendleri", labels={"value": "İlgi Endeksi", "date": "Tarih"})
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Trends verisi çekilirken hata oluştu: {e}")

# ---------------------------------------------------------
# SEKME 2: CANLI WEB HABERLERİ
# ---------------------------------------------------------
with tab2:
    st.subheader("Web'den Anlık Perakende & Marka Haberleri")
    
    selected_brand = st.selectbox(
        "Hangi marka/sektör haberlerini taramak istersiniz?",
        ['Vatan Bilgisayar', 'Teknosa', 'MediaMarkt', 'Arçelik', 'Beko', 'Alışveriş Kredisi']
    )
    
    if st.button("Web'i Tara ve Haberleri Getir"):
        with st.spinner(f"'{selected_brand}' hakkında haberler taranıyor..."):
            google_news = GNews(language='tr', country='TR', period='7d', max_results=10)
            news_items = google_news.get_news(selected_brand)
            
            if news_items:
                for item in news_items:
                    st.markdown(f"### [{item['title']}]({item['url']})")
                    st.write(f"**Kaynak:** {item['publisher']['title']} | **Tarih:** {item['published date']}")
                    st.write(item['description'])
                    st.markdown(f"[Haberin Kaynağına Git 🔗]({item['url']})")
                    st.divider()
            else:
                st.info("Son 7 güne ait ilgili haber bulunamadı.")