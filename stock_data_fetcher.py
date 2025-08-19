#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改進的股票數據獲取模組
支援多個數據源和錯誤處理
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import warnings
from shioaji_extended import ShioajiExtended
warnings.filterwarnings('ignore')

class StockDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.shioaji_client = ShioajiExtended()
        if not self.shioaji_client.connect():
            print("⚠️ Shioaji API 連接失敗，將僅使用 yfinance 作為數據源")
            self.shioaji_client = None
    
    def fetch_data_yfinance(self, symbol, period="6mo", interval="1d", retry_count=3, buffer_days=90):
        """
        使用yfinance獲取數據，包含重試機制和緩衝期。
        buffer_days: 額外獲取的歷史數據天數，用於確保技術指標計算的準確性。
        """
        # 將期間轉換為天數
        period_map = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180,
            "1y": 365, "2y": 730, "5y": 1825, "max": 36500 # max設為一個很大的數
        }
        requested_days = period_map.get(period, 180)
        
        # 加上緩衝期
        total_days = requested_days + buffer_days
        
        # yfinance 的 period 參數不接受天數，我們需要計算開始和結束日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=total_days)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # 根據 yfinance 的限制調整 interval 和數據範圍
        # ... (此處可保留原有的 intraday 週期限制檢查，但為簡化，暫時專注於日線)

        for attempt in range(retry_count):
            try:
                print(f"嘗試獲取 {symbol} 數據從 {start_str} 到 {end_str} (含緩衝), interval={interval} ... (第 {attempt + 1} 次)")
                
                ticker = yf.Ticker(symbol)
                # 使用 start 和 end 來獲取擴展後的數據
                data = ticker.history(start=start_str, end=end_str, interval=interval)
                
                if not data.empty:
                    print(f"✅ 成功獲取 {symbol} 擴展數據: {len(data)} 筆記錄")
                    
                    # 儲存原始請求的開始日期，用於後續裁剪
                    self.original_start_date = end_date - timedelta(days=requested_days)
                    
                    return data
                else:
                    print(f"⚠️ {symbol} 返回空數據")
                    
            except Exception as e:
                print(f"❌ 第 {attempt + 1} 次嘗試失敗: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2)  # 等待2秒後重試
        
        return None

    def fetch_data_shioaji(self, symbol, period="6mo"):
        """使用 Shioaji API 的 kbars 方法獲取歷史 K 線數據"""
        if not self.shioaji_client or not self.shioaji_client.is_connected:
            return None
        
        api = self.shioaji_client.api
        
        # 移除 .TW 後綴
        if symbol.endswith(".TW"):
            stock_code = symbol[:-3]
        else:
            print(f"⚠️ {symbol} 非台股，跳過 Shioaji 數據源")
            return None

        # 將期間轉換為開始和結束日期
        end_date = datetime.now()
        period_map = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
            "6mo": 180, "1y": 365, "2y": 730, "5y": 1825, "max": 3650
        }
        days = period_map.get(period, 180)
        start_date = end_date - timedelta(days=days)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        try:
            print(f"嘗試從 Shioaji 獲取 {stock_code} 從 {start_str} 到 {end_str} 的數據...")
            
            # 獲取合約
            contract = self._find_contract(api, stock_code)
            if contract is None:
                print(f"❌ 在 Shioaji 中找不到股票代碼: {stock_code}")
                return None

            # 使用 api.kbars 獲取數據
            kbars = api.kbars(contract, start=start_str, end=end_str)
            
            if kbars:
                data = pd.DataFrame({**kbars})
                
                # 轉換格式以符合 StockAnalyzer 的需求
                data = data.rename(columns={
                    'ts': 'Date',
                    'Open': 'Open',
                    'High': 'High',
                    'Low': 'Low',
                    'Close': 'Close',
                    'Volume': 'Volume'
                })
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
                
                # 確保欄位完整
                if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
                    print(f"✅ 成功從 Shioaji 獲取 {stock_code} 數據: {len(data)} 筆記錄")
                    return data

            return None
        except Exception as e:
            print(f"❌ 從 Shioaji 獲取數據失敗: {e}")
            return None

    def _find_contract(self, api, stock_code):
        """尋找股票合約"""
        try:
            if not hasattr(api.Contracts, 'Stocks'):
                print("❌ 合約資訊未載入")
                return None
            
            stocks = api.Contracts.Stocks
            
            # 方法1: 如果是字典結構
            if isinstance(stocks, dict):
                # 直接用股票代碼查找
                if stock_code in stocks:
                    return stocks[stock_code]
                
                # 遍歷查找
                for key, contract in stocks.items():
                    if hasattr(contract, 'code') and contract.code == stock_code:
                        return contract
                    if key == stock_code:
                        return contract
            
            # 方法2: 如果有 __getitem__ 方法
            elif hasattr(stocks, '__getitem__'):
                try:
                    return stocks[stock_code]
                except (KeyError, TypeError):
                    pass
            
            # 方法3: 如果是可迭代的
            elif hasattr(stocks, '__iter__'):
                for contract in stocks:
                    if hasattr(contract, 'code') and contract.code == stock_code:
                        return contract
            
            print(f"💡 提示：嘗試使用 api.Contracts.Stocks.{stock_code}")
            return getattr(stocks, stock_code, None)
            
        except Exception as e:
            print(f"⚠️ 查找合約時發生錯誤: {e}")
            return None

    def generate_sample_data(self, symbol, days=180):
        """生成示範數據（當無法獲取真實數據時使用）"""
        print(f"🔧 為 {symbol} 生成示範數據...")
        
        # 創建日期範圍
        end_date = datetime(2024, 8, 19) # 使用固定的過去日期以避免未來日期問題
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 模擬股價走勢
        np.random.seed(42)  # 固定隨機種子以獲得一致的結果
        
        # 基礎價格（根據股票代碼設定）
        if '2330' in symbol:  # 台積電
            base_price = 500
        elif '2454' in symbol:  # 聯發科
            base_price = 800
        elif '7703' in symbol:  # 銳澤
            base_price = 200
        else:
            base_price = 100
        
        # 生成價格序列
        returns = np.random.normal(0.001, 0.02, len(dates))  # 日報酬率
        prices = [base_price]
        
        for i in range(1, len(dates)):
            # 加入趨勢（緩慢上升）
            trend = 0.0005 if i > len(dates) * 0.3 else 0
            new_price = prices[-1] * (1 + returns[i] + trend)
            prices.append(max(new_price, base_price * 0.7))  # 設定最低價格
        
        # 創建OHLC數據
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # 生成開高低價
            daily_range = close * 0.03  # 日內波動3%
            high = close + np.random.uniform(0, daily_range)
            low = close - np.random.uniform(0, daily_range)
            open_price = low + np.random.uniform(0, high - low)
            
            # 生成成交量
            volume = np.random.randint(1000000, 5000000)
            
            data.append({
                'Open': round(open_price, 2),
                'High': round(high, 2),
                'Low': round(low, 2),
                'Close': round(close, 2),
                'Adj Close': round(close, 2),
                'Volume': volume
            })
        
        df = pd.DataFrame(data, index=dates)
        
        # 添加一些特殊模式
        self.add_golden_cross_pattern(df)
        self.add_uptrend_pattern(df)
        
        print(f"✅ 示範數據生成完成: {len(df)} 筆記錄")
        return df
    
    def add_golden_cross_pattern(self, df):
        """在示範數據中添加黃金交叉模式"""
        # 在數據的後1/3部分添加明顯的上升趨勢
        start_idx = int(len(df) * 0.6)
        end_idx = int(len(df) * 0.9)
        
        if end_idx > start_idx:
            for i in range(start_idx, end_idx):
                # 逐步提高價格
                multiplier = 1 + (i - start_idx) * 0.002
                df.iloc[i, df.columns.get_loc('Close')] *= multiplier
                df.iloc[i, df.columns.get_loc('High')] *= multiplier
                df.iloc[i, df.columns.get_loc('Open')] *= multiplier
                df.iloc[i, df.columns.get_loc('Low')] *= multiplier * 0.98
    
    def add_uptrend_pattern(self, df):
        """添加緩坡爬升模式"""
        # 在數據的中間部分添加穩定上升
        start_idx = int(len(df) * 0.3)
        end_idx = int(len(df) * 0.7)
        
        if end_idx > start_idx:
            for i in range(start_idx, end_idx):
                # 溫和上升
                multiplier = 1 + (i - start_idx) * 0.0008
                df.iloc[i, df.columns.get_loc('Close')] *= multiplier
                df.iloc[i, df.columns.get_loc('High')] *= multiplier
                df.iloc[i, df.columns.get_loc('Open')] *= multiplier
                df.iloc[i, df.columns.get_loc('Low')] *= multiplier * 0.99
    
    def fetch_data(self, symbol, period="6mo", interval="1d", use_demo_data=False):
        """主要的數據獲取方法，支援不同時間週期"""
        if use_demo_data:
            return self.generate_sample_data(symbol)

        data = None
        # 對於分鐘線數據，優先使用 yfinance
        if interval in ["1mo", "1wk"]:
            print("🌀 " + interval + " 優先使用 yfinance 獲取分鐘線數據...")
            data = self.fetch_data_yfinance(symbol, period, interval)

        # 如果不是分鐘線，或 yfinance 失敗，則走原有邏輯
        if data is None or data.empty:
            # 優先使用 Shioaji API (目前僅支援日線)
            #if interval == "1m":
            #    data = self.fetch_data_shioaji(symbol, period)
            
            # 如果 Shioaji 失敗或不適用，則嘗試 yfinance
            if data is None or data.empty:
                print(f"⚠️ Shioaji 數據獲取失敗或不適用，嘗試使用 yfinance 作為備援...")
                # 對於週線和月線，yfinance可以直接獲取
                yfinance_interval = interval if interval in ["1wk", "1mo"] else "1d"
                data = self.fetch_data_yfinance(symbol, period, yfinance_interval)
        
        # 如果所有真實數據源都失敗，則使用示範數據
        if data is None or data.empty:
            print(f"⚠️ 無法獲取 {symbol} 的真實數據，將使用示範數據")
            print("💡 提示：示範數據包含了理想的技術分析模式，用於展示系統功能")
            return self.generate_sample_data(symbol)
        
        return data

# 測試函數
def test_data_fetcher():
    """測試數據獲取器"""
    fetcher = StockDataFetcher()
    
    test_symbols = ['2330.TW', 'AAPL', '7703.TW']
    
    for symbol in test_symbols:
        print(f"\n{'='*50}")
        print(f"測試 {symbol}")
        print('='*50)
        
        data = fetcher.fetch_data(symbol, period="3mo")
        
        if data is not None and not data.empty:
            print(f"數據範圍: {data.index[0]} 至 {data.index[-1]}")
            print(f"最新價格: {data['Close'][-1]:.2f}")
            print(f"期間最高: {data['High'].max():.2f}")
            print(f"期間最低: {data['Low'].min():.2f}")
        else:
            print("❌ 數據獲取失敗")

if __name__ == "__main__":
    test_data_fetcher() 