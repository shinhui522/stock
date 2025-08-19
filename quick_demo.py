#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技術分析系統 - 快速示範
使用示範數據展示系統功能
"""

from stock_analyzer import StockAnalyzer
import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端

def quick_demo():
    """快速示範系統功能"""
    print("🎯 股票技術分析系統 - 快速示範")
    print("=" * 60)
    
    # 測試股票（包括您圖片中的銳澤7703）
    test_symbols = [
        ('2330.TW', '台積電'),
        ('7703.TW', '銳澤'),  # 您圖片中的股票
        ('2454.TW', '聯發科')
    ]
    
    for symbol, name in test_symbols:
        print(f"\n📊 分析 {symbol} ({name})")
        print("-" * 40)
        
        # 創建分析器
        analyzer = StockAnalyzer()
        
        # 使用示範數據（因為網路問題）
        if analyzer.fetch_data(symbol, period="6mo", use_demo_data=True):
            
            # 生成交易信號
            signals = analyzer.generate_trading_signals()
            
            # 顯示分析結果
            current_price = analyzer.data['Close'][-1]
            print(f"當前價格: {current_price:.2f}")
            
            # 黃藍線交叉分析
            crossovers = signals['crossovers']
            buy_signals = [c for c in crossovers if c['signal'] == 'BUY']
            sell_signals = [c for c in crossovers if c['signal'] == 'SELL']
            
            print(f"🔄 交叉點分析:")
            print(f"  • 買入信號 (黃金交叉): {len(buy_signals)} 次")
            print(f"  • 賣出信號 (死亡交叉): {len(sell_signals)} 次")
            
            if buy_signals:
                latest_buy = buy_signals[-1]
                print(f"  • 最近買入信號: {latest_buy['date'].strftime('%Y-%m-%d')} @ {latest_buy['price']:.2f}")
            
            # 緩坡爬升分析
            uptrends = signals['uptrends']
            print(f"📈 緩坡爬升分析:")
            print(f"  • 發現 {len(uptrends)} 個上升趨勢段")
            
            if uptrends:
                longest_trend = max(uptrends, key=lambda x: x['duration_days'])
                gain = ((longest_trend['end_price'] - longest_trend['start_price']) / longest_trend['start_price']) * 100
                print(f"  • 最長趨勢: {longest_trend['duration_days']} 天，漲幅 {gain:.2f}%")
            
            # 利潤空間分析
            profit_analysis = signals['profit_analysis']
            print(f"💰 利潤空間分析:")
            
            if profit_analysis:
                profits = [p['profit_potential'] for p in profit_analysis]
                avg_profit = sum(profits) / len(profits)
                max_profit = max(profits)
                print(f"  • 平均利潤空間: {avg_profit:.2f}%")
                print(f"  • 最大利潤空間: {max_profit:.2f}%")
                print(f"  • 交易機會數量: {len(profit_analysis)} 次")
                
                # 勝率計算
                profitable_trades = len([p for p in profits if p > 0])
                win_rate = (profitable_trades / len(profits)) * 100
                print(f"  • 歷史勝率: {win_rate:.1f}%")
            else:
                print("  • 暫無利潤空間數據")
            
            # 交易建議
            print(f"💡 交易建議:")
            recent_crossovers = [c for c in crossovers 
                               if (analyzer.data.index[-1] - c['date']).days <= 10]
            
            if recent_crossovers:
                latest_signal = recent_crossovers[-1]
                if latest_signal['signal'] == 'BUY':
                    print(f"  ✅ 近期出現買入信號，建議關注")
                else:
                    print(f"  ⚠️ 近期出現賣出信號，建議謹慎")
            else:
                print(f"  📊 目前無明確信號，建議持續觀察")
            
            # 生成圖表
            try:
                fig = analyzer.create_interactive_chart()
                if fig:
                    filename = f"{symbol.replace('.', '_')}_analysis.html"
                    fig.write_html(filename)
                    print(f"  📈 技術分析圖表已保存: {filename}")
            except Exception as e:
                print(f"  ⚠️ 圖表生成失敗: {e}")
        
        else:
            print(f"❌ 無法分析 {symbol}")

def show_system_features():
    """展示系統特色"""
    print("\n" + "=" * 60)
    print("🎯 系統特色說明")
    print("=" * 60)
    
    features = [
        ("緩坡爬升識別", "檢測穩定的上升趨勢，過濾過於陡峭的走勢"),
        ("黃藍線交叉", "5日線與20日線的交叉點，識別買賣時機"),
        ("利潤空間評估", "計算天花板與進場點距離，評估獲利潛力"),
        ("智能評分系統", "綜合多項指標，自動評分股票品質"),
        ("視覺化圖表", "生成互動式技術分析圖表"),
        ("批量篩選", "同時分析多檔股票，找出優質標的")
    ]
    
    for i, (feature, description) in enumerate(features, 1):
        print(f"{i}. {feature}")
        print(f"   {description}")
        print()

def main():
    """主函數"""
    try:
        # 執行快速示範
        quick_demo()
        
        # 展示系統特色
        show_system_features()
        
        print("=" * 60)
        print("🎉 快速示範完成！")
        print("=" * 60)
        print("💡 接下來您可以：")
        print("1. 查看生成的 HTML 圖表文件")
        print("2. 執行 'python main.py -i' 進入互動模式")
        print("3. 執行 'streamlit run streamlit_app.py' 啟動網頁界面")
        print()
        print("⚠️ 注意：")
        print("• 目前使用示範數據（因網路連接問題）")
        print("• 示範數據包含理想的技術分析模式")
        print("• 真實交易請等待網路問題解決後使用實際數據")
        
    except KeyboardInterrupt:
        print("\n示範被用戶中斷")
    except Exception as e:
        print(f"\n❌ 示範過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 