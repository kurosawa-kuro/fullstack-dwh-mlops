#!/usr/bin/env python3
"""
DuckDB DWH検証スクリプト
CI/CD環境でDuckDBデータウェアハウスの内容を確認します
"""

import duckdb
import os

def verify_dwh():
    """DuckDB DWHの内容を確認"""
    db_path = 'src/ml/data/dwh/data/house_price_dwh.duckdb'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"✅ Database file exists: {db_path}")
    
    con = duckdb.connect(db_path)
    
    # テーブル一覧
    tables = con.execute('SHOW TABLES').fetchall()
    print(f'📊 Tables: {tables}')
    
    # ビュー一覧
    views = con.execute('SHOW VIEWS').fetchall()
    print(f'📊 Views: {views}')
    
    # v_house_analyticsの確認
    if views:
        try:
            count = con.execute('SELECT COUNT(*) FROM v_house_analytics').fetchone()[0]
            print(f'📊 v_house_analytics row count: {count}')
            
            # サンプルデータの確認
            sample = con.execute('SELECT * FROM v_house_analytics LIMIT 1').fetchone()
            print(f'📊 Sample row: {sample}')
            
            return True
        except Exception as e:
            print(f'❌ Error querying v_house_analytics: {e}')
            return False
    else:
        print('❌ No views found in database')
        return False
    
    con.close()

if __name__ == '__main__':
    verify_dwh() 