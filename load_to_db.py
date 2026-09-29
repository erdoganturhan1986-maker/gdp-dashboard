import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from pytrends.request import TrendReq

# ⚠️ Veritabanı Bağlantı Bilgilerinizi Buraya Girin
DB_CONFIG = {
    "dbname": "mikspaydb_rpt",  # Veritabanı adınız
    "user": "BURAYA_KULLANICI_ADINIZI_YAZIN",
    "password": "BURAYA_SIFRENIZI_YAZIN",
    "host": "BURAYA_DATABASE_HOST_ADRESINI_YAZIN",
    "port": "5432"
}

def fetch_and_load_trends():
    print("⏳ Google Trends verileri çekiliyor...")
    pytrends = TrendReq(hl='tr-TR', tz=180)
    
    categories = {
        "Elektronik Perakende": ['Vatan Bilgisayar', 'Teknosa', 'MediaMarkt'],
        "Beyaz Eşya": ['Arçelik', 'Beko', 'Bosch', 'Siemens']
    }
    
    records_to_insert = []
    
    for category, kw_list in categories.items():
        pytrends.build_payload(kw_list, timeframe='today 3-m', geo='TR')
        df = pytrends.interest_over_time()
        
        if not df.empty and 'isPartial' in df.columns:
            df = df.drop(columns=['isPartial'])
            
            for date, row in df.iterrows():
                formatted_date = date.strftime('%Y-%m-%d')
                for brand in kw_list:
                    index_val = int(row[brand])
                    records_to_insert.append((formatted_date, brand, category, index_val))

    print(f"📊 Toplam {len(records_to_insert)} satır veri hazırlandı. Veritabanına yazılıyor...")

    # superset_local.fact_google_trends tablosuna yazar
    insert_query = """
        INSERT INTO superset_local.fact_google_trends (trend_date, brand_name, category_name, search_index)
        VALUES %s
        ON CONFLICT (trend_date, brand_name) 
        DO UPDATE SET 
            search_index = EXCLUDED.search_index,
            created_at = CURRENT_TIMESTAMP;
    """
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        execute_values(cursor, insert_query, records_to_insert)
        conn.commit()
        print("✅ Veriler superset_local.fact_google_trends tablosuna başarıyla aktarıldı!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Veritabanı Hatası: {e}")

if __name__ == "__main__":
    fetch_and_load_trends()