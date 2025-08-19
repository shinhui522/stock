import pandas as pd
import numpy as np
from stock_analyzer import StockAnalyzer
import concurrent.futures
import time

class StockScreener:
    def __init__(self):
        self.stock_list = []
        self.results = []
        
    def load_stock_list(self, stocks=None):
        """載入股票清單"""
        if stocks is None:
            # 台股熱門股票代碼（範例）
            self.stock_list = [
                '2330.TW',  # 台積電
                '2454.TW',  # 聯發科
                '2317.TW',  # 鴻海
                '2382.TW',  # 廣達
                '3711.TW',  # 日月光投控
                '2408.TW',  # 南亞科
                '2881.TW',  # 富邦金
                '2882.TW',  # 國泰金
                '2412.TW',  # 中華電
                '1301.TW',  # 台塑
                '1303.TW',  # 南亞
                '2207.TW',  # 和泰車
                '2303.TW',  # 聯電
                '3008.TW',  # 大立光
                '6505.TW',  # 台塑化
            ]
        else:
            self.stock_list = stocks
            
    def analyze_single_stock(self, symbol):
        """分析單一股票"""
        try:
            analyzer = StockAnalyzer()
            if analyzer.fetch_data(symbol, period="6mo"):  # 6個月數據
                signals = analyzer.generate_trading_signals()
                
                # 評估股票品質
                score = self.calculate_stock_score(analyzer, signals)
                
                return {
                    'symbol': symbol,
                    'current_price': analyzer.data['Close'][-1],
                    'signals': signals,
                    'score': score,
                    'analyzer': analyzer
                }
        except Exception as e:
            print(f"分析 {symbol} 時發生錯誤: {e}")
            return None
    
    def calculate_stock_score(self, analyzer, signals):
        """計算股票評分（0-100分）"""
        score = 0
        
        # 1. 緩坡爬升趨勢評分（30分）
        if signals['uptrends']:
            recent_trends = [t for t in signals['uptrends'] 
                           if (analyzer.data.index[-1] - t['end_date']).days <= 30]
            if recent_trends:
                avg_slope = np.mean([t['avg_slope'] for t in recent_trends])
                score += min(30, avg_slope * 15)  # 斜率越大分數越高
        
        # 2. 黃金交叉評分（25分）
        if signals['crossovers']:
            recent_crosses = [c for c in signals['crossovers'] 
                            if c['signal'] == 'BUY' and 
                            (analyzer.data.index[-1] - c['date']).days <= 20]
            if recent_crosses:
                score += 25
        
        # 3. 利潤空間評分（25分）
        if signals['profit_analysis']:
            avg_profit = np.mean([p['profit_potential'] for p in signals['profit_analysis']])
            score += min(25, avg_profit / 2)  # 利潤空間越大分數越高
        
        # 4. 技術指標評分（20分）
        current_data = analyzer.data.iloc[-1]
        
        # 價格在均線之上
        if current_data['Close'] > current_data['Yellow_Line']:
            score += 5
        if current_data['Close'] > current_data['Blue_Line']:
            score += 5
        if current_data['Close'] > current_data['MA60']:
            score += 5
            
        # 均線排列
        if (current_data['Yellow_Line'] > current_data['Blue_Line'] > current_data['MA60']):
            score += 5
        
        return min(100, score)
    
    def screen_stocks(self, min_score=60, max_workers=5):
        """篩選股票"""
        print(f"開始篩選 {len(self.stock_list)} 檔股票...")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任務
            future_to_symbol = {
                executor.submit(self.analyze_single_stock, symbol): symbol 
                for symbol in self.stock_list
            }
            
            # 收集結果
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    if result and result['score'] >= min_score:
                        results.append(result)
                        print(f"✓ {symbol}: 評分 {result['score']:.1f}")
                    else:
                        print(f"✗ {symbol}: 評分過低或分析失敗")
                except Exception as e:
                    print(f"✗ {symbol}: 處理錯誤 - {e}")
        
        # 按評分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        self.results = results
        
        return results
    
    def print_screening_results(self):
        """打印篩選結果"""
        if not self.results:
            print("沒有符合條件的股票")
            return
            
        print(f"\n=== 股票篩選結果 (共 {len(self.results)} 檔) ===")
        print(f"{'排名':<4} {'代碼':<12} {'當前價格':<10} {'評分':<8} {'特徵描述'}")
        print("-" * 70)
        
        for i, result in enumerate(self.results, 1):
            symbol = result['symbol']
            price = result['current_price']
            score = result['score']
            
            # 生成特徵描述
            features = []
            if result['signals']['crossovers']:
                recent_crosses = [c for c in result['signals']['crossovers'] 
                                if (pd.Timestamp.now() - c['date']).days <= 30]
                if recent_crosses:
                    features.append("近期黃金交叉")
            
            if result['signals']['uptrends']:
                features.append("緩坡上升")
                
            if result['signals']['profit_analysis']:
                avg_profit = np.mean([p['profit_potential'] 
                                    for p in result['signals']['profit_analysis']])
                if avg_profit > 10:
                    features.append(f"高利潤空間({avg_profit:.1f}%)")
            
            feature_str = ", ".join(features) if features else "基本面良好"
            
            print(f"{i:<4} {symbol:<12} {price:<10.2f} {score:<8.1f} {feature_str}")
    
    def get_detailed_analysis(self, rank=1):
        """獲取指定排名股票的詳細分析"""
        if not self.results or rank > len(self.results):
            print("無效的排名或沒有結果")
            return None
            
        result = self.results[rank - 1]
        analyzer = result['analyzer']
        
        print(f"\n=== {result['symbol']} 詳細分析 ===")
        analyzer.print_analysis_report()
        
        return analyzer
    
    def create_comparison_chart(self, top_n=5):
        """創建前N名股票的比較圖表"""
        if not self.results:
            print("沒有結果可以比較")
            return None
            
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # 取前N名
        top_stocks = self.results[:min(top_n, len(self.results))]
        
        fig = make_subplots(
            rows=len(top_stocks), cols=1,
            subplot_titles=[f"{stock['symbol']} (評分: {stock['score']:.1f})" 
                          for stock in top_stocks],
            vertical_spacing=0.05
        )
        
        for i, stock in enumerate(top_stocks, 1):
            analyzer = stock['analyzer']
            data = analyzer.data
            
            # 格式化日期為只顯示日期部分
            formatted_dates = [date.strftime('%Y-%m-%d') for date in data.index]
            
            # 添加價格線
            fig.add_trace(go.Scatter(
                x=formatted_dates,
                y=data['Close'],
                mode='lines',
                name=f"{stock['symbol']} 收盤價",
                line=dict(width=2)
            ), row=i, col=1)
            
            # 添加黃藍線
            fig.add_trace(go.Scatter(
                x=formatted_dates,
                y=data['Yellow_Line'],
                mode='lines',
                name='黃線',
                line=dict(color='yellow', width=1),
                showlegend=(i==1)
            ), row=i, col=1)
            
            fig.add_trace(go.Scatter(
                x=formatted_dates,
                y=data['Blue_Line'],
                mode='lines',
                name='藍線',
                line=dict(color='blue', width=1),
                showlegend=(i==1)
            ), row=i, col=1)
        
        fig.update_layout(
            title="熱門股票技術分析比較",
            height=300 * len(top_stocks),
            showlegend=True
        )
        
        return fig

# 使用範例
if __name__ == "__main__":
    screener = StockScreener()
    screener.load_stock_list()
    
    # 篩選股票
    results = screener.screen_stocks(min_score=50)
    screener.print_screening_results()
    
    # 查看第一名的詳細分析
    if results:
        screener.get_detailed_analysis(rank=1) 