# ETF 데이터 가져오기
import sqlite3
import pandas as pd

conn = sqlite3.connect("etf_quality.db")

query = "SELECT ticker, date, adj_close FROM etf_prices ORDER BY ticker, date"

df = pd.read_sql_query(query, conn)

conn.close()

df["date"] = pd.to_datetime(df["date"], format= "%Y-%m-%d")


print("데이터 개수:", len(df))
print("ETF 개수:", df["ticker"].nunique())

# ETF별 일별 수익률 계산
df= df.sort_values(["ticker", "date"]) 
df["daily_return"] = df.groupby("ticker")["adj_close"].pct_change()
abnormal = df[df["daily_return"].abs() > 0.20]
print("\n일별 수익률 ±20 초과 데이터")
print(abnormal[["ticker", "date", "adj_close", "daily_return"]])

# ETF 누적수익률 계산
df["cumulative_return"] = (1 + df["daily_return"]).groupby(df["ticker"]).cumprod() -1


# 연율화 변동성 계산
import numpy as np
volatility = df.groupby("ticker")["daily_return"].std() * np.sqrt(252)
print("ETF별 연율화 변동성")
print((volatility * 100).round(2))

# 샤프지수 계산
risk_free_rate = 0.03
sharpe = df.groupby("ticker")["daily_return"].agg(lambda x: (x.mean() - risk_free_rate / 252) / x.std() * np.sqrt(252))
print("ETF별 샤프지수")
print(sharpe.round(3))

# 최대낙폭(MDD)계산
df["peak"] = df.groupby("ticker")["adj_close"].cummax()
df["drawdown"] = df["adj_close"] / df["peak"] -1
mdd = df.groupby("ticker")["drawdown"].min()
print("ETF별 MDD (%)")
print((mdd*100).round(2))

# ETF 종합 평가표 만들기 
summary = pd.DataFrame({
    "cumulative_return": df.groupby("ticker")["cumulative_return"].last() * 100,
    "volatility": volatility * 100,
    "sharpe_ratio": sharpe,
    "mdd": mdd * 100
})

summary = summary.round(2)
print("\nETF 종합 성과평가")
print(summary)


from pathlib import Path
results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

summary.to_csv(results_dir / "etf_summary.csv", encoding="utf-8-sig")

print("ETF 종합 평가표 CSV 저장 완료!")

# 시장가격과 수정종가 비교 - 수정종가 조정 때문에 발생한 상승이 아님을 확인함.
query = """ SELECT ticker, date, close, adj_close FROM etf_prices WHERE ticker = '069500.KS' AND date BETWEEN'2026-07-29' AND '2026-08-04' ORDER BY date"""

with sqlite3.connect("etf_quality.db") as conn:
    price_check = pd.read_sql_query(query, conn)
    
print("\nKODEX 200 종가와 수정종가 비교")
print(price_check)

# ETF의 수익률만으로 운용 성과를 평가하면 시장 수급에 따른 괴리율 변동이 운용성과에 포함될 수 있다. 
# ETF 운용 성과를 평가할 떄는 분배금 등을 반영한 NAV 기준 수익률과 기초지수 수익률을 비교하고, 투자자의 거래 관점에서는 시장가격 수익률과 괴리율을 별도로 확인해야 한다. 

