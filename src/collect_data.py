import yfinance as yf
import sqlite3

tickers = ["069500.KS", "360750.KS", "379810.KS"]

conn = sqlite3.connect("etf_quality.db")

for ticker in tickers:
    df = yf.download(ticker, start="2025-11-01", end="2026-11-09", auto_adjust=False, progress=False)
    
    if df.empty:
        print(ticker, "데이터 없음")
        continue
    df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    
    rows = []
    for _, row in df.iterrows():
        rows.append((
            ticker,
            row["Date"].strftime("%Y-%m-%d"),
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            float(row["Adj Close"]),
            float(row["Volume"])
        ))
    conn.executemany("""
        INSERT OR IGNORE INTO etf_prices
        (ticker, date, open, high, low, close, adj_close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", rows)
    
conn.commit()

cursor = conn.cursor()
cursor.execute("SELECT ticker, COUNT(*) FROM etf_prices GROUP BY ticker")
print("DB 저장 결과:", cursor.fetchall())
conn.close()

