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