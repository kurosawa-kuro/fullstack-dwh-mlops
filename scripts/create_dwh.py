#!/usr/bin/env python3
"""
DuckDB DWH構築スクリプト
CI/CD環境でDuckDBデータウェアハウスを作成します
"""

import pandas as pd
import duckdb
import pathlib
import datetime
import os

def create_sample_data():
    """サンプルデータを作成"""
    os.makedirs('src/ml/data/raw', exist_ok=True)
    
    sample_data = pd.DataFrame({
        'sqft': [1500, 2000, 1200, 1800, 2200, 1600, 2400, 1400, 1900, 2100],
        'bedrooms': [3, 4, 2, 3, 4, 3, 5, 2, 3, 4],
        'bathrooms': [2, 3, 1, 2, 3, 2, 4, 1, 2, 3],
        'year_built': [2010, 2015, 2008, 2012, 2018, 2011, 2020, 2009, 2013, 2017],
        'location': ['Suburban', 'Urban', 'Rural', 'Suburban', 'Urban', 'Suburban', 'Urban', 'Rural', 'Suburban', 'Urban'],
        'condition': ['Good', 'Excellent', 'Fair', 'Good', 'Excellent', 'Good', 'Excellent', 'Fair', 'Good', 'Excellent'],
        'price': [300000, 450000, 200000, 350000, 500000, 320000, 550000, 180000, 380000, 480000]
    })
    
    sample_data.to_csv('src/ml/data/raw/house_data.csv', index=False)
    print('✅ CSV written')

def build_dwh():
    """DuckDB DWHを構築"""
    db_path = pathlib.Path('src/data/warehouse/duckdb/data')
    db_path.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(db_path / 'house_price_dwh.duckdb')

    # CSV → テーブル
    con.execute("""
        CREATE OR REPLACE TABLE bronze_raw_house_data AS 
        SELECT * FROM read_csv_auto('src/ml/data/raw/house_data.csv')
    """)

    # ビュー
    con.execute(f"""
        CREATE OR REPLACE VIEW v_house_analytics AS
        SELECT
            row_number() OVER () AS transaction_id,
            price, sqft, bedrooms, bathrooms,
            price / sqft AS price_per_sqft,
            (2025 - year_built) AS house_age,
            bedrooms * 1.0 / bathrooms AS bed_bath_ratio,
            location AS location_name,
            CASE
                WHEN lower(location) LIKE '%suburban%' THEN 'Suburban'
                WHEN lower(location) LIKE '%urban%' THEN 'Urban'
                ELSE 'Rural'
            END AS location_type,
            condition AS condition_name,
            CASE condition
                WHEN 'Excellent' THEN 5 WHEN 'Good' THEN 4
                WHEN 'Fair' THEN 3 WHEN 'Poor' THEN 2
                ELSE 1 END AS condition_score,
            year_built AS year_value,
            (year_built/10)*10 || 's' AS decade,
            (year_built/100 + 1) || 'th Century' AS century,
            DATE '{datetime.date.today()}' AS transaction_date
        FROM bronze_raw_house_data
    """)

    # 確認
    count = con.execute('SELECT COUNT(*) FROM v_house_analytics').fetchone()[0]
    assert count == 10, f'❌ View creation failed: expected 10, got {count}'
    
    # DuckDB ≥0.10: WAL → DB 本体へフラッシュ
    con.execute("PRAGMA force_checkpoint;")
    
    print('✅ DuckDB DWH built & verified')
    con.close()

if __name__ == '__main__':
    create_sample_data()
    build_dwh() 