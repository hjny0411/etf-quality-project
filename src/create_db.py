import sqlite3
conn = sqlite3.connect("etf_quality.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS etfs(ticker TEXT PRIMARY KEY, name TEXT NOT NULL)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS etf_prices(ticker TEXT NOT NULL, date TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, adj_close REAL, volume INTEGER, PRIMARY KEY(ticker, date), FOREIGN KEY(ticker) REFERENCES etfs(ticker))""")

etfs =[
    ("069500.KS", "KODEX 200"),
    ("360750.KS", "TIGER 미국S&P500"),
    ("379810.KS", "KODEX 미국나스닥100")]

cursor.executemany("INSERT OR IGNORE INTO etfs (ticker, name) VALUES(?, ?)", etfs)

conn.commit()
cursor.execute("SELECT * FROM etfs")
print(cursor.fetchall())
conn.close()

print("ETF 데이터베이스 생성 완료!")