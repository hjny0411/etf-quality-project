# 누적수익률 그래프 생성 코드 
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

conn = sqlite3.connect("etf_quality.db")
df = pd.read_sql_query("SELECT ticker, date, adj_close FROM etf_prices ORDER BY ticker, date", conn)
conn.close()

df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
df["daily_return"] = df.groupby("ticker")["adj_close"].pct_change()
df["cumulative_return"] = df.groupby("ticker")["adj_close"].transform(lambda x: x / x.iloc[0] -1) * 100

names = {
    "069500.KS": "KODEX 200",
    "360750.KS": "TIGER US S&P500",
    "379810.KS": "KODEX US NASDAQ100"
}

results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

plt.figure(figsize=(12, 6))

for ticker, group in df.groupby("ticker"):
    plt.plot(
        group["date"],
        group["cumulative_return"],
        label = names.get(ticker, ticker)
    )

plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
plt.title("ETF Cumulative Returns")
plt.xlabel("Date")
plt.ylabel("Cumulative_return (%)")
plt.legend
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(results_dir / "cumulative_returns.png", dpi=150)
plt.show()

print("누적수익률 그래프 저장 완료!")

# 추가 검증 = 누적수익률 일치 확인

final_returns = df.groupby("ticker")["cumulative_return"].last()

print("\nETF별 최종 누적수익률 (%)")
print(final_returns.round(2))

print("\nETF별 최고 누적수익률 (%)")
print(df.groupby("ticker")["cumulative_return"].max().round(2))

# 원천 데이터 검증(MDD 그래프를 만들기 전에 최고점의 날짜와 실제 수정종가를 확인)

kodex = df[df["ticker"] == "069500.KS"]

peak_row = kodex.loc[kodex["cumulative_return"].idxmax()]

print("\nKODEX 200 최고 수익률 기록")
print(peak_row[["date", "adj_close", "cumulative_return"]])
# 최고 누적수익률 +149.91%가 발생한 날짜와 당시 수정종가

print("\nKODEX 200 최초 및 최고 가격")
print(kodex[["date", "adj_close"]].iloc[[0, -1]])
# 최초 수정종가와 최종 수정종가

# ETF 최대낙폭(MDD) 시각화(고점대비하락률 그래프)
# Drawdown 그래프란? 누적수익률 그래프가 투자 성과를 보여준다면, Drawdown 그래프는 투자 과정에서 얼마나 큰 하락을 경험했는지 보여준다.
# cummax()=ETF별 과거 최고 가격 계산/ adj_close/peak -1 -최고점 대비 하락률/ plt.plot()-날짜별 Drawdown 시각화/ min()-전체 기간의 MDD 추출
df["peak"] = df.groupby("ticker")["adj_close"].cummax()
df["drawdown"] = (df["adj_close"] / df["peak"] -1) * 100

plt.figure(figsize=(12, 6))

for ticker, group in df.groupby("ticker"):
    plt.plot(
        group["date"],
        group["drawdown"],
        label=names.get(ticker, ticker)
    )
plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
plt.title("ETF Drawdown Comparison")
plt.xlabel("Date")
plt.ylabel("Drawdown (%)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(results_dir / "drawdown_comparison.png", dpi=150)
plt.show()

print("ETF Drawdown 그래프 저장 완료")
print("\nETF별 MDD 검증(%)")
print(df.groupby("ticker")["drawdown"].min().round(2))

