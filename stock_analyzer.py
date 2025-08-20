import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from datetime import datetime, timedelta
from stock_data_fetcher import StockDataFetcher
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self):
        self.data = None
        self.symbol = None
        self.data_fetcher = StockDataFetcher()
        
    def fetch_data(self, symbol, period="1y", interval="1d", use_demo_data=False):
        """獲取並處理股票數據，支援不同時間週期"""
        try:
            self.symbol = symbol
            # 從 data_fetcher 獲取原始數據
            raw_data = self.data_fetcher.fetch_data(symbol, period, interval, use_demo_data)
            
            if raw_data is None or raw_data.empty:
                print(f"❌ 無法獲取 {symbol} 的數據")
                self.data = None
                return False

            self.data = raw_data
            
            # --- 數據重採樣邏輯 ---
            # 檢查數據的時間間隔，以判斷是否為日內數據
            if len(self.data.index) > 1:
                # 使用 .to_series() 處理可能的 DatetimeIndex 轉換問題，並獲取最小時間差
                time_delta = self.data.index.to_series().diff().min()
                is_intraday = time_delta < timedelta(days=1)
            else:
                is_intraday = False

            # 如果獲取的是日內數據，但請求的是日/周/月線，則進行重採樣
            if is_intraday and interval in ['1d', '1wk', '1mo']:
                self.resample_data(interval)
            # 如果請求的是週線或月線，但獲取的是日線數據，也進行重採樣
            elif not is_intraday and interval in ['1wk', '1mo']:
                self.resample_data(interval)

            if self.data is None or self.data.empty:
                print(f"❌ 處理後 {symbol} 數據為空")
                return False
            
            print(f"✅ 數據載入成功: {len(self.data)} 筆記錄")
            return True
            
        except Exception as e:
            print(f"數據獲取錯誤: {e}")
            return False

    def analyze(self):
        """對已獲取的數據執行所有技術分析計算，並在最後裁剪到用戶請求的日期範圍"""
        if self.data is None:
            print("⚠️ 沒有數據可供分析，請先 fetch_data")
            return False
        
        print("🔬 開始執行技術分析 (使用擴展數據)...")
        self.calculate_moving_averages()
        self.calculate_support_resistance()
        self.detect_trend_slope()
        print("✅ 技術分析計算完成")

        # 裁剪數據到原始請求的範圍
        if hasattr(self.data_fetcher, 'original_start_date'):
            print(f"🔪 正在將數據裁剪回 {self.data_fetcher.original_start_date.strftime('%Y-%m-%d')} 之後...")
            original_start_date_aware = pd.to_datetime(self.data_fetcher.original_start_date).tz_localize(self.data.index.tz)
            self.data = self.data[self.data.index >= original_start_date_aware]
            print(f"✅ 數據裁剪完成，剩下 {len(self.data)} 筆記錄用於顯示")
        
        return True
    
    def resample_data(self, interval):
        """將數據重採樣為指定的K線週期 (日/週/月)"""
        if self.data is None or self.data.empty:
            return

        print(f"🔄 正在將數據重採樣為 {interval} 週期...")
        
        # 定義重採樣規則
        rule_map = {
            '1d': 'D',
            '1wk': 'W',
            '1mo': 'M'
        }
        rule = rule_map.get(interval)
        if not rule:
            print(f"⚠️ 不支援的重採樣週期: {interval}")
            return

        # 定義OHLCV的聚合方式
        ohlc_dict = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }
        
        try:
            resampled_data = self.data.resample(rule).apply(ohlc_dict)
            # 移除沒有交易的行
            self.data = resampled_data.dropna()
            print(f"✅ 重採樣完成，剩下 {len(self.data)} 筆記錄")
        except Exception as e:
            print(f"❌ 重採樣失敗: {e}")

    def calculate_moving_averages(self):
        """計算移動平均線（優化為EMA）"""
        if self.data is None:
            return None
            
        # 計算不同週期的指數移動平均線 (EMA)，反應更靈敏
        self.data['MA5'] = ta.trend.ema_indicator(self.data['Close'], window=5)
        self.data['MA20'] = ta.trend.ema_indicator(self.data['Close'], window=20)
        self.data['MA60'] = ta.trend.ema_indicator(self.data['Close'], window=60)
        
        # 黃線（短期）和藍線（長期）
        self.data['Yellow_Line'] = self.data['MA5']  # 黃線 - 5日EMA
        self.data['Blue_Line'] = self.data['MA20']   # 藍線 - 20日EMA
        
        return self.data
    
    def calculate_support_resistance(self, window=20):
        """計算支撐和阻力線"""
        if self.data is None:
            return None
            
        # 計算支撐線（低點的移動平均）
        self.data['Support'] = self.data['Low'].rolling(window=window).min()
        
        # 計算阻力線（高點的移動平均）
        self.data['Resistance'] = self.data['High'].rolling(window=window).max()
        
        return self.data
    
    def detect_trend_slope(self, period=20):
        """檢測趨勢斜率（緩坡爬升）"""
        if self.data is None:
            return None
            
        # 計算價格變化率
        self.data['Price_Change'] = self.data['Close'].pct_change()
        
        # 定義一個輔助函數來計算斜率
        def calculate_slope(y):
            # 移除 NaN 值以進行計算
            y = y.dropna()
            if len(y) < 2:  # 需要至少兩個點才能計算斜率
                return np.nan
            x = np.arange(len(y))
            try:
                # 使用 np.polyfit 計算線性回歸的斜率
                slope = np.polyfit(x, y, 1)[0]
                return slope
            except (np.linalg.LinAlgError, TypeError):
                # 如果計算失敗，返回 NaN
                return np.nan

        # 使用 rolling().apply() 計算移動窗口的趨勢斜率
        # raw=False 確保傳遞給 apply 的是 Pandas Series，可以處理 NaN
        self.data['Trend_Slope'] = self.data['Close'].rolling(
            window=period,
            min_periods=2  # 至少需要兩個點才能計算斜率
        ).apply(calculate_slope, raw=False)
        
        return self.data
    
    def find_crossover_points(self):
        """找到黃藍線交叉點"""
        if self.data is None or 'Yellow_Line' not in self.data.columns:
            return None
            
        crossovers = []
        
        for i in range(1, len(self.data)):
            # 黃金交叉（黃線上穿藍線）
            if (self.data['Yellow_Line'].iloc[i] > self.data['Blue_Line'].iloc[i] and 
                self.data['Yellow_Line'].iloc[i-1] <= self.data['Blue_Line'].iloc[i-1]):
                crossovers.append({
                    'date': self.data.index[i],
                    'price': self.data['Close'].iloc[i],
                    'type': '黃金交叉',
                    'signal': 'BUY'
                })
            
            # 死亡交叉（黃線下穿藍線）
            elif (self.data['Yellow_Line'].iloc[i] < self.data['Blue_Line'].iloc[i] and 
                  self.data['Yellow_Line'].iloc[i-1] >= self.data['Blue_Line'].iloc[i-1]):
                crossovers.append({
                    'date': self.data.index[i],
                    'price': self.data['Close'].iloc[i],
                    'type': '死亡交叉',
                    'signal': 'SELL'
                })
        
        return crossovers
    
    def calculate_profit_potential(self, crossover_points):
        """計算利潤空間（天花板與交叉點距離）"""
        if not crossover_points:
            return []
            
        profit_analysis = []
        
        for cross in crossover_points:
            if cross['signal'] == 'BUY':
                cross_date = cross['date']
                cross_price = cross['price']
                
                # 找到交叉點後的最高價（天花板）
                future_data = self.data[self.data.index > cross_date]
                if not future_data.empty:
                    max_price = future_data['High'].max()
                    max_date = future_data['High'].idxmax()
                    
                    # 計算利潤空間
                    profit_space = ((max_price - cross_price) / cross_price) * 100
                    
                    profit_analysis.append({
                        'crossover_date': cross_date,
                        'crossover_price': cross_price,
                        'ceiling_date': max_date,
                        'ceiling_price': max_price,
                        'profit_potential': profit_space,
                        'distance_days': (max_date - cross_date).days
                    })
        
        return profit_analysis
    
    def identify_gentle_uptrend(self, min_slope=0.1, max_slope=2.0, min_days=10):
        """識別緩坡爬升模式"""
        if self.data is None or 'Trend_Slope' not in self.data.columns:
            return []
            
        uptrend_periods = []
        current_start = None
        
        for i, slope in enumerate(self.data['Trend_Slope']):
            if pd.notna(slope) and min_slope <= slope <= max_slope:
                if current_start is None:
                    current_start = i
            else:
                if current_start is not None:
                    period_length = i - current_start
                    if period_length >= min_days:
                        uptrend_periods.append({
                            'start_date': self.data.index[current_start],
                            'end_date': self.data.index[i-1],
                            'duration_days': period_length,
                            'avg_slope': self.data['Trend_Slope'].iloc[current_start:i].mean(),
                            'start_price': self.data['Close'].iloc[current_start],
                            'end_price': self.data['Close'].iloc[i-1]
                        })
                    current_start = None
        
        return uptrend_periods
    
    def generate_trading_signals(self):
        """生成交易信號（假設 analyze 已被調用）"""
        if self.data is None:
            return None
            
        # 找到交叉點和趨勢
        crossovers = self.find_crossover_points()
        uptrends = self.identify_gentle_uptrend()
        profit_potential = self.calculate_profit_potential(crossovers)
        
        return {
            'crossovers': crossovers,
            'uptrends': uptrends,
            'profit_analysis': profit_potential
        }
    
    def create_interactive_chart(self):
        """創建互動式圖表（假設 analyze 已被調用）"""
        if self.data is None:
            return None
            
        # 格式化日期為只顯示日期部分
        formatted_dates = [date.strftime('%Y-%m-%d') for date in self.data.index]
        
        # 創建子圖
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f'{self.symbol} 股價走勢圖', '成交量'),
            vertical_spacing=0.4,
            row_heights=[0.7, 0.3]
        )
        
        # K線圖
        fig.add_trace(go.Candlestick(
            x=formatted_dates,
            open=self.data['Open'],
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            name='K線',
            increasing_line_color='red',
            decreasing_line_color='green'
        ), row=1, col=1)
        
        # 移動平均線
        fig.add_trace(go.Scatter(
            x=formatted_dates,
            y=self.data['Yellow_Line'],
            mode='lines',
            name='黃線(EMA5)',
            line=dict(color='yellow', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=formatted_dates,
            y=self.data['Blue_Line'],
            mode='lines',
            name='藍線(EMA20)',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=formatted_dates,
            y=self.data['MA60'],
            mode='lines',
            name='EMA60',
            line=dict(color='purple', width=1)
        ), row=1, col=1)
        
        # 支撐阻力線
        fig.add_trace(go.Scatter(
            x=formatted_dates,
            y=self.data['Support'],
            mode='lines',
            name='支撐線',
            line=dict(color='green', width=1, dash='dash')
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=formatted_dates,
            y=self.data['Resistance'],
            mode='lines',
            name='阻力線',
            line=dict(color='red', width=1, dash='dash')
        ), row=1, col=1)
        
        # 成交量
        colors = ['red' if close > open else 'green'
                 for close, open in zip(self.data['Close'], self.data['Open'])]
        
        fig.add_trace(go.Bar(
            x=formatted_dates,
            y=self.data['Volume'],
            name='成交量',
            marker_color=colors
        ), row=2, col=1)
        
        # 標記交叉點
        crossovers = self.find_crossover_points()
        if crossovers:
            buy_dates = [c['date'].strftime('%Y-%m-%d') for c in crossovers if c['signal'] == 'BUY']
            buy_prices = [c['price'] for c in crossovers if c['signal'] == 'BUY']
            sell_dates = [c['date'].strftime('%Y-%m-%d') for c in crossovers if c['signal'] == 'SELL']
            sell_prices = [c['price'] for c in crossovers if c['signal'] == 'SELL']
            
            if buy_dates:
                fig.add_trace(go.Scatter(
                    x=buy_dates,
                    y=buy_prices,
                    mode='markers',
                    name='買入信號',
                    marker=dict(symbol='triangle-up', size=15, color='lime')
                ), row=1, col=1)
            
            if sell_dates:
                fig.add_trace(go.Scatter(
                    x=sell_dates,
                    y=sell_prices,
                    mode='markers',
                    name='賣出信號',
                    marker=dict(symbol='triangle-down', size=15, color='red')
                ), row=1, col=1)
        
        # 更新佈局
        fig.update_layout(
            title=f'{self.symbol} 技術分析圖表',
            xaxis_title='日期',
            yaxis_title='價格',
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            xaxis=dict(
                type='category',
                rangeslider=dict(
                    visible=False
                )
            )
        )
        
        return fig
    
    def print_analysis_report(self):
        """打印分析報告"""
        if self.data is None:
            print("請先獲取股票數據")
            return
            
        signals = self.generate_trading_signals()
        
        print(f"\n=== {self.symbol} 技術分析報告 ===")
        print(f"分析期間: {self.data.index[0].strftime('%Y-%m-%d')} 至 {self.data.index[-1].strftime('%Y-%m-%d')}")
        print(f"當前價格: {self.data['Close'][-1]:.2f}")
        
        print(f"\n【黃藍線交叉點分析】")
        if signals['crossovers']:
            for i, cross in enumerate(signals['crossovers'][-5:], 1):  # 顯示最近5個交叉點
                print(f"{i}. {cross['date'].strftime('%Y-%m-%d')} - {cross['type']} - 價格: {cross['price']:.2f}")
        else:
            print("未發現明顯的交叉點")
            
        print(f"\n【緩坡爬升趨勢】")
        if signals['uptrends']:
            for i, trend in enumerate(signals['uptrends'][-3:], 1):  # 顯示最近3個趨勢
                gain = ((trend['end_price'] - trend['start_price']) / trend['start_price']) * 100
                print(f"{i}. {trend['start_date'].strftime('%Y-%m-%d')} 至 {trend['end_date'].strftime('%Y-%m-%d')}")
                print(f"   持續天數: {trend['duration_days']}天, 漲幅: {gain:.2f}%")
        else:
            print("未發現明顯的緩坡爬升趨勢")
            
        print(f"\n【利潤空間分析】")
        if signals['profit_analysis']:
            for i, profit in enumerate(signals['profit_analysis'][-3:], 1):  # 顯示最近3個分析
                print(f"{i}. 交叉日期: {profit['crossover_date'].strftime('%Y-%m-%d')}")
                print(f"   交叉價格: {profit['crossover_price']:.2f}")
                print(f"   天花板價格: {profit['ceiling_price']:.2f}")
                print(f"   利潤空間: {profit['profit_potential']:.2f}%")
                print(f"   到達天花板天數: {profit['distance_days']}天")
        else:
            print("暫無利潤空間數據") 