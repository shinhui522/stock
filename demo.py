#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技術分析系統 - 示範腳本
展示系統的核心功能
"""

from stock_analyzer import StockAnalyzer
from stock_screener import StockScreener
import numpy as np

def demo_single_analysis():
    """示範個股分析功能"""
    print("=" * 60)
    print("🔍 示範功能：個股技術分析")
    print("=" * 60)
    
    # 分析台積電
    symbol = "2330.TW"
    print(f"正在分析 {symbol} (台積電)...")
    
    analyzer = StockAnalyzer()
    
    if analyzer.fetch_data(symbol, period="6mo"):
        # 生成交易信號
        signals = analyzer.generate_trading_signals()
        
        # 打印分析報告
        analyzer.print_analysis_report()
        
        # 分析結果摘要
        print(f"\n📊 分析結果摘要：")
        print(f"• 發現 {len(signals['crossovers'])} 個黃藍線交叉點")
        print(f"• 發現 {len(signals['uptrends'])} 個緩坡爬升趨勢")
        
        if signals['profit_analysis']:
            avg_profit = np.mean([p['profit_potential'] for p in signals['profit_analysis']])
            print(f"• 平均利潤空間：{avg_profit:.2f}%")
        
        # 生成圖表
        try:
            fig = analyzer.create_interactive_chart()
            if fig:
                filename = f"{symbol.replace('.', '_')}_demo.html"
                fig.write_html(filename)
                print(f"• 圖表已保存為：{filename}")
        except Exception as e:
            print(f"• 圖表生成失敗：{e}")
    else:
        print(f"❌ 無法獲取 {symbol} 的數據")

def demo_stock_screening():
    """示範股票篩選功能"""
    print("\n" + "=" * 60)
    print("🎯 示範功能：智能股票篩選")
    print("=" * 60)
    
    # 創建篩選器
    screener = StockScreener()
    
    # 使用預設台股清單
    print("正在載入台股熱門股票清單...")
    screener.load_stock_list()
    
    print(f"將篩選 {len(screener.stock_list)} 檔股票")
    print("篩選條件：評分 >= 50分")
    
    # 執行篩選
    results = screener.screen_stocks(min_score=50)
    
    # 顯示結果
    screener.print_screening_results()
    
    return results

def demo_comparison_analysis():
    """示範批量比較功能"""
    print("\n" + "=" * 60)
    print("📊 示範功能：股票批量比較")
    print("=" * 60)
    
    # 比較幾檔熱門台股
    stocks = ['2330.TW', '2454.TW', '2317.TW', '0050.TW']
    print(f"正在比較：{', '.join(stocks)}")
    
    comparison_data = []
    
    for symbol in stocks:
        print(f"分析 {symbol}...")
        analyzer = StockAnalyzer()
        
        if analyzer.fetch_data(symbol, period="3mo"):
            signals = analyzer.generate_trading_signals()
            current_price = analyzer.data['Close'][-1]
            first_price = analyzer.data['Close'][0]
            price_change_pct = ((current_price - first_price) / first_price) * 100
            
            comparison_data.append({
                'symbol': symbol,
                'current_price': current_price,
                'price_change_pct': price_change_pct,
                'crossovers': len(signals['crossovers']),
                'uptrends': len(signals['uptrends']),
                'avg_profit': np.mean([p['profit_potential'] for p in signals['profit_analysis']]) if signals['profit_analysis'] else 0
            })
    
    # 顯示比較結果
    print(f"\n📈 比較結果（近3個月）：")
    print("-" * 80)
    print(f"{'股票代碼':<12} {'當前價格':<10} {'漲跌幅%':<10} {'交叉點':<8} {'趨勢段':<8} {'利潤空間%':<10}")
    print("-" * 80)
    
    # 按漲跌幅排序
    comparison_data.sort(key=lambda x: x['price_change_pct'], reverse=True)
    
    for data in comparison_data:
        print(f"{data['symbol']:<12} {data['current_price']:<10.2f} {data['price_change_pct']:<10.2f} "
              f"{data['crossovers']:<8} {data['uptrends']:<8} {data['avg_profit']:<10.2f}")

def demo_pattern_detection():
    """示範模式識別功能"""
    print("\n" + "=" * 60)
    print("🔍 示範功能：交易模式識別")
    print("=" * 60)
    
    symbol = "2454.TW"  # 聯發科
    print(f"分析 {symbol} 的交易模式...")
    
    analyzer = StockAnalyzer()
    
    if analyzer.fetch_data(symbol, period="1y"):
        signals = analyzer.generate_trading_signals()
        
        print(f"\n🔄 黃藍線交叉模式：")
        if signals['crossovers']:
            buy_signals = [c for c in signals['crossovers'] if c['signal'] == 'BUY']
            sell_signals = [c for c in signals['crossovers'] if c['signal'] == 'SELL']
            
            print(f"• 買入信號（黃金交叉）：{len(buy_signals)} 次")
            print(f"• 賣出信號（死亡交叉）：{len(sell_signals)} 次")
            
            if buy_signals:
                print(f"• 最近買入信號：{buy_signals[-1]['date'].strftime('%Y-%m-%d')} @ {buy_signals[-1]['price']:.2f}")
        
        print(f"\n📈 緩坡爬升模式：")
        if signals['uptrends']:
            total_days = sum(t['duration_days'] for t in signals['uptrends'])
            avg_duration = total_days / len(signals['uptrends'])
            
            print(f"• 發現 {len(signals['uptrends'])} 個上升趨勢段")
            print(f"• 平均持續時間：{avg_duration:.1f} 天")
            
            # 顯示最長的趨勢段
            longest_trend = max(signals['uptrends'], key=lambda x: x['duration_days'])
            gain = ((longest_trend['end_price'] - longest_trend['start_price']) / longest_trend['start_price']) * 100
            print(f"• 最長趨勢段：{longest_trend['duration_days']} 天，漲幅 {gain:.2f}%")
        
        print(f"\n💰 利潤空間分析：")
        if signals['profit_analysis']:
            profits = [p['profit_potential'] for p in signals['profit_analysis']]
            print(f"• 平均利潤空間：{np.mean(profits):.2f}%")
            print(f"• 最大利潤空間：{max(profits):.2f}%")
            print(f"• 最小利潤空間：{min(profits):.2f}%")
            
            # 勝率計算
            profitable_trades = len([p for p in profits if p > 0])
            win_rate = (profitable_trades / len(profits)) * 100
            print(f"• 歷史勝率：{win_rate:.1f}%")

def main():
    """主示範函數"""
    print("🎉 歡迎使用股票技術分析系統示範！")
    print("本示範將展示系統的核心功能...")
    
    try:
        # 1. 個股分析示範
        demo_single_analysis()
        
        # 2. 股票篩選示範
        screening_results = demo_stock_screening()
        
        # 3. 批量比較示範
        demo_comparison_analysis()
        
        # 4. 模式識別示範
        demo_pattern_detection()
        
        print("\n" + "=" * 60)
        print("🎊 示範完成！")
        print("=" * 60)
        print("💡 使用建議：")
        print("1. 執行 'python main.py -i' 進入互動模式")
        print("2. 執行 'streamlit run streamlit_app.py' 啟動網頁界面")
        print("3. 查看生成的 HTML 圖表文件")
        
        if screening_results:
            print(f"4. 篩選到 {len(screening_results)} 檔優質股票，建議進一步分析")
        
        print("\n⚠️  免責聲明：本系統僅供學習和研究使用，不構成投資建議")
        
    except KeyboardInterrupt:
        print("\n\n示範被用戶中斷")
    except Exception as e:
        print(f"\n❌ 示範過程中發生錯誤：{e}")
        print("請檢查網路連接和依賴套件是否正確安裝")

if __name__ == "__main__":
    main() 