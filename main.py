#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技術分析系統 - 主程式
功能：
1. 緩坡爬升趨勢識別
2. 黃藍線交叉點檢測
3. 利潤空間分析
4. 股票篩選和比較
"""

from stock_analyzer import StockAnalyzer
from stock_screener import StockScreener
import argparse
import sys

def analyze_single_stock(symbol, period="6mo"):
    """分析單一股票"""
    print(f"\n=== 開始分析 {symbol} ===")
    
    analyzer = StockAnalyzer()
    
    if not analyzer.fetch_data(symbol, period=period):
        print(f"錯誤：無法獲取 {symbol} 的數據")
        return None
    
    # 打印分析報告
    analyzer.print_analysis_report()
    
    # 生成圖表（可選）
    try:
        fig = analyzer.create_interactive_chart()
        if fig:
            # 保存為HTML文件
            filename = f"{symbol.replace('.', '_')}_analysis.html"
            fig.write_html(filename)
            print(f"\n圖表已保存為: {filename}")
    except Exception as e:
        print(f"圖表生成失敗: {e}")
    
    return analyzer

def screen_stocks(min_score=60, custom_stocks=None):
    """篩選股票"""
    print("\n=== 開始股票篩選 ===")
    
    screener = StockScreener()
    screener.load_stock_list(custom_stocks)
    
    results = screener.screen_stocks(min_score=min_score)
    screener.print_screening_results()
    
    if results:
        print(f"\n是否查看第一名股票的詳細分析？(y/n): ", end="")
        choice = input().lower()
        if choice == 'y':
            screener.get_detailed_analysis(rank=1)
    
    return results

def interactive_mode():
    """互動模式"""
    print("=== 股票技術分析系統 ===")
    print("歡迎使用！請選擇功能：")
    
    while True:
        print("\n功能選單：")
        print("1. 個股分析")
        print("2. 股票篩選")
        print("3. 啟動網頁界面")
        print("4. 退出")
        
        choice = input("\n請選擇功能 (1-4): ").strip()
        
        if choice == '1':
            symbol = input("請輸入股票代碼 (例: 2330.TW): ").strip().upper()
            if symbol:
                period = input("分析期間 (1d/1mo/3mo/6mo/1y/2y，預設6mo): ").strip() or "6mo"
                analyze_single_stock(symbol, period)
            else:
                print("股票代碼不能為空")
                
        elif choice == '2':
            try:
                min_score = input("最低評分 (0-100，預設60): ").strip()
                min_score = int(min_score) if min_score else 60
                
                print("是否使用自定義股票清單？(y/n): ", end="")
                use_custom = input().lower() == 'y'
                
                custom_stocks = None
                if use_custom:
                    print("請輸入股票代碼（用空格分隔）: ", end="")
                    stocks_input = input().strip()
                    if stocks_input:
                        custom_stocks = stocks_input.split()
                
                screen_stocks(min_score, custom_stocks)
                
            except ValueError:
                print("評分必須是數字")
                
        elif choice == '3':
            print("正在啟動網頁界面...")
            import subprocess
            try:
                subprocess.run(["streamlit", "run", "streamlit_app.py"], check=True)
            except subprocess.CalledProcessError:
                print("啟動失敗，請確保已安裝 streamlit")
            except FileNotFoundError:
                print("找不到 streamlit 命令，請先安裝：pip install streamlit")
                
        elif choice == '4':
            print("謝謝使用！")
            break
            
        else:
            print("無效選擇，請重新輸入")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='股票技術分析系統')
    parser.add_argument('--symbol', '-s', help='股票代碼 (例: 2330.TW)')
    parser.add_argument('--period', '-p', default='6mo', 
                       help='分析期間 (1d/1mo/3mo/6mo/1y/2y)')
    parser.add_argument('--screen', action='store_true', 
                       help='執行股票篩選')
    parser.add_argument('--min-score', type=int, default=60, 
                       help='篩選最低評分 (0-100)')
    parser.add_argument('--stocks', nargs='+', 
                       help='自定義股票清單')
    parser.add_argument('--web', action='store_true', 
                       help='啟動網頁界面')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='互動模式')
    
    args = parser.parse_args()
    
    try:
        if args.web:
            print("正在啟動網頁界面...")
            import subprocess
            subprocess.run(["streamlit", "run", "streamlit_app.py"])
            
        elif args.interactive:
            interactive_mode()
            
        elif args.symbol:
            analyze_single_stock(args.symbol, args.period)
            
        elif args.screen:
            screen_stocks(args.min_score, args.stocks)
            
        else:
            # 預設進入互動模式
            interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n程式被用戶中斷")
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 