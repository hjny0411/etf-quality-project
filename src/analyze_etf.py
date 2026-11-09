# ETF 데이터 가져오기
import sqlite3
import pandas as pd

conn = sqlite3.connect("etf_quality.db")

query = "SELECT ticker, date, adj_close FROM etf_prices ORDER BY ticker, date"

df = pd.read_sql_query(query, conn)

conn.close()



# dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors = "coerce")

df["date"] = pd.to_datetime(df["date"], format= "%Y-%m-%d")

# print("날짜 변환 실패:", dates.isna().sum())
# print(df.loc[dates.isna(), ["ticker", "date"]].head(10))

print(df.head())
print("데이터 개수:", len(df))
print("ETF 개수:", df["ticker"].nunique())

# ETF별 일별 수익률 계산
# ETF가 3종이므로 반드시 종목별로 수익률을 계산해야 함.
# sort_values-종목별, 날짜별 정렬/ groupby-ETF별로 데이터 분리/ pet_change()-전 거래일 대비 수익률 계산/ daily_return-계산한 수익률 저장
df= df.sort_values(["ticker", "date"]) 
df["daily_return"] = df.groupby("ticker")["adj_close"].pct_change()
print(df[["ticker", "date", "adj_close", "daily_return"]].head(10))

# ETF 누적수익률 계산
# 분석 기간 동안 ETF 가격이 총 몇 % 상승하거나 하락했는지 계산한다.
# 1+daily_return- 수익률을 성장배율로 변환/ groupby("df[ticker]")-ETF별로 계산/cumprod()-성장배율을 누적 곱셈/ -1 -누적수익률로 변환
df["cumulative_return"] = (1 + df["daily_return"]).groupby(df["ticker"]).cumprod() -1
print(df[["ticker", "date", "daily_return", "cumulative_return"]].head(10))

# 연율화 변동성 계산
# 연율화 변동성은 ETF의 일별 수익률이 얼마나 크게 흔들리는지를 연간 기준으로 환산한 지표이다. 
# std-일별 수익률의 표본 표준편차/ np.sqrt(252)-연율화/ *100 -소수 수익률을 %로 변환/ round(2)-소수점 둘째 자리까지 표시
import numpy as np
volatility = df.groupby("ticker")["daily_return"].std() * np.sqrt(252)
print("ETF별 연율화 변동성")
print((volatility * 100).round(2))

# 샤프지수 계산
# 샤프지수(sharp ratio)는 위험 한 단위당 얼마나 많은 초과수익을 얻었는지 평가하는 지표이다. 
# (포트폴리오 연환산 수익률 - 무위험수익률)/연율화 변동성
# 일별 초과수익률을 이용해 샤프지수를 계산하자. 무위험수익률은 3%로 가정. 실제 평가에서는 분석기간과 통화에 적합한 무위험금리를 사용
risk_free_rate = 0.03
sharpe = df.groupby("ticker")["daily_return"].agg(lambda x: (x.mean() - risk_free_rate / 252) / x.std() * np.sqrt(252))
print("ETF별 샤프지수")
print(sharpe.round(3))

# 최대낙폭(MDD)계산
# 분석 기간 중 과거 최고점에서 이후 저점까지 얼마나 크게 하락했는지 나타내는 위험지표이다. 
# cummax()-해당 시점까지의 최고 수정종가/ drawdown-최고점 대비 현재 하락률/ min()-가장 큰 하락폭을 추출
df["peak"] = df.groupby("ticker")["adj_close"].cummax()
df["drawdown"] = df["adj_close"] / df["peak"] -1
mdd = df.groupby("ticker")["drawdown"].min()
print("ETF별 MDD (%)")
print((mdd*100).round(2))

# ETF 종합 평가표 만들기 
summary = pd.DataFrame({
    "cumulative_return": df.groupby("ticker")["cumulative_return"].last() * 100,
    "volatility": volatility * 100,
    "sharp_ratio": sharpe,
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