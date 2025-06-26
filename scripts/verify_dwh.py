#!/usr/bin/env python3
"""
DuckDB DWH検証スクリプト
CI/CD環境でDuckDBデータウェアハウスの内容を確認します
"""

import duckdb
import os
import sys

def verify_dwh():
    """DuckDB DWHの内容を確認"""
    db_path = 'src/data/warehouse/duckdb/data/house_price_dwh.duckdb'
    wal_path = 'src/data/warehouse/duckdb/data/house_price_dwh.duckdb.wal'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"✅ Database file exists: {db_path}")
    
    # WALファイルの確認
    if os.path.exists(wal_path):
        print(f"📄 WAL file exists: {wal_path}")
    else:
        print(f"📄 No WAL file found: {wal_path}")
    
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
            
            con.close()
            return True
        except Exception as e:
            print(f'❌ Error querying v_house_analytics: {e}')
            con.close()
            return False
    else:
        print('❌ No views found in database')
        con.close()
        return False

if __name__ == '__main__':
    if not verify_dwh():
        sys.exit("❌ DWH verification failed") 