-- 데이터 건수
SELECT ticker, COUNT(*) AS data_count
FROM etf_prices
GROUP BY ticker
ORDER BY data_count DESC;

-- 중복치 탐지
SELECT ticker, date, COUNT(*) AS duplicate_count
FROM etf_prices
GROUP BY ticker, date
HAVING COUNT(*)>= 2;

-- 결측치 탐지
SELECT ticker, date, close, adj_close, volume
FROM etf_prices
WHERE close IS NULL OR adj_close IS NULL OR volume IS NULL;

-- 비정상 가격 탐지 
SELECT ticker, date, open, high, low, close
FROM etf_prices
WHERE open <= 0 OR high <=0 OR low <= 0 OR close <=0;

-- OHLC 가격의 논리적 일관성 검증 
SELECT ticker, date, open, high, low, close
FROM etf_prices
WHERE high < open OR high < close OR low > open OR low > close;

-- 날짜 형식 오류(형식 및 실제 날짜 유효성 검사) 
SELECT ticker, date 
FROM etf_prices
WHERE date(date) IS NULL OR date(date) !=date;

-- 종가와 수정종가 차이(1% 초과 차이 나는 종목과 개수) 
SELECT ticker, date, close, adj_close, (close - adj_close) * 100.0 / close AS diff_pct
FROM etf_prices
WHERE ABS((close - adj_close) *100.0 / close) > 1;

SELECT ticker, COUNT(*) AS diff_count, MIN(date) AS 시작일, MAX(date) AS 종료일
FROM etf_prices
WHERE ABS((close - adj_close) *100.0 / close) > 1
GROUP BY ticker;

-- 패턴 확인
SELECT ticker, date, close, adj_close, (close - adj_close) * 100.0 / close AS diff_pct
FROM etf_prices
WHERE ticker = '379810.KS';

-- 나스닥100 수정종가 조정 구간(분배금 누적 반영 확인)
SELECT ROUND((close - adj_close) * 100.0 / close, 2) AS diff_pct, COUNT(*) AS trading_day, MIN(date) AS start_date, MAX(date) AS end_date
FROM etf_prices
WHERE ticker = '379810.KS'
GROUP BY ROUND((close - adj_close) * 100.0 / close, 2)
ORDER BY MIN(date);